# Task 2 – Review phân tích của AI (human review)

> Đầu vào: `ai_analysis_prompt.md` (prompt), `ai_analysis_output_raw.md` (output nguyên văn).
> Mọi "giá trị đúng" dưới đây được lấy từ file gốc: `.jtl`, `console.txt`, `pre_run_db.txt`/`post_run_db.txt`, `node_resource.csv`, `bench_index.md`. Cột **Nguồn** chỉ rõ file.

## 1. Tổng quan

AI đọc **đúng phần lớn số liệu thống kê** (p95, RPS, error rate, số đơn đều khớp `analysis.md`). Nó cũng tự phát hiện vài điểm tốt:
- Nhãn "403 = khóa tài khoản" là nhãn assertion, không phải lỗi thật.
- RPS ~2.500 ở cuối test breakpoint là số ảo do "retry storm".
- **Response login trả cả mật khẩu** – điểm này nhóm đã bỏ sót khi khảo sát (xem §4).

Các sai sót của AI nằm ở **diễn giải ngữ cảnh** và **quy kết nguyên nhân**, cùng một số đề xuất tối ưu đưa ra con số lợi ích không có căn cứ đo.

## 2. Các chỗ AI hiểu sai / diễn giải sai số liệu

| # | AI nói | Giá trị đúng | Nguồn | Vì sao AI sai |
|---|---|---|---|---|
| M1 | "Dữ liệu không được reset giữa các lần chạy: 1.500 → 2.510 (Load) → 26.441 (Stress) → 28.163 (Spike) → **55.973 (Stress mạnh) → 117.431 (Soak)**" – xem như một chuỗi chạy liên tục | Có **2 phiên chạy độc lập**. Phiên chính thức 22/11 (Load → Stress → Spike) bắt đầu từ DB sạch 1.500 đơn. Stress mạnh và Soak thuộc phiên khảo sát 19/11: Stress mạnh bắt đầu với **28.275** đơn (không phải 28.163), Soak bắt đầu với **56.984** | `results/23120317_Stress_20261119_breakpoint/pre_run_db.txt`; `results/23120317_Soak_20261119/pre_run_db.txt`; `results/23120317_Load_20261119/pre_run_db.txt` (1.500) | AI nối các con số "số đơn hiện có" theo thứ tự tên file, không kiểm tra thời điểm chạy (cột `timeStamp` trong `.jtl`: 19/11 so với 22/11). Prompt cũng không nói rõ các lần chạy thuộc 2 phiên khác nhau – một phần lỗi do prompt |
| M2 | "**Điểm nghẽn chính là CPU của event loop node**"; "hai bước giỏ hàng không chạm DB vẫn p95 ~92 ms → cả event loop bị nghẽn" | Trong soak, các bước **không chạm DB** (06, 07) có avg **26–27 ms**. Các bước **có DB** (01–05, 08) có avg **75–90 ms**, tức ~3× chậm hơn. Phần lớn thời gian chờ nằm ở **hàng đợi của 1 kết nối SQLite**, không phải event loop. Event loop chỉ chiếm phần nhỏ hơn | `results/23120317_Soak_20261119/analysis.md` §1 (tính từ `.jtl`) | AI chỉ nhìn p95 của bước giỏ hàng (92 ms, khác 0) để kết luận event loop nghẽn, mà không so sánh với các bước có DB. Nó cũng không xét đến việc node-sqlite3 tuần tự hóa mọi truy vấn trên 1 connection |
| M3 | "CPU node đạt 118–126% (≈100% luồng JS + phần threadpool) → event loop đã đầy" | Chỉ có **tổng CPU-time** của process, không tách được luồng JS và threadpool. Không thể suy ra event loop đạt 100% từ dữ liệu này. Ở Stress chính thức, CPU **trung bình** chỉ 60% (đỉnh 118% là 1 khoảng giữa 2 mẫu) | `results/23120317_Stress_20261119/node_resource.csv`, `analysis.md` §4 | Diễn giải quá mức một chỉ số tổng hợp. Muốn kết luận event loop bão hòa cần đo event-loop lag (`perf_hooks.monitorEventLoopDelay`) – chính AI cũng gợi ý điều này ở 3.10 |
| M4 | "Soak **không đạt** p95 tổng (244 ms > 200 ms)" | Ngưỡng SLA đã thiết kế trước khi chạy là **p95 ≤ 500 ms** (`02_Test_Design.md` §4). Theo ngưỡng này, p95 tổng soak 244 ms **đạt**. Điểm không đạt thật sự là **độ trôi** (p95 theo phút 47 → 393 ms) | `docs/02_Test_Design.md` §4; `results/23120317_Soak_20261119/analysis.md` §2 | AI tự đặt SLO mới (200 ms) rồi chấm theo đó, tức "dời cột gôn" sau khi đã thấy kết quả. AI không được cung cấp SLA đã định trước (thiếu sót của prompt) |
| M5 | "Giỏ hàng là **nguyên nhân chính** của mức tăng ~16 MB RAM trong 15 phút" | Không có số đo nào tách riêng bộ nhớ của `userCarts`. RAM soak chỉ tăng 109 → 125 MB, và còn có object cache của V8, buffer response lớn hơn… Kết luận chỉ là **giả thuyết hợp lý**, không phải kết quả đo | `node_resource.csv` chỉ có Working Set tổng | AI biến một suy luận từ code thành khẳng định. Muốn chứng minh cần heap snapshot hoặc đếm `userCarts` |
| M6 | "Response View Order History tăng từ ~17 KB lên ~37 KB" | Trung bình phút đầu **18.291 B** → phút cuối **35.707 B** (min 15.518, max 40.213) | Tính từ `results/23120317_Soak_20261119/23120317_Soak_20261119.jtl` cột `bytes` của label 02 | Sai lệch nhỏ: AI lấy giá trị gần min/max thay vì trung bình. Không ảnh hưởng kết luận |
| M7 | Phần chú thích phân loại lỗi "nhãn mặc định của assertion" | Đúng là không có 403. Tuy nhiên nhãn đó **không phải mặc định của JMeter** mà là *custom message* do AI (Claude, bản sinh test plan đầu tiên) tự viết sai, nhóm đã sửa trong `gen_testplans.py` sau lần chạy breakpoint | `scripts/gen_testplans.py` (hàm `assert_code`) | AI không biết lịch sử file; chi tiết nhỏ, nhưng cho thấy AI suy đoán xuất xứ dữ liệu |

### Những chỗ AI **đúng** (đã kiểm chứng)

| AI nói | Kiểm chứng |
|---|---|
| Lỗi đầu tiên ở **1.094 VU, 4,5%** | `console.txt`: `Active: 1094 … Err: 1186 (4.54%)` ✔ |
| Login chịu gần hết lỗi vì là bước **mở kết nối TCP mới** | Load `.jtl`: cột `Connect` > 0 ở **805/1.053** mẫu Login, và **0** ở mọi bước 02–08 ✔. Nguyên nhân là test plan đặt `same_user_on_next_iteration=false` (mỗi vòng = khách mới = kết nối mới) |
| RPS ~2.500 là ảo; goodput sụp còn ~50 RPS | Phù hợp với `analysis.md` breakpoint: 99,9% lỗi nằm ở Login ✔ |
| Spike thiết kế **quá nhẹ** (~200 RPS < 30% năng lực) | Đúng – là hạn chế thiết kế hợp lệ, ghi nhận để cải tiến |

## 3. Đánh giá đề xuất tối ưu: khả thi (feasible) hay ảo (hallucinated)

| # | Đề xuất của AI | Phân loại | Lý do |
|---|---|---|---|
| 3.1 | Index `orders(user_id,id DESC)`, `users(email)` | **Feasible – đã đo** | `bench_index.md`: 10,68 → 1,20 ms; EXPLAIN đổi `SCAN` → `SEARCH USING INDEX`. Con số AI trích đúng |
| 3.1b | Index `coupon_usage(coupon_id,user_id)` | Feasible nhưng **lạc đề** | Workflow 5 không gọi coupon; không có số đo nào liên quan |
| 3.1c | `UNIQUE` index trên email | Feasible **có điều kiện** | `/api/register` hiện cho phép email trùng → phải dọn dữ liệu trùng trước, nếu không `CREATE UNIQUE INDEX` sẽ lỗi |
| 3.2 | Phân trang `LIMIT 20` + chọn cột | **Feasible – đã đo** | 0,18 ms (59×). Tuy nhiên câu "p95 soak trở về vài chục ms" là **ước đoán chưa đo** |
| 3.2b | Login không trả `user` có mật khẩu | **Feasible – xác nhận thật** | `curl` login trả `"password":"Test1234!"` (bug bảo mật mới, xem §4) |
| 3.3 | WAL + PRAGMA, "ghi nhanh hơn vài lần" | Feasible, nhưng **lợi ích bị phóng đại / chưa đo** | Backend chỉ có 1 connection node-sqlite3 nên lợi ích "đọc không chặn ghi" của WAL gần như không phát huy khi chưa có nhiều connection (3.7). "Nhanh hơn vài lần" không có số đo |
| 3.3b | "WAL là **điều kiện bắt buộc** để chạy cluster với SQLite" | **Hallucinated (khẳng định sai)** | SQLite ở chế độ rollback journal vẫn hỗ trợ nhiều process truy cập (khóa file + `busy_timeout`). WAL là *khuyến nghị*, không bắt buộc |
| 3.4 | Bỏ `UPDATE` thừa khi login | **Feasible** | Đúng logic code: mỗi login thành công đều `UPDATE`; workflow giảm từ 2 → 1 lệnh ghi |
| 3.4b | Prepared statement "tiết kiệm 5–15%" | Feasible, **con số bịa** | Không có số đo; truy vấn hiện tại đã dùng tham số `?` |
| 3.5 | Cache sản phẩm, "+20–40% năng lực" | Feasible, **con số bịa** | Products đã chỉ ~1,2 ms ở tải thấp. Phần chậm trong soak là do xếp hàng sau truy vấn orders, nên sửa 3.1/3.2 trước sẽ hiệu quả hơn. 20–40% không có căn cứ |
| 3.5b | Sửa SQL injection ở search (`LIKE ?`) | **Feasible** | Đúng (đã ghi nhận ở khảo sát API, B6) |
| 3.6 | Cluster 4–6 worker, "×3–4 RPS, điểm gãy lên nhiều nghìn VU" | Feasible về kỹ thuật, **con số không có căn cứ** | Mâu thuẫn với chính nhận định 2.2.6 của AI (JMeter chạy chung máy, tranh CPU). SQLite vẫn 1 writer. Không thể ×3–4 trên cùng laptop. AI có nêu đúng điều kiện tiên quyết: chuyển `userCarts` khỏi RAM |
| 3.7 | `better-sqlite3` "nhanh hơn 2–5×" | **Có rủi ro / con số bịa** | API **đồng bộ** chặn event loop. Theo chính nhận định của AI, event loop là nút thắt, nên đổi sang API đồng bộ có thể làm tệ hơn. Chỉ hợp lý khi đi kèm cluster |
| 3.7b | PostgreSQL + `pg.Pool` | Feasible dài hạn, **quá phạm vi** | Thay toàn bộ tầng dữ liệu của SUT – không phù hợp đề xuất cho bài kiểm thử |
| 3.8 | Sửa rò rỉ giỏ hàng | **Feasible, bắt buộc** | Vi phạm FR-08; View Cart 8,8 → 15,6 KB trong soak |
| 3.9 | Backlog 2048, keep-alive, load shedding 503, rate limit login | Feasible | Hợp lý cho hành vi quá tải. Backlog chỉ dời điểm gãy, không tăng throughput. Nguyên nhân "backlog 511 đầy → RST" là **giả thuyết chưa kiểm chứng** (chưa đo `netstat`) |
| 3.9b | `express.json()` thay `body-parser` để tăng hiệu năng | **Không có tác dụng đáng kể** | `express.json()` chính là body-parser được tích hợp sẵn |
| 3.10 | Bật "Same user on each iteration" để tái sử dụng kết nối | **Sai mục tiêu kiểm thử** | Mỗi vòng lặp mô phỏng **một khách hàng khác** (CSV 500 user), nên kết nối mới là hành vi thực tế. Bật cờ này làm test "dễ" hơn thực tế và che mất vấn đề accept backlog |
| 3.10b | Backoff khi Login lỗi, reset dữ liệu trước mỗi lần chạy, tách máy JMeter | **Feasible** | Đúng, ghi nhận làm cải tiến quy trình (phiên chính thức 22/11 đã reset DB) |

**Tóm tắt:** 9 đề xuất feasible (2 đã đo được lợi ích: index, phân trang). 1 khẳng định sai (WAL bắt buộc cho cluster). 5 con số lợi ích bịa không có số đo (WAL "vài lần", prepared "5–15%", cache "20–40%", cluster "×3–4", better-sqlite3 "2–5×"). 2 đề xuất sai mục tiêu hoặc không tác dụng (same-user, express.json).

## 4. Phát hiện mới nhờ AI (sau khi kiểm chứng)

- **Login trả nguyên bản ghi user gồm mật khẩu plaintext.** Kiểm chứng: `curl -d '{"email":"test@eshop.com","password":"Test1234!"}' localhost:3000/api/login` → `"user":{… "password":"Test1234!" …}`. Đã bổ sung thành Issue 6 trong `docs/05_GitHub_Issues.md`.

## 5. Vì sao AI sai (nguyên nhân)

1. **Thiếu ngữ cảnh trong prompt:** không nói 2 phiên chạy khác ngày, không đưa SLA đã định → dẫn tới M1, M4.
2. **Suy luận từ code thay vì từ số đo:** M2, M5, 3.3b – AI hiểu Node/SQLite "theo sách" rồi gán vào dữ liệu mà không đối chiếu số liệu theo từng bước.
3. **Thói quen đưa con số lợi ích "cho đẹp":** các hệ số ×2–5, 20–40% không có nguồn. Đây là hallucination điển hình khi được hỏi "lợi ích kỳ vọng".
4. **Không tự nhất quán:** khẳng định event loop là nút thắt nhưng lại đề xuất `better-sqlite3` đồng bộ, và đề xuất cluster ×3–4 dù đã nêu JMeter tranh CPU trên cùng máy.
