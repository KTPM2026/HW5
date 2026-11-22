# AI Audit Report — 5-section Template per Artifact (HW05 – Thành viên 5)

> Theo mẫu **[AI-02] FIT@HCMUS – AI Audit Report** (bản .docx đã điền: `ai-forms/[AI-02] AI Audit Report – 23120317.docx`).

## 1. Student Information

| Field | Value |
|---|---|
| Student name (printed): | Nguyễn Đức Phát |
| Student ID: | 23120317 |
| Class / Cohort: | Nhóm KTPM2026 – Thành viên 5 |
| Assignment ID (e.g., HW#00, HW#02): | HW05 |
| Assignment date: | 22/11/2026 |
| AI tool(s) used: | Claude Code v2.1.329 (CLI, Windows) – model Claude Opus 5.5 (claude-opus-5-5), Anthropic – trợ lý chính, chạy dạng agent (đọc file, chạy lệnh, ghi file); Claude Code subagent `general-purpose` (Claude Opus 5.5) – phiên mới không kế thừa ngữ cảnh, dùng cho Task 2 (AI phân tích .jtl) |
| AI used? | [x] Yes  [ ] No |

## 2. Instructions (đã tuân thủ)

- Mỗi artifact do AI tạo là một hàng. Prompt **nguyên văn** (không diễn giải).
- AI output: trích đoạn chính + vị trí **nguyên văn** trong `docs/ai_session_transcript.txt` (số dòng) hoặc file artifact.
- Verdict: VALID / INVALID / INCOMPLETE; lý do trích ISTQB / tài liệu kỹ thuật / bằng chứng log gốc; cột 5 là bản sửa của sinh viên.
- Prompt log có thời gian: `docs/prompt_log.md` (Appendix A).

## 3. Audit Table — one row per artifact

| # | (1) Prompt + Tool | (2) AI Output | (3) Verdict | (4) Reasoning | (5) Student Fix |
|---:|---|---|---|---|---|
| 1 | **Khảo sát API (docs/01_API_Survey.md)**<br>Tool/Time: Claude Code · ~21:40 19/11/2026<br>Prompt: "Đọc HW05, tôi là thành viên 5, chịu trách nhiệm về các phần sau: Người 5 Workflow 5 Login → View Order History → Browse Products → Add to Cart → Checkout Truy xuất lịch sử đơn hàng và tạo đơn mới […] 1. Khảo sát API đăng nhập. 2. Khảo sát API Order History. 3. Khảo sát API sản phẩm. 4. Khảo sát API Cart. 5. Khảo sát API Checkout. 6. Chuẩn bị dữ liệu tài khoản và đơn hàng. 7. Thiết kế và chạy 3 kịch bản Performance Testing. 8. Phân tích kết quả và đề xuất tối ưu." | Bảng 5 endpoint (auth, SQL, index, phân trang) + 9 bug ứng viên B1–B9 (lockout +2/180 s, giỏ không xóa, full scan orders, IDOR, SQL injection…). Nguyên văn: transcript dòng 10–120; file docs/01_API_Survey.md. | **INCOMPLETE** | Đúng với mã nguồn server.js (đã kiểm chứng lockout bằng curl: 401, 401, 403). Nhưng bỏ sót việc /api/login trả nguyên bản ghi user gồm mật khẩu plaintext – lỗi bảo mật do AI khác phát hiện ở Task 2. ISTQB CTFL v4.0 §2.2.2 (Test types – non-functional/security) và §5.5 (Defect management). | Bổ sung Issue #7 "POST /api/login trả về mật khẩu plaintext" sau khi tự kiểm tra bằng curl (response chứa "password":"Test1234!"). |
| 2 | **Dữ liệu CSV + script (scripts/prepare_data.js, reset_lockout.js, data/*.csv)**<br>Tool/Time: Claude Code · ~22:50 19/11/2026<br>Prompt: "(cùng prompt của Artifact #1 – nhiệm vụ 6 "Chuẩn bị dữ liệu tài khoản và đơn hàng")" | 500 user perf5_user_001..500 (mật khẩu thỏa FR-01), 3 đơn/user = 1.500 đơn, products.csv 10 dòng. Nguyên văn: transcript dòng 10–120; console "users.csv: 500 user (mới tạo 500, đã có 0); đã tạo thêm 1500 đơn hàng lịch sử". | **VALID** | Chạy thật trên SUT; pre_run_db.txt mỗi lần chạy chính thức ghi đúng 1.500 đơn, 0 user bị khóa. Đáp ứng yêu cầu data-driven của đề (CSV parameterization) và CT-PT ch.4 (chuẩn bị dữ liệu kiểm thử). | Không sửa. Bổ sung bước bắt buộc chạy sau khi start server vì database.js DROP/seed DB khi khởi động. |
| 3 | **Test plan JMeter bản đầu (scripts/gen_testplans.py → *.jmx)**<br>Tool/Time: Claude Code · ~23:00 19/11/2026<br>Prompt: "Máy tôi có Jmeter rồi, ở D/Tools" | Smoke test lỗi: "Uncaught Exception BUG! exception in phase 'semantic analysis' in source unit 'Script1.groovy' Unsupported class file major version 69" – bước 05–08 không chạy. Nguyên văn: transcript dòng 121–252. | **INVALID** | AI dùng JSR223 Groovy mà không kiểm tra JDK (25). Groovy đi kèm JMeter 5.6.3 không đọc được class file Java 25. Bằng chứng: jmeter.log của smoke run. Tham chiếu: Apache JMeter User Manual – Component Reference (JSR223 / Functions: __jexl3). | Bỏ JSR223PostProcessor; tính tổng tiền bằng `${__jexl3(${price} * ${quantity})}` trong body Checkout. Smoke lại: 8/8 bước 0% lỗi, đơn hàng tạo đúng tổng tiền. |
| 4 | **Message của Response Assertion**<br>Tool/Time: Claude Code · ~23:28 19/11/2026<br>Prompt: "cập nhật cho tôi đi" | Bảng phân loại lỗi Stress breakpoint: "01 Login \| Non HTTP response code: org.apache.http.conn.HttpHostConnectException \| Sai HTTP status (403 = tài khoản bị khóa / token sai) \| 534586". Nguyên văn: transcript dòng 423–665. | **INVALID** | Message gán sẵn nguyên nhân "403 = khóa tài khoản" cho mọi status ≠ 200, trong khi post_run_db.txt cho thấy 0 user bị khóa – lỗi thật là connection refused. Assertion phải mô tả điều kiện kiểm tra, không đoán nguyên nhân (CT-PT ch.2 – thu thập & diễn giải metric). | Đổi message thành "HTTP status khác mong đợi (401/403 = sai credential/bị khóa/token; Non HTTP = lỗi kết nối/timeout)" trong gen_testplans.py, sinh lại 4 test plan. |
| 5 | **Tham số kịch bản Stress (100→500 VU)**<br>Tool/Time: Claude Code · ~23:00 19/11/2026<br>Prompt: "(cùng prompt của Artifact #1 – nhiệm vụ 7 "Thiết kế và chạy 3 kịch bản")" | Stress 5 bậc × 100 VU, think 0,3–1 s → 0% lỗi, p95 ≤ 35 ms: không tìm được điểm gãy. Nguyên văn: transcript dòng 253–422. | **INCOMPLETE** | Mục tiêu stress test là tìm giới hạn/điểm gãy (ISTQB CT-PT ch.1 – types of performance testing: stress testing). AI ước lượng năng lực Node.js + SQLite quá thấp. | Giữ plan làm Stress "theo thiết kế", thêm biến thể breakpoint `-Jstep_users=400 -Jthink_min=0 -Jthink_range=200` (400→2000 VU): tìm được bão hòa ~900–950 RPS, gãy ~1.100–1.200 VU. |
| 6 | **Tham số Soak mặc định**<br>Tool/Time: Claude Code · ~23:30 19/11/2026<br>Prompt: "cập nhật cho tôi đi" | Soak mặc định 150 VU, think 1–2 s ≈ 100 RPS (khoảng 10% năng lực đo được). Nguyên văn: transcript dòng 423–665. | **INVALID** | Endurance test phải ở mức tải duy trì gần ngưỡng thực tế (CT-PT ch.1 – endurance testing); 10% năng lực không cho thông tin về ngưỡng bền. | Đổi mặc định thành 400 VU, think 0,3–1 s (~600 RPS ≈ 65% throughput tối đa). Kết quả: suy giảm p95 47 → 393 ms trong 15 phút. |
| 7 | **Script giám sát tài nguyên (run_scenario.sh) + số liệu CPU**<br>Tool/Time: Claude Code · ~23:55 19/11/2026<br>Prompt: "phần bạn xong chưa, hãy đưa ra hướng dẫn chi tiết các bước làm phần của tôi đi." | Báo "CPU 113%" cho Stress; node_resource.csv có dòng "23:44:29,113.1,1,065.9" (dấu phẩy hàng nghìn làm vỡ cột). Nguyên văn: transcript dòng 666–766. | **INVALID** | PowerShell format "{2:N1}" chèn dấu phân cách hàng nghìn (Microsoft Docs – Standard numeric format strings, "N" vs "F"); script còn giả định chu kỳ 5 s trong khi thực tế ~14 s khi máy tải nặng. | Đổi sang "{2:F1}"; analyze_jtl.py ghép lại cột thừa và tính CPU theo timestamp thật → Stress CPU TB 54% / đỉnh 90% (không phải 113%). |
| 8 | **Báo cáo phân tích (docs/03_Results_Analysis.md)**<br>Tool/Time: Claude Code · ~00:00 20/11/2026, cập nhật 15:35 22/11/2026<br>Prompt: "ok tôi làm xong bước 2 trong file rồi, các file cần có tôi đã lưu ở root, làm cho tôi từ bước 3 đi." | Bảng tổng hợp 5 kịch bản, nguyên nhân gốc, 11 đề xuất tối ưu, bẫy diễn giải. Nguyên văn: file docs/03_Results_Analysis.md; transcript dòng 1158–1263. | **INCOMPLETE** | Bản đầu ghi "95% lỗi ở Login" (đúng 99,9% = 538.783/539.398) và dựa vào so sánh 2 lần Load mà file .jtl đã bị ghi đè (không còn bằng chứng). Đề yêu cầu mọi kết luận đối chiếu được với .jtl gốc (AI Agreement §11 – Performance results). | Sửa thành 99,9%; thay so sánh mất bằng chứng bằng số đo bench_index.md; cập nhật toàn bộ bảng bằng số của 3 lần chạy chính thức 22/11. |
| 9 | **Task 2 – AI phân tích .jtl (docs/task2/ai_analysis_output_raw.md)**<br>Tool/Time: Claude Code subagent · ~15:35 22/11/2026<br>Prompt: "Nguyên văn đầy đủ: docs/task2/ai_analysis_prompt.md ("Bạn là chuyên gia performance testing… Câu 1… Câu 2… Câu 3…")" | Nguyên văn đầy đủ: docs/task2/ai_analysis_output_raw.md. | **INCOMPLETE** | Đọc đúng thống kê nhưng 7 chỗ diễn giải sai (M1–M7 trong ai_analysis_review.md), ví dụ nối 2 phiên chạy khác ngày thành một chuỗi (pre_run_db.txt: breakpoint bắt đầu 28.275 đơn, không phải 28.163), tự đặt SLA 200 ms sau khi xem kết quả. CT-PT ch.2 (aggregating results) – không trộn kết quả từ điều kiện thử khác nhau. | docs/task2/ai_analysis_review.md: mỗi lỗi có giá trị đúng trích từ .jtl/console.txt/pre_run_db.txt. |
| 10 | **Task 2 – Đề xuất tối ưu của AI**<br>Tool/Time: Claude Code subagent · ~15:35 22/11/2026<br>Prompt: "(Câu 3 trong docs/task2/ai_analysis_prompt.md) "Đề xuất các tối ưu cụ thể cho backend này (ví dụ index database, connection pool, SQLite WAL, cache, cluster...), mỗi đề xuất nêu lợi ích kỳ vọng."" | 20 đề xuất (index, LIMIT, WAL, prepared statement, cache, cluster ×3–4, better-sqlite3 ×2–5…). Nguyên văn: ai_analysis_output_raw.md – Câu 3. | **INCOMPLETE** | 9 feasible (2 đã đo: index 8,9×, LIMIT 59×). "WAL là điều kiện bắt buộc để cluster SQLite" là sai: rollback journal vẫn hỗ trợ nhiều process qua file locking (SQLite docs – File Locking And Concurrency, https://www.sqlite.org/lockingv3.html; WAL https://www.sqlite.org/wal.html). 5 hệ số lợi ích không có phép đo. | Bảng phân loại feasible/hallucinated trong ai_analysis_review.md §3; chỉ giữ đề xuất có số đo trong khuyến nghị ưu tiên (03_Results_Analysis.md §7). |
| 11 | **CI workflow mẫu (ci/perf-regression.yml)**<br>Tool/Time: Claude Code · ~16:05 22/11/2026<br>Prompt: "ok làm đi" | yaml.parser.ParserError: while parsing a flow mapping … expected ',' or '}', but got '{' (dòng 70: `with: { name: perf-${{ github.sha }}, … }`). Nguyên văn: transcript dòng 2116–cuối. | **INVALID** | Biểu thức `${{ }}` đặt trong YAML flow mapping `{ }` làm hỏng cú pháp (YAML 1.2 spec – flow mappings; GitHub Docs – Expressions). | Viết lại `with:` dạng block (name / path: \|). Kiểm tra lại bằng yaml.safe_load: OK, 2 job, 9 step. Chưa chạy thật trên GitHub Actions. |
| 12 | **Cổng hồi quy p95 (scripts/perf_gate.py)**<br>Tool/Time: Claude Code · ~16:00 22/11/2026<br>Prompt: "ok làm đi" | Case A Load vs chính nó: PASS; Case B Soak: REGRESSION 8/8 (exit 1); Case C Spike: PASS (6 cảnh báo nhiễu); Case D chỉ ngưỡng %: REGRESSION giả 6/8. Nguyên văn: transcript dòng 2116–cuối. | **VALID** | Đã chạy trên 4 bộ .jtl thật; hành vi khớp thiết kế ngưỡng kép. ISTQB CTFL v4.0 §6.2 (benefits and risks of test automation – false positives). | Không sửa code; ghi nhận hạn chế: View Order History ở Case C tăng đúng +5 ms (biên ngưỡng) → cần hiệu chỉnh theo độ lệch chuẩn runner. |
| 13 | **Ảnh bằng chứng do AI thao tác (evidence/ReportView_*.png, evidence/*_resource.jpg)**<br>Tool/Time: Claude Code · ~15:31–15:48 22/11/2026<br>Prompt: "tôi mở jmeter rồi, hoặc bạn tự mở rồi chụp report giúp tôi, tôi cấp toàn quyền." | 3 ảnh JMeter GUI (Summary Report / Aggregate Report / View Results Tree) nạp từ .jtl chính thức; 3 khung hình cắt từ video quay màn hình của sinh viên bằng ffmpeg. Nguyên văn: transcript dòng 1822–1967. | **VALID** | Số trên ảnh khớp .jtl gốc (Load 8.268 sample, 0%; Stress 193.203 sample, p95 45 ms, p99 91 ms) và khớp analysis.md. Ảnh không phải do AI tạo nội dung mà chụp từ dữ liệu thật; tuy vậy được khai báo minh bạch vì do AI thao tác. | Ghi chú trong báo cáo: listener Spike đã bỏ tick "Errors" để hiển thị mẫu (0 lỗi); plan mở từ test-plans/report-view (bản sao trỏ sẵn .jtl). |
| 14 | **Nội dung 6 GitHub Issue (#2–#7)**<br>Tool/Time: Claude Code · ~15:58 22/11/2026<br>Prompt: "https://github.com/KTPM2026/HW5 https://youtu.be/Y2VKcs27d3Y" | AI soạn và đăng 6 issue bằng gh CLI. Nguyên văn: docs/05_GitHub_Issues.md và https://github.com/KTPM2026/HW5/issues. | **INVALID** | AI Agreement §11: "Bug reports: 100% student-written; AI may not draft the description". Nội dung kỹ thuật đã kiểm chứng (curl, .jtl) nhưng phần mô tả do AI viết – vi phạm quy định dù đúng nội dung. | [SINH VIÊN THỰC HIỆN] Tự viết lại phần mô tả của 6 issue bằng lời của mình (giữ số liệu/ảnh làm bằng chứng), cập nhật docs/05_GitHub_Issues.md tương ứng. |
| 15 | **Bản nháp AI Critique (docs/08_AI_Critique.md)**<br>Tool/Time: Claude Code · ~16:08 22/11/2026<br>Prompt: "ok làm đi" | Đoạn ~290 từ về lỗi của AI và nguyên tắc rút ra. Nguyên văn: transcript dòng 2116–cuối. | **INCOMPLETE** | Nội dung bám đúng các lỗi đã ghi nhận, nhưng phần phản tư phải là của sinh viên (đề HW05 mục 10; AI-04 Reflective Statement câu 5). | [SINH VIÊN THỰC HIỆN] Viết lại bằng trải nghiệm và giọng văn của mình; giữ 200–300 từ. |

## 4. Summary of AI Accuracy

| Metric | Count | Percentage |
|---|---:|---:|
| Total AI-generated artifacts audited | 15 | 100% |
| VALID (correct, accepted as-is) | 3 | 20% |
| INVALID (wrong; rejected) | 6 | 40% |
| INCOMPLETE (acceptable after edits) | 6 | 40% |

## 5. Conclusion — When should AI be used (or not)?

AI hữu ích nhất ở phần cơ học có thể kiểm chứng ngay: đọc mã nguồn để khảo sát API, sinh dữ liệu và test plan, chạy JMeter và tính thống kê từ .jtl – các artifact này lỗi là lộ ngay khi chạy. AI kém nhất ở chỗ cần phán đoán và ngữ cảnh: chọn mức tải, gán nguyên nhân lỗi, so sánh các lần chạy khác điều kiện, và đưa ra hệ số lợi ích không có phép đo. Khuyến nghị: dùng AI cho bản nháp và tự động hóa, nhưng mọi kết luận về hiệu năng phải truy về một dòng trong .jtl hoặc một phép đo lặp lại được; prompt phải kèm SLA và điều kiện chạy; các phần quy định là của sinh viên (bug report, phản tư, video) không giao cho AI.

## 6. Mandatory Disclosure

"Test plans, data-preparation and analysis scripts, the API survey and the performance report were initially generated by Claude Code (Claude Opus 5.5); I reviewed and modified the test-plan calculation (Groovy → __jexl3), the assertion messages, the Stress and Soak load parameters, the resource-monitor script and the analysis figures, and added the Stress breakpoint and Soak scenarios; the three JMeter report-view screenshots were captured by Claude Code from my own result files and the resource screenshots were cut by Claude Code from my own recording; the official test executions, the demo video with my own narration, the dxdiag hardware report and [the AI Critique and the GitHub bug report descriptions – to be rewritten by me before submission] were done entirely by me. The detailed AI Audit Report is attached as Appendix A. I confirm I did not use AI to generate any artifact listed in the prohibited category."

## Signature

| Field | Value |
|---|---|
| Student name (printed): | Nguyễn Đức Phát |
| Student ID: | 23120317 |
| Class / Cohort: | Nhóm KTPM2026 – Thành viên 5 |
| Course: | CS423 / CSC13003 – Software Testing |
| Instructor: | Dr. Lam Quang Vu / Dr. Tran Duy Hoang / MSc. Tran Thi Bich Hanh / MSc. Truong Phuoc Loc / MSc. Ho Tuan Thanh |
| Date: | 22/11/2026 |
| Signature: |  |

## References

- Kharbach, M. (2026). AI Use Policy Templates for Higher Education. CC BY-NC-SA 4.0.
- ISTQB Certified Tester Foundation Level Syllabus v4.0 – §2.2.2 Test Types, §5.5 Defect Management, §6.2 Benefits and Risks of Test Automation.
- ISTQB Certified Tester Performance Testing (CT-PT) Syllabus – ch.1 Basic Concepts (types of performance testing), ch.2 Performance Measurement Fundamentals, ch.4 Performance Testing Tasks.
- Apache JMeter User Manual – Component Reference & Functions (https://jmeter.apache.org/usermanual/).
- SQLite – EXPLAIN QUERY PLAN (https://www.sqlite.org/eqp.html), Write-Ahead Logging (https://www.sqlite.org/wal.html), File Locking (https://www.sqlite.org/lockingv3.html).
- Microsoft Docs – Standard numeric format strings (N vs F).
- Hardman, P. (2025). A Post-AI Learning Taxonomy.

> Lưu ý cho sinh viên: hãy tự kiểm tra lại số mục ISTQB theo đúng phiên bản syllabus dùng trên lớp trước khi ký.
