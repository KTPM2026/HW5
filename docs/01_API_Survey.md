# 01 – Khảo sát API (Người 5 – Workflow 5)

**Workflow 5:** Login → View Order History → Browse Products → Add to Cart → Checkout
**Mục tiêu:** Truy xuất lịch sử đơn hàng và tạo đơn mới.
**SUT:** EShop backend — `eshop-sut/backend/server.js` (Express 5 + sqlite3, 1 kết nối SQLite, port 3000)
**Nguồn khảo sát:** `api_specification.md`, `README.md` (SRS) và đọc trực tiếp mã nguồn `server.js`, `database.js`, `frontend-web/src/pages/*.jsx`.

## Ánh xạ nhóm endpoint theo đề bài

| Nhóm (đề HW05) | Bước workflow | Endpoint |
|---|---|---|
| Auth-heavy | Login | `POST /api/login` |
| Read-heavy | View Order History | `GET /api/orders/my-orders` |
| Read-heavy | Browse Products | `GET /api/products`, `GET /api/products?search=`, `GET /api/products/:id` |
| Transactional | Add to Cart | `POST /api/cart`, `GET /api/cart` |
| Transactional | Checkout | `POST /api/checkout` |

---

## 1. API Đăng nhập – `POST /api/login`

| Mục | Chi tiết |
|---|---|
| Auth | Không |
| Request | `{"email": "...", "password": "..."}` (Content-Type: application/json) |
| 200 | `{"message":"Login successful","token":"<JWT>","user":{...}}` |
| 401 | `{"error":"Invalid email or password"}` (sai email hoặc sai mật khẩu) |
| 403 | `{"error":"Tài khoản đã bị khóa. Vui lòng thử lại sau."}` (đang bị khóa) |
| DB | 1× `SELECT * FROM users WHERE email=?` (**không có index trên `email`**) + 1× `UPDATE users` (ghi!) mỗi lần login |
| Token | JWT HS256, payload `{id, role}`, **không có `exp`** → token dùng được mãi |

**Hành vi khóa tài khoản (quan trọng cho Stress/Spike):**

| | Đặc tả SRS FR-02 | Code thực tế |
|---|---|---|
| Tăng bộ đếm mỗi lần sai | +1 | **+2** (`login_attempts + 2`) |
| Ngưỡng khóa | ≥ 3 lần sai | ≥ 3 → thực tế **khóa ngay ở lần sai thứ 2** |
| Thời gian khóa | 30 giây | **180 giây** |
| Login đúng khi đang khóa | — | 403, kể cả đúng mật khẩu |

→ Hệ quả cho kiểm thử hiệu năng: chỉ cần 2 request sai (ví dụ dữ liệu CSV lỗi) là account bị khóa 3 phút và mọi VU dùng account đó đều nhận 403. Vì vậy test plan **chỉ dùng credential hợp lệ**, mỗi VU một account riêng (pool 500 user), có assertion phát hiện 403 và có script `reset_lockout.js` để reset giữa các lần chạy.

> Nhận xét hiệu năng: login *luôn* chạy một câu `UPDATE` (kể cả khi thành công) → với SQLite (khóa ghi toàn DB) login là thao tác ghi, cạnh tranh khóa với checkout.

## 2. API Order History – `GET /api/orders/my-orders`

| Mục | Chi tiết |
|---|---|
| Auth | `Authorization: Bearer <token>` (thiếu → 401, token sai → 403) |
| 200 | Mảng đơn hàng `[{id,user_id,total_amount,status,shipping_address,created_at}, ...]` sắp xếp `id DESC` |
| DB | `SELECT * FROM orders WHERE user_id=? ORDER BY id DESC` |
| Không phân trang | Trả **toàn bộ** đơn của user |
| Index | **Không có index trên `orders.user_id`** → full table scan bảng `orders` |

Rủi ro hiệu năng: bảng `orders` tăng sau **mỗi** lần checkout trong lúc test, nên chi phí của API này tăng tuyến tính theo thời gian chạy (đặc biệt rõ ở soak test). Đây là điểm nghi vấn chính của workflow 5.

API liên quan: `GET /api/orders/:id` — **không yêu cầu auth** (IDOR – ai cũng xem được đơn của người khác). Không đưa vào workflow tải nhưng ghi nhận là bug bảo mật.

## 3. API Sản phẩm

| Endpoint | Auth | Hành vi |
|---|---|---|
| `GET /api/products` | Không | `SELECT * FROM products` – 5 sản phẩm seed, trả toàn bộ, không phân trang |
| `GET /api/products?search=kw` | Không | **SQL nối chuỗi** `LIKE '%${kw}%'` → SQL Injection; lỗi trả HTML `<h1>Database Error</h1>` |
| `GET /api/products/:id` | Không | id không tồn tại → **200 `{}`** (lẽ ra 404); id chẵn → `price` trả về kiểu **string** |

Dữ liệu seed: id 1..5 (iPhone 15 Pro Max 30.000.000; Samsung S24 Ultra 28.000.000; MacBook Pro M3 45.000.000; AirPods Pro 2 6.000.000; Keychron Q1 4.000.000).

→ Test plan phải dùng hàm Groovy `Long.parseLong(String.valueOf(price))` để tính tổng, vì `price` có thể là number hoặc string. Assertion cho product detail phải kiểm tra `$.id` tồn tại (vì id sai vẫn trả 200).

## 4. API Cart

| Endpoint | Auth | Hành vi |
|---|---|---|
| `GET /api/cart` | Bearer | Trả mảng item trong `userCarts[userId]` |
| `POST /api/cart` | Bearer | Body `{id,name,price,quantity}` → **push** nguyên body vào mảng |

Phát hiện:
- Giỏ hàng lưu **trong RAM của tiến trình Node** (`const userCarts = {}`), không lưu DB → restart server là mất giỏ.
- Thêm cùng sản phẩm **tạo dòng mới** thay vì tăng số lượng (vi phạm FR-07).
- **Checkout không xóa giỏ** (vi phạm FR-08) → mảng giỏ của mỗi user **tăng vô hạn** trong lúc test ⇒ rò rỉ bộ nhớ + `GET /api/cart` trả payload ngày càng lớn. Cần theo dõi RAM của process `node` trong soak test.
- Không validate body (có thể đẩy giá/qty âm).

## 5. API Checkout – `POST /api/checkout`

| Mục | Chi tiết |
|---|---|
| Auth | Bearer |
| Request (theo spec) | `{"total_amount": 200000, "shipping_address": "..."}`; frontend còn gửi `items`, `coupon_id` (backend bỏ qua) |
| 200 | `{"message":"Checkout successful","orderId": <id>}` |
| DB | 1× `INSERT INTO orders` (ghi) |

Phát hiện:
- Backend **tin `total_amount` từ client**, không tính lại từ giỏ (vi phạm FR-08) → test plan vẫn gửi tổng đúng (price × qty) để dữ liệu hợp lý.
- Không đọc giỏ, không kiểm tra giỏ rỗng, không xóa giỏ.
- `shipping_address` không bắt buộc.

## 6. Đặc điểm hạ tầng ảnh hưởng tới kiểm thử

1. **`database.js` gọi `initDatabase()` khi được `require`** → mỗi lần khởi động `node server.js` DB bị DROP & seed lại (chỉ còn 2 user, 0 đơn). ⇒ Bước chuẩn bị dữ liệu **phải chạy sau khi server đã khởi động**, qua API.
2. Một kết nối sqlite3 duy nhất, không bật WAL, không có index phụ → mọi ghi (login UPDATE, checkout INSERT) tuần tự hóa.
3. Node.js đơn luồng: JSON serialize + JWT verify/sign đều trên event loop.
4. Không rate limit, không connection limit.

## 7. Tóm tắt bug/issue phát hiện khi khảo sát (ứng viên GitHub Issues)

| # | Loại | Mô tả |
|---|---|---|
| B1 | Functional | Login sai tăng bộ đếm +2, khóa 180s (spec: +1, 30s) |
| B2 | Functional | Checkout không xóa giỏ hàng |
| B3 | Performance | Giỏ hàng in-memory tăng vô hạn → memory leak |
| B4 | Performance | Không có index `orders.user_id`, `users.email`; my-orders không phân trang |
| B5 | Security | `GET /api/orders/:id` không yêu cầu auth (IDOR) |
| B6 | Security | SQL injection ở `GET /api/products?search=` |
| B7 | Functional | Checkout tin `total_amount` của client |
| B8 | Functional | `GET /api/products/:id` id không tồn tại trả 200 `{}`; id chẵn trả price dạng string |
| B9 | Security | JWT không hết hạn, secret hard-code; `/api/register` không chặn trùng email |
