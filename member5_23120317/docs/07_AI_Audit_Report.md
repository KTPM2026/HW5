# 07 – AI Audit Report (Thành viên 5 – Nguyễn Đức Phát, 23120317)

**Tuyên bố:** I use AI tools for the following tasks.

| Công cụ | Phiên bản | Vai trò |
|---|---|---|
| Claude Code (CLI, Windows) | model Claude Opus 5.5 (`claude-opus-5-5`), effort medium | Trợ lý chính: khảo sát API, sinh dữ liệu và test plan, chạy JMeter CLI, phân tích .jtl, viết tài liệu, thao tác Git/GitHub |
| Claude Code – subagent `general-purpose` | Claude Opus 5.5, phiên mới không kế thừa ngữ cảnh | AI phân tích độc lập cho Task 2 |
| Apache JMeter 5.6.3, Task Manager, dxdiag | – | Công cụ kiểm thử / giám sát (không phải AI) |

> Phiên Claude Code là một phiên **agentic** dài (AI tự gọi tool: đọc file, chạy lệnh, ghi file). Bảng dưới liệt kê **nguyên văn mọi prompt** của sinh viên và tóm tắt output tương ứng. Transcript đầy đủ (mọi lệnh và kết quả tool) được xuất bằng lệnh `/export` của Claude Code và nộp kèm: `docs/ai_session_transcript.txt`.
> Giờ là giờ địa phương GMT+7, ước lượng theo timestamp file/commit tạo ra trong lượt đó.

## 1. Phiên Claude Code chính

| # | Ngày giờ | Prompt của sinh viên (nguyên văn) | Output của AI (tóm tắt) | Sinh viên review / chỉnh sửa |
|---|---|---|---|---|
| 1 | 19/11/2026 ~21:35 | "Đọc HW05, tôi là thành viên 5, chịu trách nhiệm về các phần sau: Người 5 Workflow 5 Login → View Order History → Browse Products → Add to Cart → Checkout Truy xuất lịch sử đơn hàng và tạo đơn mới" + dán danh sách 8 nhiệm vụ (khảo sát API đăng nhập / Order History / sản phẩm / Cart / Checkout, chuẩn bị dữ liệu, thiết kế & chạy 3 kịch bản, phân tích & đề xuất tối ưu) | Đọc PDF đề, clone eshop-sut, đọc `server.js`/`database.js`. Viết `docs/01_API_Survey.md` (9 bug ứng viên). Viết `prepare_data.js` (500 user, 1.500 đơn), `reset_lockout.js`, `gen_testplans.py`. Thử lockout bằng curl: 401, 401, 403 | Xác nhận lockout sai spec bằng output curl thật |
| 2 | 19/11 ~22:58 | "Máy tôi có Jmeter rồi, ở D/Tools" | Dừng tải JMeter, dùng `D:/Tools/apache-jmeter-5.6.3`. Smoke test **lỗi**: JSR223 Groovy `Unsupported class file major version 69` (JDK 25) → AI thay bằng `__jexl3`. Smoke lại: 8/8 bước pass. Viết `run_scenario.sh`, chạy Load / Stress / Spike lần 1 | Ghi nhận lỗi của AI (Groovy trên JDK 25) |
| 3 | 19/11 ~23:05 | "1. MSSV: 23120317, tên: Nguyễn Đức Phát. 2. Có bắt buộc tôi phải tự chạy không, hay bạn chạy cho tôi được ?" | Sinh lại test plan tên `23120317_*`. Giải thích phần bắt buộc sinh viên tự làm (video giọng thật, ảnh tài nguyên, dxdiag) theo mục 11 của đề | – |
| 4 | 19/11 ~23:25 | "cập nhật cho tôi đi" | Báo kết quả vòng 1 (0% lỗi, chưa gãy). Chạy Stress breakpoint 400 → 2000 VU: tìm ra điểm gãy ~1.100–1.200 VU. AI phát hiện chính message assertion do nó viết ("403 = khóa tài khoản") gây hiểu nhầm → sửa. Chạy Soak 15 phút | Kiểm tra `post_run_db.txt`: 0 user bị khóa → xác nhận lỗi là lỗi kết nối |
| 5 | 19/11 ~23:55 | "phần bạn xong chưa, hãy đưa ra hướng dẫn chi tiết các bước làm phần của tôi đi." | Phân tích Soak (p95 47 → 393 ms), đo index trên bản sao DB (`bench_index.js`: 8,9× / 59×). Viết `03_Results_Analysis.md`, `04_Huong_dan_thuc_hien.md`. AI tự đính chính 2 số sai đã báo trước đó (CPU "113%" do lỗi parse; "95%" lỗi Login → đúng là 99,9%) | Đọc lại, đối chiếu số trong `analysis.md` |
| 6 | 22/11 ~14:55 | "làm phần quay video này đơn giản hơn đi, nó đang khá phức tạp so với đề bài yêu cầu" | Viết `record_demo.sh` (1 lệnh chạy Load → Stress → Spike), rút gọn hướng dẫn quay | Sinh viên tự quay video, tự thuyết minh |
| 7 | 22/11 ~15:30 | "ok tôi làm xong bước 2 trong file rồi, các file cần có tôi đã lưu ở root, làm cho tôi từ bước 3 đi." | Phân tích 3 lần chạy chính thức, cắt khung hình video làm ảnh tài nguyên, cập nhật báo cáo. Giao Task 2 cho subagent độc lập, review output (7 diễn giải sai). Soạn 6 issue. Khởi tạo Git, commit từng bước | Kiểm tra mốc giờ video so với `.jtl` (lệch ~30 s) |
| 8 | 22/11 ~15:40 | "đặt tiêu đề video là gì" | Đề xuất tiêu đề và mô tả YouTube có mốc thời gian | Sinh viên tự chỉnh mốc thời gian |
| 9 | 22/11 ~15:42 | "tôi mở jmeter rồi, hoặc bạn tự mở rồi chụp report giúp tôi, tôi cấp toàn quyền." | Mở JMeter GUI bằng bản sao test plan trỏ sẵn `.jtl`, chụp Summary Report / Aggregate Report / View Results Tree bằng script PowerShell | Ảnh khớp số liệu `.jtl` (8.268 / 193.203 sample) |
| 10 | 22/11 ~15:55 | "https://github.com/KTPM2026/HW5 https://youtu.be/Y2VKcs27d3Y" | Repo chỉ có quyền READ → fork, đặt bài vào `member5_23120317/`, mở PR #1. Vẽ biểu đồ từ `.jtl`, đăng issue #2–#7. Viết README có link video | – |
| 11 | 22/11 ~16:10 | "ok làm đi" | Task 3 (`perf_gate.py` + CI mẫu, thử trên số liệu thật), Agent Skill, AI Audit Report (file này), bản nháp AI Critique | Sinh viên đọc, chỉnh sửa và chịu trách nhiệm phần Critique |

## 2. Phiên subagent – Task 2 (AI phân tích độc lập)

| Ngày giờ | Prompt | Output | Review |
|---|---|---|---|
| 22/11/2026 ~15:35 | Nguyên văn: `docs/task2/ai_analysis_prompt.md` | Nguyên văn: `docs/task2/ai_analysis_output_raw.md` | `docs/task2/ai_analysis_review.md`: 7 chỗ diễn giải sai (có giá trị đúng từ `.jtl`), phân loại 20 đề xuất feasible/hallucinated |

## 3. Tổng hợp lỗi của AI đã phát hiện và sửa

| # | Lỗi | Phát hiện bởi | Sửa |
|---|---|---|---|
| 1 | Test plan dùng JSR223 Groovy, không chạy trên JDK 25 | Smoke test | `__jexl3` |
| 2 | Stress thiết kế ban đầu (500 VU) không tìm được điểm gãy | Kết quả 0% lỗi | Thêm biến thể breakpoint 400→2000 VU |
| 3 | Message assertion gán mọi lỗi là "403 = khóa tài khoản" | Đối chiếu `post_run_db.txt` | Message trung tính |
| 4 | Monitor CPU dùng định dạng `N1` (dấu phẩy hàng nghìn) → CSV vỡ, báo CPU "113%" sai | Đối chiếu số liệu | `F1` + tính theo timestamp thật |
| 5 | Ghi chú "CPU 100% = event loop bão hòa" | Soak CPU > 100% | Giải thích threadpool libuv |
| 6 | Báo "95% lỗi ở Login" (đúng là 99,9%) | Tính lại từ bảng lỗi | Sửa báo cáo |
| 7 | Soak mặc định 150 VU (~10% năng lực) – vô nghĩa cho endurance | Số liệu Stress | 400 VU / ~600 RPS |
| 8 | So sánh 2 lần Load dựa trên file đã bị ghi đè (không còn bằng chứng) | Review trước khi nộp | Thay bằng số `bench_index.md` |
| 9 | Subagent Task 2: 7 diễn giải sai, 5 con số lợi ích bịa | Review thủ công | `ai_analysis_review.md` |
| 10 | CI YAML lỗi cú pháp (`${{ }}` trong flow mapping) | `yaml.safe_load` | Viết lại dạng block |
