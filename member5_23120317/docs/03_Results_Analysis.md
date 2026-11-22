# 03 – Kết quả, phân tích & đề xuất tối ưu (Người 5 – Workflow 5)

> Tất cả số liệu dưới đây được tính lại từ file `.jtl` gốc bằng `scripts/analyze_jtl.py` (chi tiết: `results/<plan>/analysis.md`) và từ `node_resource.csv` (RAM/CPU tiến trình node lắng nghe port 3000). **Load, Stress, Spike: lần chạy chính thức ngày 22/11/2026** (có quay video, DB sạch 1.500 đơn lúc bắt đầu, 0 user bị khóa trước/sau mỗi lần chạy – xem `pre_run_db.txt`/`post_run_db.txt`). **Stress-breakpoint và Soak: lần chạy khảo sát ngày 19/11/2026** (không quay video, dùng để tìm điểm gãy và ngưỡng bền).

## 1. Môi trường

| Hạng mục | Giá trị |
|---|---|
| Hostname | VICTUS16 |
| CPU | AMD Ryzen 5 6600H – 6 core / 12 thread |
| RAM | 16 GB (16.384 MB theo dxdiag; Windows báo 15,2 GB khả dụng) |
| OS | Windows 11 Home Single Language (10.0.26300) |
| Java / JMeter | JDK 25.0.3 / Apache JMeter 5.6.3 (CLI, `-n`) |
| SUT | eshop-sut backend – Node.js v22.19.0, Express 5, sqlite3 (1 connection, journal mặc định) |
| Lưu ý | JMeter và SUT chạy **cùng máy** → ở mức tải cao JMeter cũng tranh CPU/cổng mạng với SUT |

## 2. Tổng hợp kết quả

| Kịch bản | Tải | Sample | RPS TB | Avg | p95 | p99 | Lỗi | RAM node (đầu→đỉnh) | CPU node TB/đỉnh | Đơn tạo |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---:|
| **Load** (22/11) | 50 VU, 6 phút, think 1–3s | 8.268 | 23,2 | 2,0 ms | 5 ms | 7 ms | 0% | 84,6→85,5 MB | 4% / 7% | 1.010 |
| **Stress** (22/11) | 100→500 VU (5 bậc×90s), think 0,3–1s | 193.203 | 429,6 (đỉnh ~735) | 9,6 ms | 45 ms | 91 ms | 0% | 84,9→138,1 MB | 60% / 118% | 23.931 |
| **Stress – breakpoint** (19/11) | 400→2000 VU, think 0–0,2s | 765.531 | xem §3 | 561 ms | 1.321 ms | 6.979 ms | 70,46%* | 68→**188** MB | 67% / 126% | 27.698 |
| **Spike** (22/11) | 20 → +300 VU/5s @120s, giữ 60s → 20 | 15.247 | 51,1 (đỉnh 203) | 2,5 ms | 6 ms | 9 ms | 0% | 64,7→102,8 MB | 9% / 46% | 1.722 |
| **Soak** (19/11) | 400 VU, 15 phút, think 0,3–1s | 484.715 | 538,9 | 67,7 ms | 244 ms | 358 ms | 0% | 109→127 MB | 104% / 119% | 60.447 |

\* xem §6 – con số 70% bị khuếch đại bởi "bão lỗi" ở bước Login.

### 2.1 Load – đạt SLA
Mọi request p95 ≤ 7 ms (Checkout cao nhất: p95 7 ms), 0 lỗi, RPS ổn định ~25/s sau ramp-up, CPU node ≤ 7%. Hệ thống dư năng lực rất nhiều ở mức tải dự kiến.

### 2.1b Stress (theo thiết kế) – chưa gãy
RPS tăng tuyến tính theo bậc (77 → 154 → 307 → 460 → 610 → 735). p95 theo cửa sổ: 5 ms (100–200 VU) → 8 ms (300 VU) → 11–16 ms (400 VU) → **80–90 ms ở 500 VU** – dấu hiệu bắt đầu bão hòa, nhưng 0 lỗi. RAM node 85 → 138 MB, CPU đỉnh 118%.

### 2.2 Spike – chịu được và hồi phục ngay
Khi tăng từ 20 → 320 VU trong 5s, RPS từ ~13 → ~202 nhưng p95 chỉ 6 → 7 ms, 0 lỗi; sau khi rút tải (t=180s), RPS và p95 trở về baseline (13 RPS, p95 6 ms) ngay trong cửa sổ 30s đầu tiên. RAM tăng 64,7 → 102,8 MB rồi giảm về 74 MB (GC).

## 3. Stress – điểm gãy (breaking point)

Lần Stress theo thiết kế (tối đa 500 VU) **không làm gãy** hệ thống (0% lỗi, p95 ≤ 90 ms mỗi cửa sổ). Chạy thêm biến thể mạnh hơn (`-Jstep_users=400 -Jthink_min=0 -Jthink_range=200`):

| Bậc | VU | RPS | p95 | Lỗi | Nhận định |
|---|---:|---:|---:|---:|---|
| 1 | 400 | 840–967 | 355–505 ms | 0% | Vùng tối đa còn đạt SLA p95 ≤ 500 ms |
| 2 | 800 | 854–906 | 953–1.301 ms | 0% | **Bão hòa**: thêm gấp đôi VU nhưng RPS không tăng, latency tăng (Little's law) |
| 3 | 1.200 | 1.063 → 2.207 | 2.171–2.252 ms | 23,7% → 73,2% | **Gãy**: server từ chối kết nối |
| 4–5 | 1.600–2.000 | ~2.400–2.600 | — | 92–98% | RPS "cao" là request hỏng tức thì, không phải năng lực thật |

**Kết luận:** throughput tối đa có ích ≈ **900–950 RPS** (~115–120 phiên mua/s × 8 request); SLA p95 ≤ 500 ms giữ được tới ~400 VU (think ~0,1s); điểm gãy nằm giữa **800 và 1.200 VU**. Sau test, server không crash (lần Load chạy ngay sau đó 0% lỗi) – tự hồi phục.

Phân loại lỗi (từ `.jtl`): 534.586 `HttpHostConnectException` (connection refused – hàng đợi accept/backlog đầy), 3.999 `java.net.BindException` (máy tải hết ephemeral port – giới hạn **phía JMeter**, do chạy cùng máy), 198 `SocketTimeoutException` (>30 s), vài trăm `SocketException`. **0 tài khoản bị khóa** (`post_run_db.txt`) → lỗi không liên quan FR-02.

## 4. Endurance / Soak – ngưỡng bền

Mục tiêu ~600 RPS (≈65% của 950 RPS). Kết quả 15 phút, 0 lỗi nhưng **suy giảm liên tục**:

| Phút | RPS | Avg | p95 |
|---|---:|---:|---:|
| 1–2 | 599 | 15 ms | 47 ms |
| 4–5 | 584 | 35 ms | 101 ms |
| 8–9 | 547 | 81 ms | 260 ms |
| 11–12 | 528 | 111 ms | 281 ms |
| 14–15 | 494 | 146 ms | 393 ms |

Diễn tiến theo cửa sổ 3 phút (từ `.jtl`):

| Phút | Order History: bytes TB / ms | View Cart: bytes TB / ms | Browse Products ms | Login ms |
|---|---|---|---:|---:|
| 0–3 | 19.424 B / 22,1 | 8.839 B / 6,3 | 15,8 | 19,6 |
| 6–9 | 27.157 B / 90,3 | 12.304 B / 26,7 | 79,6 | 88,9 |
| 12–15 | 34.570 B / 174,6 | 15.642 B / 53,2 | 160,3 | 171,9 |

**Ngưỡng bền trên phần cứng này:**
- Duy trì được **~540 RPS trung bình (≈67 đơn hàng/s) trong 15 phút, 0 lỗi, p95 tổng 244 ms** – nhưng không phải trạng thái dừng: RPS giảm 17% và p95 tăng ~8× trong 15 phút. Ngoại suy tuyến tính, p95 vượt 500 ms sau khoảng 18–20 phút ở mức tải này.
- **Trần bộ nhớ:** node 127 MB trong soak (đỉnh tuyệt đối 188 MB khi quá tải) – bộ nhớ **không** phải nút thắt ở thời lượng này dù có rò rỉ giỏ hàng.
- **CPU:** node trung bình 104%, đỉnh 119% của 1 logical core → event loop gần bão hòa.
- Nguyên nhân suy giảm là **tăng trưởng dữ liệu**, không phải rò rỉ tài nguyên (xem §5).

## 5. Phân tích nguyên nhân gốc

1. **Order History quét toàn bảng & không phân trang.** `EXPLAIN QUERY PLAN` → `SCAN orders`. Trên bản sao DB (117.431 đơn): 10,68 ms/truy vấn, trả TB 235 đơn/user (`results/optimization/bench_index.md`). Ở 67 lần/s ⇒ ~0,72 s thời gian DB mỗi giây.
2. **Một kết nối SQLite duy nhất, tuần tự hóa.** node-sqlite3 xếp hàng mọi truy vấn trên 1 connection, nên `Browse Products` (bảng 5 dòng) cũng chậm từ 15,8 → 160 ms — nó phải **chờ sau** các lần quét `orders` và các `INSERT`/`UPDATE` của checkout & login.
   Bằng chứng đối chứng: `Add to Cart`/`View Cart` không chạm DB nên chỉ 26–27 ms TB (chậm do event loop), trong khi mọi request có truy vấn DB đều 75–90 ms TB.
3. **Payload tăng dần:** response my-orders 19 KB → 35 KB (JSON serialize trên event loop); giỏ hàng không bao giờ được xóa (B2/B3) → `GET /api/cart` 8,8 KB → 15,6 KB.
4. **Login luôn ghi DB** (`UPDATE users SET login_attempts=0...` kể cả khi đăng nhập đúng) và `users.email` không có index (`SCAN users`).
5. **Cùng truy vấn, khác kích thước bảng:** Load chính thức (bảng orders 1.500 → 2.510 dòng) Order History TB 2,0 ms; trên bản sao DB 117.431 dòng, riêng truy vấn SQL đã mất 10,68 ms (`bench_index.md`) – tăng theo số dòng, trong khi các API không chạm bảng orders giữ ~1,1–1,4 ms.

## 6. Bẫy diễn giải số liệu (dùng cho Task 2 – đối chiếu phân tích của AI)

| Cách đọc dễ sai | Giá trị đúng trong `.jtl` |
|---|---|
| "Breakpoint test có 70% lỗi → hệ thống hỏng 70% giao dịch" | **99,9%** lỗi nằm ở `01 Login` (538.783/539.398). Connection refused trả về tức thì + `startnextloop` + think ~0 ⇒ thread lặp login liên tục. Các bước 02–08 chỉ lỗi 0,06–0,97%. |
| "Cuối test đạt 2.500 RPS – cao hơn bậc 400 VU" | Phần lớn là request hỏng nhanh; checkout thành công chỉ ~61 đơn/s. |
| "Lỗi do khóa tài khoản (message assertion ghi 403)" | responseCode là `Non HTTP response code: ...ConnectException`; `post_run_db.txt`: 0 user bị khóa. Message gây hiểu nhầm là do assertion AI sinh ra (đã sửa). |
| "Soak 0% lỗi, p95 244 ms → ổn định" | p95 theo phút tăng 47 → 393 ms, RPS giảm 599 → 494: hệ thống **đang suy giảm**. |
| "Stress 500 VU đạt ~735 RPS là năng lực tối đa" | Đó là giới hạn **của kịch bản**, không phải của hệ thống; biến thể breakpoint cho thấy ~950 RPS. |
| "CPU node vượt 100% là lỗi đo" | Có thể >100%: sqlite3 chạy trên libuv threadpool; nhưng phần JS chỉ 1 luồng. |

## 7. Đề xuất tối ưu & đánh giá khả thi

| # | Đề xuất | Khả thi? | Căn cứ |
|---|---|---|---|
| O1 | `CREATE INDEX idx_orders_user_id ON orders(user_id, id DESC)` | **Khả thi – đã kiểm chứng** | Bản sao DB: 10,68 → 1,20 ms/truy vấn (**8,9×**); plan đổi thành `SEARCH ... USING INDEX` |
| O2 | Phân trang my-orders (`LIMIT 20 OFFSET ?`) | **Khả thi – đã kiểm chứng** | 0,56 ms không index; **0,18 ms** khi có index (**59×**), payload giảm ~12× (235 → 20 đơn) |
| O3 | `CREATE INDEX idx_users_email ON users(email)` (UNIQUE sau khi dọn trùng) | Khả thi, lợi ích nhỏ ở 502 user | `SCAN users` → `SEARCH ... USING INDEX`; còn sửa luôn bug cho phép email trùng |
| O4 | Chỉ `UPDATE users` khi `login_attempts>0` hoặc đang có `locked_until` | Khả thi | Loại 1 lệnh ghi/1 login thành công (≈68 ghi/s trong soak) |
| O5 | Xóa giỏ sau checkout / lưu giỏ vào DB | Khả thi, **bắt buộc** (bug FR-08) | View Cart 8,8 → 15,6 KB trong 15 phút; RAM node tăng |
| O6 | Bật `PRAGMA journal_mode=WAL; synchronous=NORMAL` | Khả thi nhưng **lợi ích hạn chế** | WAL cho phép đọc song song với ghi *giữa các connection*; backend chỉ có 1 connection node-sqlite3 (tuần tự hóa) nên phải kèm O7 mới phát huy. Chưa đo – cần A/B |
| O7 | Pool đọc riêng (nhiều `sqlite3.Database` read-only) hoặc chuyển sang `better-sqlite3` | Khả thi, công sức vừa | Giải quyết đúng nguyên nhân §5.2 (hàng đợi 1 connection) |
| O8 | Cluster mode / PM2 nhiều worker | Khả thi một phần | Tăng CPU cho JWT/JSON, nhưng **giỏ hàng in-memory sẽ hỏng** (mỗi worker 1 `userCarts`) → phải làm O5 trước |
| O9 | Tăng backlog `app.listen(PORT, '0.0.0.0', 2048)` | Khả thi nhưng chỉ dời điểm gãy | Giảm connection refused khi quá tải, không tăng throughput |
| O10 | "Thêm Redis cache cho order history" | Không cần thiết / quá mức | Sau O1+O2 truy vấn còn 0,18 ms; cache thêm độ phức tạp & sai lệch dữ liệu ngay sau checkout |
| O11 | "Thêm connection pool cho SQLite như PostgreSQL" | **Diễn đạt sai bản chất** nếu hiểu là pool ghi | SQLite chỉ 1 writer tại một thời điểm; pool chỉ có ích cho đọc (= O7) |

**Ưu tiên:** O1 + O2 + O5 (rẻ, đã đo được) → O4 → O7 (+O6) → O8.

## 8. Issue đề xuất log lên GitHub

| Issue | Loại | Bằng chứng |
|---|---|---|
| Order History chậm dần theo số đơn (full scan, không phân trang) | Performance | §4, §5, `bench_index.md` |
| Giỏ hàng không xóa sau checkout, tăng vô hạn trong RAM | Functional + Performance | §4 bảng bytes View Cart |
| Login sai: +2/lần, khóa 180s (spec +1, ≥3, 30s) | Functional | `curl` 3 lần: 401, 401, 403 |
| Connection refused khi > ~1.000 VU đồng thời | Performance | §3, `results/23120317_Stress_20261119_breakpoint` |
| `GET /api/orders/:id` không cần auth (IDOR) | Security | `curl localhost:3000/api/orders/1550` trả đơn của user 51 |

## 9. Ghi chú review: những chỗ AI (Claude) làm sai trong quá trình này

1. Test plan bản đầu dùng **JSR223 Groovy** để tính tiền → lỗi `Unsupported class file major version 69` trên JDK 25 (Groovy đi kèm JMeter 5.6.3 không hỗ trợ). Sửa: dùng `__jexl3`.
2. Stress thiết kế ban đầu (tối đa 500 VU, think 0,3–1s) **không tìm được điểm gãy** – AI ước lượng năng lực Node+SQLite quá thấp. Sửa: thêm biến thể breakpoint 400→2000 VU.
3. Message assertion AI viết gán mọi status ≠ 200 thành "403 = tài khoản bị khóa" → bảng phân loại lỗi gây hiểu nhầm. Sửa message.
4. Script giám sát dùng định dạng `N1` (có dấu phân cách nghìn `1,065.9`) làm vỡ CSV và giả định chu kỳ 5s (thực tế ~14s khi máy tải nặng) → con số "CPU TB 113%" báo cáo ban đầu cho Stress là **sai**; giá trị đúng 54% TB / 90% đỉnh. Sửa format `F1` và tính theo timestamp thật.
5. Ghi chú ban đầu "CPU 100% = bão hòa event loop" chưa chính xác (sqlite3 dùng threadpool).
6. Soak mặc định ban đầu (150 VU, think 1–2s ≈ 100 RPS) chỉ ~10% năng lực – không có ý nghĩa endurance; chỉnh thành 400 VU/think 0,3–1s sau khi có số liệu Stress.
