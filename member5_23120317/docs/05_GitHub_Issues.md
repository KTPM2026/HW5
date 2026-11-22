# 05 – Nội dung GitHub Issues (Người 5 – Workflow 5)

> Bản nháp để đăng lên trang Issues của repo. Mỗi issue đính kèm ảnh tương ứng trong `evidence/` hoặc ảnh chụp HTML report.

---

## Issue 1 – [Perf] `GET /api/orders/my-orders` chậm dần theo số đơn hàng (full table scan, không phân trang)

**Labels:** performance

**Mô tả.** Truy vấn `SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC` không có index trên `orders.user_id` và trả về toàn bộ đơn của user. Thời gian phản hồi và kích thước response tăng tuyến tính theo kích thước bảng `orders`.

**Bằng chứng**
- `EXPLAIN QUERY PLAN` → `SCAN orders` (`results/optimization/bench_index.md`).
- Bảng 117.431 đơn: 10,68 ms/truy vấn, trung bình 235 đơn/response.
- Soak 400 VU: response Order History 19,4 KB → 34,6 KB; thời gian 22 → 175 ms sau 15 phút.

**Tái hiện.** Chạy `23120317_Soak_20261119.jmx` 15 phút và so sánh p95 phút 1 với phút 15.

**Đề xuất.** `CREATE INDEX idx_orders_user_id ON orders(user_id, id DESC)` + phân trang `LIMIT 20`. Đã đo trên bản sao DB: nhanh hơn 8,9× (chỉ index) và 59× (index + LIMIT).

---

## Issue 2 – [Bug] Giỏ hàng không bị xóa sau checkout, tăng vô hạn trong RAM

**Labels:** bug, performance

**Mô tả.** `POST /api/checkout` không xóa `userCarts[userId]` (vi phạm FR-08). Giỏ lưu trong RAM process (`const userCarts = {}`) nên tăng mãi; `POST /api/cart` cùng sản phẩm tạo dòng mới thay vì tăng số lượng (vi phạm FR-07).

**Tái hiện**
1. Login → `POST /api/cart` → `POST /api/checkout` → `GET /api/cart`.
2. **Mong đợi:** `[]`. **Thực tế:** vẫn còn item đã thanh toán.

**Bằng chứng.** Soak: response `GET /api/cart` 8,8 KB → 15,6 KB trong 15 phút.

---

## Issue 3 – [Bug] Khóa tài khoản sai đặc tả: khóa sau 2 lần sai, khóa 180 giây

**Labels:** bug

**Đặc tả FR-02.** Mỗi lần sai +1; khóa khi ≥ 3 lần; khóa 30 giây.
**Thực tế (`server.js`).** `login_attempts + 2`; khóa 180.000 ms.

**Tái hiện**
```bash
for i in 1 2 3; do curl -s -w " [%{http_code}]\n" -H 'Content-Type: application/json' \
  -d '{"email":"test@eshop.com","password":"wrong"}' localhost:3000/api/login; done
```
Kết quả: `401, 401, 403` → bị khóa ngay ở lần thử thứ 3 (sau 2 lần sai).

---

## Issue 4 – [Perf] Server từ chối kết nối khi > ~1.000 người dùng đồng thời

**Labels:** performance

**Mô tả.** Stress 400 → 2.000 VU (think 0–0,2 s): throughput bão hòa ~900–950 RPS từ 800 VU (p95 ~1,3 s); từ 1.200 VU xuất hiện `HttpHostConnectException` (connection refused), error rate cửa sổ 30 s tăng 23,7% → 98%. Server không crash và tự hồi phục.

**Bằng chứng.** `results/23120317_Stress_20261119_breakpoint/analysis.md`, HTML report cùng thư mục.

**Ghi chú.** Một phần lỗi (`BindException`, 3.999 mẫu) do máy chạy JMeter hết cổng tạm – JMeter chạy chung máy với server.

---

## Issue 5 – [Security] `GET /api/orders/:id` không yêu cầu xác thực (IDOR)

**Labels:** security

**Tái hiện.** `curl localhost:3000/api/orders/1` (không có header `Authorization`) → trả về đầy đủ đơn hàng của user khác (user_id, total_amount, shipping_address).
**Mong đợi.** 401 nếu không có token; 403/404 nếu đơn không thuộc user.

---

## Issue 6 – [Security] `POST /api/login` trả về mật khẩu plaintext trong response

**Labels:** security

**Mô tả.** Login thành công trả `res.json({ message, token, user })`, trong đó `user` là nguyên bản ghi `SELECT *` gồm cột `password` (lưu plaintext), `reset_token`, `login_attempts`.

**Tái hiện**
```bash
curl -s -H 'Content-Type: application/json' -d '{"email":"test@eshop.com","password":"Test1234!"}' localhost:3000/api/login
```
Kết quả: `"user":{"id":2,"name":"Test User","email":"test@eshop.com","password":"Test1234!",...}`.

**Mong đợi.** Chỉ trả các trường cần thiết (`id, name, email, role`); mật khẩu phải được băm (bcrypt) và không bao giờ trả về client.

> Phát hiện bởi AI trong Task 2 và đã được kiểm chứng thủ công.
