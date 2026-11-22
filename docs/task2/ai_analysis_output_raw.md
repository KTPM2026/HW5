# Task 2 – Output nguyên văn của AI phân tích

- **Công cụ:** Claude Code – subagent `general-purpose` (model Claude Opus 5.5), phiên mới, không có ngữ cảnh hội thoại trước
- **Thời gian:** 22/11/2026, ~15:35–15:39 (GMT+7)
- **Prompt:** xem `ai_analysis_prompt.md`
- **Đầu vào AI được đọc:** `server.js`, `database.js`, 5 file `analysis.md` (Load, Stress, Stress breakpoint, Spike, Soak), vài dòng đầu `.jtl`, `node_resource.csv`, `console.txt`, `bench_index.md`

---

## Câu 1. Phân tích kết quả từng kịch bản và đề xuất ngưỡng hiệu năng

### Lưu ý chung trước khi đọc số liệu
- JMeter và server chạy chung 1 laptop → ở tải cao JMeter (JVM tới 2000 thread) giành CPU với node; các giới hạn đo được là giới hạn của cả cụm "client + server", thấp hơn năng lực thật của server.
- Dữ liệu không được reset giữa các lần chạy: bảng `orders` tăng 1.500 → 2.510 (Load) → 26.441 (Stress) → 28.163 (Spike) → 55.973 (Stress mạnh) → 117.431 (sau Soak). Vì `GET /api/orders/my-orders` trả về toàn bộ đơn của user và không có index, các lần chạy sau chịu "tải dữ liệu" nặng hơn — cần lưu ý khi so sánh giữa các kịch bản.
- Cột "Message" trong bảng lỗi của Stress mạnh ghi "Sai HTTP status (403 = tài khoản bị khóa / token sai)" — đây chỉ là nhãn mặc định của assertion, **không** có response 403 nào; toàn bộ lỗi là lỗi tầng TCP (Non HTTP response code), xem Câu 2.
- Think time: Load 1–3 s, Spike 1–2 s, Stress/Soak 0,3–1,0 s; Stress mạnh đạt ~2,3 req/s/VU so với ~1,5 req/s/VU ở Stress thường, tức think time ngắn hơn.

### 1.1 Load test (50 VU, 6 phút)
- 8.268 request, **0% lỗi**, throughput ổn định **~25 RPS** (23,2 RPS trung bình), 1.010 đơn hàng (2,83 đơn/s).
- Thời gian phản hồi rất thấp: avg 2,0 ms, **p95 5 ms**, p99 7 ms, max 42 ms. Bước chậm nhất là Checkout (INSERT, p95 7 ms).
- Tài nguyên: CPU node ~4% (đỉnh 7%), RAM ổn định 84–85 MB.
- **Đánh giá:** Đạt tốt — hệ thống gần như "nhàn rỗi", không có vấn đề. Mức tải này chỉ dùng <5% năng lực.

### 1.2 Stress test (100 → 500 VU, bậc 100 VU/90 s)
- 193.203 request, **0% lỗi**, 23.931 đơn (53 đơn/s), throughput trung bình 430 RPS.
- RPS tăng gần tuyến tính theo VU từ 100 → 400 VU (154 → 307 → 459 → 610 RPS), p95 chỉ tăng nhẹ 5 → 16 ms.
- **Điểm gãy khúc (knee) ở ~500 VU / ~730 RPS:** RPS chỉ tăng thêm ~20% (lẽ ra ~25%) nhưng **p95 tăng gấp 4 (23 → 90 ms)**, avg 7,5 → 31 ms, max 244 ms → dấu hiệu bão hòa, request bắt đầu xếp hàng.
- CPU node trung bình 60%, đỉnh **118%** (event loop JS đơn luồng, ~100% là trần thực tế); RAM tăng 85 → 138 MB và không giảm lại.
- **Đánh giá:** Đạt (không lỗi, p95 < 100 ms), nhưng đã chạm trần của tiến trình node đơn luồng ở khoảng 700–750 RPS với cấu hình think time này.

### 1.3 Stress mạnh (400 → 2000 VU, bậc 400 VU/90 s)
- **400 VU:** ~920–970 RPS, 0% lỗi nhưng p95 đã 355–505 ms (với think time ngắn, hệ thống bão hòa ngay từ bậc đầu).
- **800 VU:** RPS không tăng mà giảm nhẹ (906 → 854), **p95 ~1,3 s**, avg ~830 ms, vẫn 0% lỗi → vùng suy giảm (chỉ xếp hàng, không phục vụ thêm được).
- **1.100–1.200 VU (giây 180–240):** bắt đầu lỗi — console ghi 4,5% lỗi tại 1.094 VU, cửa sổ 180–210 s 23,7%, 210–240 s 73%.
- **1.300–2.000 VU:** lỗi 90–98%, max response 30,5 s (= timeout đọc 30 s của JMeter).
- RPS báo cáo tăng vọt lên ~2.500/s nhưng là **ảo**: phần lớn là request Login bị từ chối kết nối ngay lập tức (~1 ms) rồi thread lập tức vòng lặp mới (`on_sample_error = startnextloop`) → "retry storm". **Goodput (request thành công) sụp đổ**: ~900 RPS (≤800 VU) → ~590 (210–240 s) → ~190 (240–300 s) → ~100–130 (300–360 s) → **chỉ còn ~45–65 RPS** ở 2000 VU. Login chiếm 567.676 sample với 94,9% lỗi.
- Các bước 02–08 ít lỗi (0,06–0,97%) nhưng rất chậm: p95 1,6–5,7 s, p99 ~11 s.
- Tiến trình node **không crash** (node_resource.csv vẫn ghi đến cuối, CPU-time vẫn tăng), không có HTTP 5xx, không có lỗi SQLite; CPU trung bình 67%, đỉnh 126%; RAM lên tới 188 MB rồi tụt về ~96–111 MB khi phần lớn kết nối bị từ chối.
- **Đánh giá:** Không đạt từ 800 VU (vi phạm p95) và **gãy chức năng ở ~1.100–1.200 VU**.

### 1.4 Spike test (20 → 320 VU trong 5–10 s, giữ 60 s, về 20 VU)
- 15.247 request, **0% lỗi**. RPS nhảy 13 → 201–203 khi spike, p95 chỉ tăng 6 → 7 ms, max 36 ms.
- Phục hồi tức thì: ngay cửa sổ 180–210 s sau spike p95 về 6 ms, RPS về 13. RAM 65 → 103 MB khi spike rồi về 74 MB (GC thu hồi tốt). CPU đỉnh 46%.
- **Đánh giá:** Đạt. Tuy nhiên spike này **quá nhẹ** (chỉ ~200 RPS, <30% năng lực) nên chỉ chứng minh hệ thống hấp thụ được đột biến vừa phải; chưa chứng minh khả năng chịu đột biến vượt ngưỡng. Nên chạy thêm spike lên 800–1.200 VU với think time 0,3–1 s để kiểm tra khả năng phục hồi sau quá tải.

### 1.5 Soak test (400 VU, 15 phút)
- 484.715 request, **0% lỗi**, 60.447 đơn (67 đơn/s), throughput trung bình 539 RPS. Không crash.
- **Vấn đề: hiệu năng suy giảm liên tục theo thời gian** dù số VU không đổi:

  | Chỉ số | Phút 1–2 | Phút 14–15 | Thay đổi |
  |---|---:|---:|---:|
  | RPS | 599 | 494 | −17,5% |
  | Avg | 15 ms | 146 ms | ×~9,5 |
  | p95 | 47 ms | 393 ms | ×~8,4 |
  | Max | 107 ms | 661 ms | ×~6 |

- p95 tổng 244 ms; các bước có truy cập DB đều có p95 ~250–280 ms, còn hai bước giỏ hàng (06, 07 — không chạm DB) vẫn p95 ~92 ms → cả event loop bị nghẽn chứ không chỉ riêng truy vấn.
- CPU node trung bình **104%** — event loop bão hòa suốt 15 phút, tức là mức tải soak (400 VU, think 0,3–1 s) đang nằm ngay sát trần năng lực.
- RAM 109 → 127 MB (đỉnh), cuối 125 MB: tăng ~15% trong 15 phút — chậm nhưng không có xu hướng giảm (xem Câu 2).
- **Đánh giá:** Đạt về lỗi, **không đạt về độ ổn định thời gian phản hồi**.

### 1.6 Đề xuất ngưỡng hiệu năng (SLO) cho hệ thống này
Dựa trên năng lực đo được (baseline p95 ~5 ms ở tải thấp, trần ~700–900 RPS) và kỳ vọng thông thường của web API thương mại điện tử:

| Nhóm | Chỉ số | Ngưỡng đề xuất |
|---|---|---|
| Thời gian phản hồi | p95 các API đọc (02–05, 07) | ≤ 200 ms |
| | p95 API ghi (01 Login, 06, 08 Checkout) | ≤ 300 ms |
| | p99 toàn bộ | ≤ 500 ms; max ≤ 2 s |
| | Ở mức tải thường (≤50 VU) | p95 ≤ 50 ms (baseline thực tế ~5 ms — dùng để phát hiện regression) |
| Lỗi | Load / Soak | < 0,1% (mục tiêu 0%) |
| | Stress tới mức tải thiết kế, Spike | < 1%; không có lỗi tầng kết nối (connection refused/reset) |
| Throughput | Năng lực bền vững tối thiểu | ≥ 500 RPS (~60 workflow/đơn hàng/s) với p95 trong ngưỡng |
| | Mức vận hành khuyến nghị | ≤ 70% trần ≈ 500–600 RPS (~350–400 VU với think 0,3–1 s) |
| Ổn định (soak) | Độ trôi | p95 cửa sổ cuối ≤ 1,2 × p95 cửa sổ ổn định đầu; RPS giảm ≤ 5% |
| | Bộ nhớ | RAM tăng ≤ 10%/giờ, phải về lại mức nền sau khi hết tải |
| Phục hồi (spike) | | p95 về baseline trong ≤ 30 s sau khi tải giảm |
| Tài nguyên | | CPU node ≤ 80% một core ở mức tải thiết kế (chừa dư địa cho đột biến) |

Đối chiếu: Load, Stress (≤500 VU) và Spike **đạt**; Stress mạnh **không đạt** từ 800 VU (p95 >1 s) và ~1.100 VU (lỗi >1%); Soak **không đạt** cả p95 tổng (244 ms > 200 ms cho API đọc) lẫn tiêu chí độ trôi (p95 ×8, RPS −17,5%).

---

## Câu 2. Điểm gãy, nguyên nhân lỗi và độ ổn định khi chạy lâu

### 2.1 Điểm gãy nằm ở đâu
Cần phân biệt ba mốc:
1. **Điểm bão hòa (knee): ~400–500 VU, tương ứng ~730–970 RPS** (tùy think time và lượng dữ liệu). Từ đây RPS ngừng tăng, latency tăng vọt, CPU node chạm ~100–126% (event loop đơn luồng đã đầy).
2. **Điểm vi phạm SLO: ~800 VU** — p95 ~1,3 s, RPS giảm nhẹ, chưa có lỗi.
3. **Điểm gãy chức năng (breaking point): ~1.100–1.200 VU** (giây 180–240 của Stress mạnh): tỷ lệ lỗi nhảy từ 0% → 4,5% → 23,7% → 73%, rồi >90% từ 1.300 VU; goodput sụp từ ~900 RPS xuống ~50 RPS. Đây là kiểu sụp đổ dây chuyền (congestion collapse), không phải suy giảm từ từ.

### 2.2 Nguyên nhân gây lỗi
Toàn bộ lỗi nằm ở **tầng kết nối TCP** — không có HTTP 4xx/5xx, không có lỗi SQLite:

| Loại lỗi | Số lượng | Ý nghĩa |
|---|---:|---|
| `HttpHostConnectException: Connection refused` | 534.586 (Login) + ~500 (bước khác) | Server từ chối kết nối mới |
| `java.net.BindException: Address already in use` | 3.999 | Máy client (JMeter) hết cổng tạm (ephemeral port) |
| `SocketTimeoutException: Read timed out` (30 s) | 198 | Request được nhận nhưng không được xử lý kịp trong 30 s |
| `SocketException: Connection reset` | ~110 | Kết nối keep-alive bị đóng/reset giữa chừng |

Chuỗi nhân quả:
1. **Gốc rễ: Node.js chỉ có một event loop.** Mọi việc — parse JSON, ký/kiểm JWT, chuyển dòng SQLite thành object JS, `JSON.stringify` response, `accept()` kết nối mới — đều chạy trên một luồng. CPU node đạt đỉnh 118–126% (≈100% luồng JS + phần threadpool libuv của sqlite3). Vượt mức này, request chỉ còn xếp hàng.
2. **Hàng đợi accept tràn.** Khi event loop quá bận, node không kịp `accept()`; backlog của socket lắng nghe (mặc định 511) đầy → trên Windows SYN mới bị trả RST → JMeter nhận "Connection refused". Login bị gần như toàn bộ lỗi này vì là bước đầu mỗi vòng lặp (thường phải mở kết nối mới), các bước sau tái sử dụng kết nối keep-alive nên ít bị.
3. **Retry storm khuếch đại sự cố.** Test plan đặt `on_sample_error = startnextloop` và không có backoff: Login lỗi → thread lập tức Login lại mà không có think time. Hàng nghìn thread liên tục mở kết nối mới làm RPS ảo ~2.500/s, giữ backlog luôn đầy, đè bẹp các request hợp lệ.
4. **Cạn cổng tạm phía client.** Vòng lặp mở/đóng kết nối liên tục tạo rất nhiều socket TIME_WAIT trên Windows (dải cổng mặc định 49152–65535) → `BindException: Address already in use`. Đây là giới hạn của môi trường test, không phải của server.
5. **Dữ liệu tăng làm công việc mỗi request nặng dần**: `SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC` không có index và không LIMIT (benchmark `results/optimization/bench_index.md`: EXPLAIN = `SCAN orders` trên 117k dòng, 10,7 ms/truy vấn, trả trung bình 235 dòng); `SELECT * FROM users WHERE email = ?` cũng là `SCAN users`; mỗi Login thành công còn chạy thêm một `UPDATE users` (ghi đĩa) với SQLite ở chế độ journal mặc định (rollback journal, chỉ một writer).
6. **Môi trường dùng chung**: JMeter 2.000 thread chạy cùng máy, tranh CPU với node, làm điểm gãy đo được thấp hơn thực tế.

Kết luận: **điểm nghẽn chính là CPU của event loop node đơn tiến trình**, bị làm nặng thêm bởi truy vấn không index/không phân trang và response phình to; lỗi chỉ lộ ra dưới dạng từ chối kết nối và bị retry storm phía JMeter khuếch đại. Server không crash — nếu giảm tải, nó sẽ trở lại phục vụ bình thường (như đã thấy ở Spike: phục hồi tức thì khi tải dưới trần).

### 2.3 Hệ thống có ổn định khi chạy lâu không?
**Ổn định về chức năng, nhưng không ổn định về hiệu năng.**

- Ổn định: 0 lỗi trên 484.715 request, không crash, không lỗi DB, RAM không tăng đột biến (109 → 125 MB).
- Không ổn định: latency tăng liên tục gần như tuyến tính (avg ×9,5, p95 47 → 393 ms) và RPS giảm 17,5% trong khi tải không đổi. Ngoại suy xu hướng này, sau ~30–60 phút p95 sẽ vượt 500 ms–1 s.

Nguyên nhân của độ trôi là **dữ liệu tăng không giới hạn**, không phải rò rỉ bộ nhớ thông thường:
1. **Bảng `orders` tăng gấp đôi trong lúc soak (56.984 → 117.431 đơn).** Mỗi View Order History phải quét toàn bảng (không index trên `user_id`) và trả *toàn bộ* đơn của user: kích thước response đo trong .jtl tăng từ ~17 KB lên ~37 KB. Việc chuyển dòng → object → `JSON.stringify` diễn ra trên event loop, nên chi phí này làm chậm *mọi* request, kể cả các bước không truy cập DB.
2. **Giỏ hàng trong bộ nhớ (`userCarts`) chỉ tăng không giảm**: mỗi Add to Cart `push` vào mảng của user, Checkout không xóa giỏ, không có giới hạn/TTL. Response View Cart cuối soak đã ~15–17 KB và tiếp tục tăng. Đây là **rò rỉ bộ nhớ theo thiết kế** — nguyên nhân chính của mức tăng ~16 MB RAM trong 15 phút, và sẽ không bao giờ dừng nếu server chạy nhiều giờ/ngày.
3. Mức tải soak (CPU ~104%) sát trần nên mọi chi phí tăng thêm chuyển thẳng thành thời gian chờ trong hàng đợi.

Khuyến nghị kiểm thử: chạy lại soak ở ~60–70% năng lực (~250–300 VU hoặc ~500 RPS) trong ít nhất 1–2 giờ, sau khi đã áp dụng index/phân trang/sửa giỏ hàng, để tách bạch ảnh hưởng của dữ liệu với ảnh hưởng bão hòa CPU.

---

## Câu 3. Đề xuất tối ưu cho backend

(Xếp theo tỷ lệ lợi ích / công sức, từ cao đến thấp.)

### 3.1 Thêm index cho các truy vấn nóng (ưu tiên số 1)
```sql
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id, id DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_coupon_usage_coupon_user ON coupon_usage(coupon_id, user_id);
```
- **Lợi ích:** benchmark thực tế trên 117.431 đơn: View Order History từ **10,7 ms → 1,2 ms/truy vấn (~9×)**, kế hoạch thực thi đổi từ `SCAN orders` sang `SEARCH ... USING INDEX`; Login từ `SCAN users` → `SEARCH users USING INDEX idx_users_email`. Quan trọng hơn: chi phí truy vấn không còn tăng tuyến tính theo kích thước bảng → khử phần lớn độ trôi của soak. Index UNIQUE trên email còn chặn đăng ký trùng email.

### 3.2 Phân trang lịch sử đơn hàng và chỉ SELECT cột cần thiết
- `SELECT id, total_amount, status, created_at FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 20` (hoặc keyset `AND id < ?`).
- **Lợi ích:** benchmark: index + LIMIT 20 chỉ **0,18 ms (~59× nhanh hơn hiện tại)**; response giảm từ ~37 KB xuống ~2–3 KB → giảm mạnh chi phí chuyển dòng/`JSON.stringify` trên event loop — đây là tối ưu có tác động lớn nhất lên CPU node. Ước tính p95 soak trở về mức vài chục ms và RPS không còn suy giảm theo thời gian.
- Tương tự cho `/api/admin/orders` (JOIN toàn bảng) và `/api/products`.
- Login không nên `SELECT *` rồi trả nguyên `user` (đang trả cả mật khẩu trong response — vừa là lỗi bảo mật vừa tốn băng thông).

### 3.3 Bật SQLite WAL và tinh chỉnh PRAGMA
```js
db.exec(`PRAGMA journal_mode = WAL;
         PRAGMA synchronous = NORMAL;
         PRAGMA busy_timeout = 5000;
         PRAGMA cache_size = -20000;   -- ~20 MB page cache
         PRAGMA temp_store = MEMORY;
         PRAGMA mmap_size = 268435456;`);
```
- **Lợi ích:** WAL cho phép đọc không chặn ghi và ngược lại; mỗi commit chỉ append vào file WAL, với `synchronous=NORMAL` không cần fsync mỗi giao dịch → các bước ghi (Login UPDATE, Checkout INSERT ~25% số request) nhanh hơn vài lần, giảm độ trễ đuôi (p99) khi đọc–ghi đan xen. `busy_timeout` tránh lỗi `SQLITE_BUSY` khi chuyển sang nhiều tiến trình (mục 3.6). WAL là điều kiện bắt buộc để chạy cluster với SQLite.

### 3.4 Bỏ các lệnh ghi không cần thiết, dùng prepared statement
- Login chỉ `UPDATE users SET login_attempts = 0, locked_until = NULL` khi `login_attempts > 0` hoặc `locked_until IS NOT NULL` (hiện *mọi* lần đăng nhập đều ghi đĩa).
- Chuẩn bị sẵn các câu lệnh nóng (`db.prepare(...)`) một lần lúc khởi động và tái sử dụng, thay vì để SQLite parse lại SQL mỗi request.
- **Lợi ích:** giảm ~50% số lệnh ghi của workflow (8 bước hiện có 2 lệnh ghi → còn 1), giảm tranh chấp khóa ghi duy nhất của SQLite; prepared statement tiết kiệm chi phí parse (~5–15% cho truy vấn ngắn).

### 3.5 Cache dữ liệu đọc nhiều, ít thay đổi
- `/api/products`, `/api/products/:id`, `/api/categories` (bước 03, 05 và một phần 04) chiếm ~3/8 lưu lượng nhưng dữ liệu gần như tĩnh → cache trong bộ nhớ (ví dụ `lru-cache`, TTL 30–60 s, xóa cache khi POST/PUT/DELETE sản phẩm), kèm `ETag`/`Cache-Control: max-age=30` để trình duyệt/CDN cache. Có thể cache sẵn chuỗi JSON đã serialize để bỏ qua cả `JSON.stringify`.
- **Lợi ích:** ~35% request không chạm DB và gần như không tốn CPU → tăng năng lực tổng thể ước tính 20–40%. (Khi chạy cluster, dùng Redis làm cache chung.) Đồng thời sửa lỗi **SQL injection** ở search (`LIKE '%${searchQuery}%'`) bằng tham số `LIKE ?`.

### 3.6 Tận dụng đa nhân: Node cluster / PM2 (tối ưu lớn nhất về throughput)
- CPU node chỉ đạt ~100–126% trên máy 12 luồng — tức đang dùng ~1/12 năng lực CPU. Chạy `pm2 start server.js -i 4` (hoặc `node:cluster`) với 4–6 worker (chừa nhân cho OS và JMeter, hoặc tách JMeter ra máy khác).
- **Lợi ích:** trần throughput kỳ vọng tăng **~3–4× (từ ~900 lên ~2.500–3.500 RPS)** cho phần đọc; điểm gãy dịch lên nhiều nghìn VU; mỗi worker có event loop và backlog riêng nên lỗi "Connection refused" giảm hẳn.
- **Điều kiện kèm theo:** bật WAL (3.3) vì SQLite vẫn chỉ một writer; **chuyển `userCarts` ra khỏi bộ nhớ tiến trình** (Redis hoặc bảng `cart_items`) vì các worker không chia sẻ RAM — nếu không giỏ hàng sẽ sai giữa các request; tăng `UV_THREADPOOL_SIZE` (ví dụ 8–16) nếu vẫn dùng `sqlite3` bất đồng bộ.

### 3.7 Connection pool / lựa chọn tầng dữ liệu
- Thư viện `sqlite3` hiện dùng **một kết nối duy nhất**; với SQLite, "pool" chủ yếu có ý nghĩa cho đọc. Phương án tốt hơn: chuyển sang `better-sqlite3` (API đồng bộ, nhanh hơn 2–5× cho truy vấn ngắn vì không qua threadpool/callback), kết hợp cluster (mỗi worker một kết nối) + WAL → tương đương pool đọc song song.
- Dài hạn, với nhiều writer đồng thời (Checkout), chuyển sang **PostgreSQL/MySQL** với `pg.Pool` (max ~10–20 kết nối/instance).
- **Lợi ích:** loại bỏ giới hạn một-writer của SQLite, hỗ trợ scale ngang nhiều instance sau load balancer; pool giới hạn số kết nối đồng thời giúp DB không bị quá tải khi spike.

### 3.8 Sửa rò rỉ giỏ hàng
- Xóa giỏ sau Checkout thành công (`delete userCarts[userId]`), gộp sản phẩm trùng (tăng `quantity` thay vì `push`), giới hạn số dòng/giỏ (ví dụ ≤100), TTL cho giỏ không hoạt động, hoặc lưu giỏ vào Redis/DB.
- **Lợi ích:** RAM node không còn tăng theo thời gian; response View Cart giữ cố định vài trăm byte thay vì 15 KB+; loại bỏ một nguồn gây trôi hiệu năng khi soak nhiều giờ.

### 3.9 Bảo vệ khi quá tải ở tầng HTTP
- Tăng backlog: `app.listen(PORT, '0.0.0.0', 2048)`; đặt `server.keepAliveTimeout = 65000`, `server.headersTimeout = 66000` để client tái sử dụng kết nối lâu hơn (giảm số kết nối mới → giảm "Connection refused/reset").
- Thêm **load shedding**: theo dõi độ trễ event loop (`perf_hooks.monitorEventLoopDelay`), khi vượt ngưỡng (ví dụ 100 ms) trả nhanh `503 + Retry-After`; thêm rate limit cho `/api/login` (`express-rate-limit`).
- Chạy với `NODE_ENV=production`, dùng `express.json()` thay `body-parser`, bỏ `cors()` mở toàn bộ nếu không cần.
- **Lợi ích:** khi vượt tải hệ thống suy giảm *có kiểm soát* (trả 503 nhanh, request hợp lệ vẫn được phục vụ, goodput giữ gần trần) thay vì sụp goodput xuống ~50 RPS như ở Stress mạnh; không còn thời gian chờ tới timeout 30 s.

### 3.10 Cải thiện quy trình đo (để kết quả đáng tin hơn)
- Tách JMeter sang máy khác (hoặc ít nhất giới hạn CPU affinity) để không tranh CPU với server.
- Đổi `on_sample_error` của Login thành `continue` + think time, hoặc thêm backoff, để tránh retry storm làm sai lệch RPS/lỗi.
- Bật "Same user on each iteration" để tái sử dụng kết nối; nếu cần tải lớn từ Windows, tăng `MaxUserPort`/giảm `TcpTimedWaitDelay` để tránh `BindException`.
- **Reset/chuẩn hóa dữ liệu trước mỗi lần chạy** (số đơn hàng cố định) để các kịch bản so sánh được với nhau; theo dõi thêm event-loop lag và số kết nối TCP.
- Sau khi tối ưu, chạy lại cùng bộ kịch bản và so sánh với baseline hiện tại (trần ~900 RPS, p95 soak 393 ms, điểm gãy ~1.100 VU).

### Tóm tắt lợi ích kỳ vọng
| Tối ưu | Tác động chính | Mức kỳ vọng |
|---|---|---|
| Index `orders(user_id,id)`, `users(email)` | Latency truy vấn, khử trôi soak | 10,7 → 1,2 ms/truy vấn (~9×, đã đo) |
| Phân trang + chọn cột | CPU event loop, kích thước response | 10,7 → 0,18 ms (~59×, đã đo); response 37 KB → ~3 KB |
| WAL + PRAGMA | Latency ghi, đọc–ghi song song | Ghi nhanh hơn vài lần, giảm p99 |
| Bỏ UPDATE thừa ở Login, prepared statement | Số lệnh ghi | −50% lệnh ghi |
| Cache sản phẩm/danh mục | Tải DB/CPU | ~35% request gần như miễn phí, +20–40% năng lực |
| Cluster 4–6 worker (+Redis cho giỏ) | Trần throughput, điểm gãy | ~3–4× RPS, điểm gãy lên nhiều nghìn VU |
| better-sqlite3 / PostgreSQL + pool | Thông lượng DB, scale ngang | 2–5× cho truy vấn ngắn; bỏ giới hạn một-writer |
| Sửa rò rỉ `userCarts` | RAM, ổn định dài hạn | RAM phẳng, View Cart response cố định |
| Backlog/keep-alive/load shedding/rate limit | Hành vi khi quá tải | Giữ goodput khi quá tải thay vì sụp; không còn timeout 30 s |
