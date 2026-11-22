---
name: perf-testing-workflow
description: Thiết kế, chạy và phân tích performance test (Load / Stress / Spike / Soak) bằng JMeter cho một nhóm endpoint REST API, rồi để AI phân tích log .jtl và tự review lại các chỗ diễn giải sai. Dùng khi người dùng yêu cầu kiểm thử hiệu năng một workflow/endpoint mới của SUT (vd. eshop-sut), cần test plan đặt tên {StudentID}_{ScenarioType}_{YYYYMMDD}, dữ liệu CSV, .jtl + HTML report, ngưỡng chịu tải, hoặc cổng hồi quy p95.
---

# Performance testing workflow (JMeter + AI log analysis)

Skill này đóng gói quy trình đã dùng cho Workflow 5 của HW05. Áp dụng lại cho **một nhóm endpoint bất kỳ**: đi tuần tự từng bước, **không** gộp thành một lệnh "chạy load test rồi đánh giá". Sau mỗi bước, báo cho người dùng biết đã làm gì và có số liệu gì.

Các script nằm trong `../../scripts/` (tương đối với file này):

| Script | Vai trò |
|---|---|
| `prepare_data.js` | Đăng ký user qua API, tạo đơn lịch sử, ghi `data/users.csv`, `data/products.csv` |
| `reset_lockout.js` | Reset `login_attempts/locked_until` trực tiếp trong SQLite giữa các lần chạy |
| `gen_testplans.py` | Sinh `.jmx` Load/Stress/Spike/Soak – sửa hàm `workflow()` cho endpoint mới |
| `run_scenario.sh` | Reset lockout → JMeter CLI → `.jtl` + `html-report/` + RAM/CPU process SUT |
| `analyze_jtl.py` | Bảng thống kê theo label, timeline, phân loại lỗi, tài nguyên → `analysis.md` |
| `bench_index.js` | Kiểm chứng đề xuất index/LIMIT trên **bản sao** DB |
| `perf_gate.py` | Cổng hồi quy p95 so với baseline (ngưỡng kép % + ms) |
| `plot_issue_charts.py` | Biểu đồ minh họa cho GitHub Issues |

## Bước 1 – Khảo sát endpoint (đọc code, không đoán)
1. Đọc `api_specification.md` **và** mã nguồn route thật (`server.js`). Với mỗi endpoint ghi: method, auth, body, mã trả về, truy vấn SQL, có ghi DB không, có index không (`EXPLAIN QUERY PLAN`), có phân trang không, có trạng thái in-memory không.
2. Xếp endpoint vào 3 nhóm: auth-heavy / read-heavy / transactional.
3. Tìm các hành vi ảnh hưởng tới test: lockout (đếm số lần sai, thời gian khóa – **thử bằng curl**, đừng tin spec), DB có bị reset khi khởi động không, kiểu dữ liệu không nhất quán (vd. `price` lúc number lúc string).
4. Ghi ra `docs/01_API_Survey.md` kèm danh sách bug ứng viên.

## Bước 2 – Dữ liệu
- Khởi động SUT **trước**, rồi chạy `prepare_data.js` (nếu SUT seed lại DB khi start).
- Số account ≥ số VU tối đa, mỗi VU một account để không kích hoạt lockout chéo.
- Seed dữ liệu lịch sử cố định (vd. 3 đơn/user) để mọi lần chạy bắt đầu cùng kích thước bảng. **Ghi số dòng trước/sau mỗi lần chạy** (`pre_run_db.txt`/`post_run_db.txt`).

## Bước 3 – Sinh test plan
1. Sửa `workflow()` trong `gen_testplans.py`: mỗi bước là một `http(...)`, kèm:
   - assertion **status** + assertion **JSONPath nội dung** (vd. `$.orderId` tồn tại; id sai vẫn 200 `{}` thì phải assert `$.id`),
   - extractor cho biến dùng ở bước sau,
   - message assertion **trung tính** ("HTTP status khác mong đợi; Non HTTP = lỗi kết nối"), không gán sẵn nguyên nhân.
2. Tính toán trong body dùng `__jexl3` (không dùng JSR223 Groovy nếu JDK ≥ 25 – Groovy đi kèm JMeter 5.6.3 không chạy).
3. Mọi tham số tải là property `${__P(...)}` để chỉnh bằng `-J` mà không sửa file.
4. Mỗi kịch bản một listener khác loại: Load = Summary Report, Stress = Aggregate Report, Spike = View Results Tree.
5. `python gen_testplans.py --student-id <MSSV> --date <YYYYMMDD>`.

## Bước 4 – Chạy
1. Smoke 30 s (`-Jusers=3 -Jduration=30`) – yêu cầu 0% lỗi ở mọi bước trước khi chạy thật.
2. `bash run_scenario.sh Load|Stress|Spike`. Stress theo thiết kế **chưa gãy** thì chạy biến thể breakpoint: `RUN_TAG=breakpoint bash run_scenario.sh Stress -Jstep_users=400 -Jthink_min=0 -Jthink_range=200`.
3. Soak ở ~65–70% throughput tối đa đo được, 10–15 phút: `bash run_scenario.sh Soak -Jusers=<N>`.
4. Ghi lại thời điểm bắt đầu/kết thúc để đối chiếu với video và ảnh Task Manager.

## Bước 5 – Phân tích (người + AI)
1. `python analyze_jtl.py <jtl> --window 30 --resource <dir>/node_resource.csv > <dir>/analysis.md`.
2. Xác định: ngưỡng SLA từng bậc, **điểm bão hòa** (RPS ngừng tăng), **điểm gãy** (lỗi > 1%), xu hướng soak (p95 theo phút), trần RAM.
3. Giao cho **một AI phiên mới, không có ngữ cảnh** phân tích `analysis.md` theo 3 câu hỏi riêng (kết quả + ngưỡng; điểm gãy + nguyên nhân; đề xuất tối ưu). Lưu nguyên văn prompt và output.
4. Review output AI theo checklist bẫy diễn giải:
   - Error % tổng bị khuếch đại bởi "bão lỗi" (lỗi kết nối trả về tức thì + `startnextloop`)? → xem lỗi theo label.
   - RPS cao ở cuối quá tải là request hỏng nhanh? → tính goodput (chỉ request thành công).
   - Có trộn các lần chạy khác ngày / khác kích thước DB? → đọc `pre_run_db.txt` và `timeStamp`.
   - Có tự đặt SLA mới sau khi xem kết quả?
   - Quy kết nguyên nhân có được tách theo bước có/không chạm DB?
   - Con số lợi ích tối ưu ("×3", "+30%") có số đo không? Không có = đánh dấu chưa kiểm chứng.
5. Kiểm chứng đề xuất tối ưu bằng đo thật trên bản sao (`bench_index.js`) trước khi kết luận "feasible".

## Bước 6 – Báo cáo & theo dõi liên tục
- Issue: mỗi bug một issue có bước tái hiện + số liệu + ảnh (`plot_issue_charts.py`).
- Tạo baseline: `perf_gate.py baseline <jtl> -o ci/baseline.json`; kiểm tra: `perf_gate.py check <jtl> -b ci/baseline.json` (ngưỡng kép +20% **và** +5 ms; chỉ dùng % sẽ báo động giả khi p95 nền vài ms).
- Commit sau mỗi bước (khảo sát, dữ liệu, từng test plan, kết quả, phân tích).

## Những điều không được làm
- Không bịa hoặc chỉnh sửa `.jtl`, ảnh tài nguyên, video – đó là bằng chứng chấm điểm.
- Không restart SUT giữa các kịch bản nếu SUT reset DB khi khởi động (sẽ mất user đã seed).
- Không sửa DB đang chạy để thử tối ưu – luôn làm trên bản sao.
