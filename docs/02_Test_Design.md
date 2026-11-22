# 02 – Thiết kế kịch bản Performance Testing (Người 5 – Workflow 5)

## 1. Workflow & độ phủ nhóm endpoint

Mỗi vòng lặp (iteration) của 1 virtual user (VU) = 1 phiên mua hàng của 1 khách khác nhau (CSV `users.csv`, `shareMode.all`, recycle):

| # | Sampler | Endpoint | Nhóm | Assertion | Trích xuất |
|---|---|---|---|---|---|
| 01 | Login | `POST /api/login` | **Auth-heavy** | HTTP 200 + `$.token` tồn tại | `token`, `user_id` |
| 02 | View Order History | `GET /api/orders/my-orders` | **Read-heavy** | 200 + `$[0].user_id == ${user_id}` (đơn đúng chủ) | `history_size` |
| 03 | Browse Products | `GET /api/products` | Read-heavy | 200 + `$[0].id` | |
| 04 | Search Products | `GET /api/products?search=${keyword}` | Read-heavy | 200 + `$[0].name` | |
| 05 | Product Detail | `GET /api/products/${product_id}` | Read-heavy | 200 + `$.id` tồn tại (id sai vẫn 200 `{}`) | `prod_name`, `price` |
| 06 | Add to Cart | `POST /api/cart` | **Transactional** | 200 + `$.message == "Added to cart"` | |
| 07 | View Cart | `GET /api/cart` | Transactional | 200 + `$[0].id` | |
| 08 | Checkout | `POST /api/checkout` | **Transactional** | 200 + `$.orderId` tồn tại | `order_id` |

Lý do độ phủ: workflow có 1 thao tác auth (login có `UPDATE` – ghi DB), 4 thao tác đọc (trong đó *Order History* là truy vấn quét toàn bảng `orders` không index) và 3 thao tác giao dịch (giỏ in-memory + `INSERT` đơn hàng). Tỉ lệ đọc/ghi ≈ 5:3 mỗi vòng, phản ánh hành vi khách quay lại xem đơn cũ rồi mua tiếp.

`ThreadGroup.on_sample_error = startnextloop`: bước nào lỗi (vd. login 403) thì bỏ phần còn lại của phiên — đúng hành vi người dùng thật (không đăng nhập được thì không mua được) và tránh gửi checkout với token rỗng.

## 2. Dữ liệu (data-driven)

| File | Cột | Số dòng | Nguồn |
|---|---|---|---|
| `data/users.csv` | `email,password,shipping_address` | 500 | `scripts/prepare_data.js` đăng ký qua `POST /api/register` |
| `data/products.csv` | `product_id,quantity,keyword` | 10 (5 SP × qty 1/2) | lấy từ `GET /api/products` |

- Mỗi user được tạo sẵn **3 đơn** (tổng 1.500 đơn) để Order History có dữ liệu thật ngay từ đầu.
- 500 account ≥ số VU tối đa (Stress 500 VU, Spike 320 VU) → không có 2 VU cùng dùng 1 account cùng lúc ở mức tải thường.
- Tổng tiền checkout = `price × quantity` tính bằng `__jexl3` (backend tin `total_amount` từ client – bug B7 – nên phải gửi đúng để dữ liệu đơn hợp lý).
- Từ khóa tìm kiếm được `__urlencode` (có ký tự tiếng Việt, ví dụ "Bàn").

**Quy trình reset giữa các lần chạy** (`scripts/run_scenario.sh` tự làm):
1. `node scripts/reset_lockout.js` → `UPDATE users SET login_attempts=0, locked_until=NULL`.
2. Không restart server (restart = DB bị DROP/seed lại, mất 500 user) — nếu buộc phải restart thì chạy lại `prepare_data.js`.

## 3. Tham số 3 kịch bản (+ soak)

| | Load | Stress | Spike | Soak (endurance) |
|---|---|---|---|---|
| File | `{ID}_Load_20261119.jmx` | `{ID}_Stress_20261119.jmx` | `{ID}_Spike_20261119.jmx` | `{ID}_Soak_20261119.jmx` |
| Hình dạng tải | 50 VU cố định | Bậc thang 5 × 100 VU, mỗi bậc 90s (100→500); biến thể breakpoint `-Jstep_users=400 -Jthink_min=0 -Jthink_range=200` (400→2000) | Nền 20 VU; +300 VU trong 5s tại t=120s, giữ 60s | 400 VU cố định (~600 RPS ≈ 65% năng lực tối đa đo từ Stress) |
| Ramp-up | 60s | 30s / bậc | 10s nền, **5s** đột biến | 60s |
| Thời lượng | 360s | 450s | 300s | 900s (15 phút) |
| Think-time | Uniform 1–3s | Uniform 0.3–1s | Uniform 1–2s | Uniform 0.3–1s |
| Listener (report view) | **Summary Report** | **Aggregate Report** | **View Results Tree** (chỉ lỗi) | Simple Data Writer |
| Mục tiêu | Xác nhận SLA ở tải dự kiến | Tìm điểm gãy (breaking point) | Khả năng chịu & hồi phục sau đột biến | Ngưỡng bền (RPS ổn định, trần RAM) |

Mọi tham số là JMeter property, chỉnh bằng `-J` không sửa file, ví dụ: `-Jusers=80 -Jduration=600`, `-Jstep_users=150`, `-Jspike_users=500`.

**Giải thích lựa chọn tham số**
- *Think-time 1–3s (Load)*: thời gian người dùng đọc trang giữa các thao tác trên SPA; với ~8 request/phiên → mỗi VU ≈ 0.4 req/s → 50 VU ≈ 20 req/s, mức "giờ cao điểm" hợp lý cho demo shop.
- *Ramp-up 60s*: tránh hiệu ứng khởi động đồng loạt làm méo số liệu Load (spike là việc của kịch bản Spike).
- *Stress bậc thang*: mỗi bậc giữ 60s sau khi ramp để hệ thống ổn định → đọc được p95/RPS theo bậc và xác định bậc đầu tiên vi phạm SLA. Think-time giảm còn 0.3–1s để tăng áp lực.
- *Spike 5s*: mô phỏng flash-sale/thông báo đẩy; giai đoạn 180–300s chỉ còn nền để đo thời gian hồi phục.

## 4. SLA / ngưỡng đánh giá (đề xuất)

| Chỉ số | Ngưỡng |
|---|---|
| p95 response time từng request (Load) | ≤ 500 ms |
| p95 Checkout / Login | ≤ 800 ms |
| Error rate (Load) | < 1% |
| Error rate (Stress, bậc "ổn định") | < 5% |
| Hồi phục sau spike | p95 trở về ≤ 1,5× baseline trong ≤ 30s |
| APDEX (HTML report) | satisfied 500 ms / tolerated 1500 ms |

## 5. Xử lý khóa tài khoản (FR-02)

- Chỉ dùng credential hợp lệ; không có request sai mật khẩu trong workflow → về lý thuyết không kích hoạt khóa.
- Nhưng code khóa ngay sau **2** lần sai trong **180s** (B1), nên chỉ cần CSV hỏng 1 dòng là khóa → assertion `HTTP 200` ở Login có message "403 = tài khoản bị khóa"; `run_scenario.sh` in số user bị khóa trước/sau mỗi lần chạy (`pre_run_db.txt`, `post_run_db.txt`).

## 6. Lệnh chạy

```bash
# 1. khởi động backend (DB reset!) rồi chuẩn bị dữ liệu
cd eshop-sut/backend && node server.js
node member5/scripts/prepare_data.js --users 500 --orders 3
# 2. sinh test plan với MSSV thật
python member5/scripts/gen_testplans.py --student-id <MSSV> --date 20261119
# 3. chạy (CLI, xuất .jtl + HTML report + RAM/CPU node)
bash member5/scripts/run_scenario.sh Load
bash member5/scripts/run_scenario.sh Stress
bash member5/scripts/run_scenario.sh Spike
bash member5/scripts/run_scenario.sh Soak
# 4. phân tích
python member5/scripts/analyze_jtl.py member5/results/<plan>/<plan>.jtl --resource member5/results/<plan>/node_resource.csv
```

Để quay video/chụp màn hình: mở `.jmx` bằng JMeter GUI (listener tương ứng hiển thị trực tiếp) cạnh Task Manager → tab Details → `node.exe`.
