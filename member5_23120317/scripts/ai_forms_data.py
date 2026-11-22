"""Dữ liệu dùng chung cho các biểu mẫu AI (AI-02 Audit, AI-03 Disclosure, AI-04 Reflective, AI-05 Privacy).
Mọi trích dẫn transcript trỏ tới docs/ai_session_transcript.txt (số dòng) – output nguyên văn nằm ở đó.
"""

STUDENT = {
    "name": "Nguyễn Đức Phát",
    "id": "23120317",
    "cohort": "Nhóm KTPM2026 – Thành viên 5",
    "course": "CS423 / CSC13003 – Software Testing",
    "assignment_id": "HW05",
    "assignment_title": "HW05 – Performance Testing (Workflow 5: Login → View Order History → Browse Products → Add to Cart → Checkout)",
    "date": "22/11/2026",
    "instructor": "Dr. Lam Quang Vu / Dr. Tran Duy Hoang / MSc. Tran Thi Bich Hanh / MSc. Truong Phuoc Loc / MSc. Ho Tuan Thanh",
    "category": "4 – AI-Assisted Production",
}

TOOLS = [
    "Claude Code v2.1.329 (CLI, Windows) – model Claude Opus 5.5 (claude-opus-5-5), Anthropic – trợ lý chính, chạy dạng agent (đọc file, chạy lệnh, ghi file)",
    "Claude Code subagent `general-purpose` (Claude Opus 5.5) – phiên mới không kế thừa ngữ cảnh, dùng cho Task 2 (AI phân tích .jtl)",
]

# Mỗi artifact: id, tên, công cụ+thời gian, prompt nguyên văn, output (trích + vị trí nguyên văn), verdict, lý do (có trích dẫn), sửa
ARTIFACTS = [
    dict(
        name="Khảo sát API (docs/01_API_Survey.md)",
        time="Claude Code · ~21:40 19/11/2026",
        prompt="Đọc HW05, tôi là thành viên 5, chịu trách nhiệm về các phần sau: Người 5 Workflow 5 Login → View Order History → Browse Products → Add to Cart → Checkout Truy xuất lịch sử đơn hàng và tạo đơn mới […] 1. Khảo sát API đăng nhập. 2. Khảo sát API Order History. 3. Khảo sát API sản phẩm. 4. Khảo sát API Cart. 5. Khảo sát API Checkout. 6. Chuẩn bị dữ liệu tài khoản và đơn hàng. 7. Thiết kế và chạy 3 kịch bản Performance Testing. 8. Phân tích kết quả và đề xuất tối ưu.",
        output="Bảng 5 endpoint (auth, SQL, index, phân trang) + 9 bug ứng viên B1–B9 (lockout +2/180 s, giỏ không xóa, full scan orders, IDOR, SQL injection…). Nguyên văn: transcript dòng 10–120; file docs/01_API_Survey.md.",
        verdict="INCOMPLETE",
        reason="Đúng với mã nguồn server.js (đã kiểm chứng lockout bằng curl: 401, 401, 403). Nhưng bỏ sót việc /api/login trả nguyên bản ghi user gồm mật khẩu plaintext – lỗi bảo mật do AI khác phát hiện ở Task 2. ISTQB CTFL v4.0 §2.2.2 (Test types – non-functional/security) và §5.5 (Defect management).",
        fix="Bổ sung Issue #7 \"POST /api/login trả về mật khẩu plaintext\" sau khi tự kiểm tra bằng curl (response chứa \"password\":\"Test1234!\").",
    ),
    dict(
        name="Dữ liệu CSV + script (scripts/prepare_data.js, reset_lockout.js, data/*.csv)",
        time="Claude Code · ~22:50 19/11/2026",
        prompt="(cùng prompt của Artifact #1 – nhiệm vụ 6 \"Chuẩn bị dữ liệu tài khoản và đơn hàng\")",
        output="500 user perf5_user_001..500 (mật khẩu thỏa FR-01), 3 đơn/user = 1.500 đơn, products.csv 10 dòng. Nguyên văn: transcript dòng 10–120; console \"users.csv: 500 user (mới tạo 500, đã có 0); đã tạo thêm 1500 đơn hàng lịch sử\".",
        verdict="VALID",
        reason="Chạy thật trên SUT; pre_run_db.txt mỗi lần chạy chính thức ghi đúng 1.500 đơn, 0 user bị khóa. Đáp ứng yêu cầu data-driven của đề (CSV parameterization) và CT-PT ch.4 (chuẩn bị dữ liệu kiểm thử).",
        fix="Không sửa. Bổ sung bước bắt buộc chạy sau khi start server vì database.js DROP/seed DB khi khởi động.",
    ),
    dict(
        name="Test plan JMeter bản đầu (scripts/gen_testplans.py → *.jmx)",
        time="Claude Code · ~23:00 19/11/2026",
        prompt="Máy tôi có Jmeter rồi, ở D/Tools",
        output="Smoke test lỗi: \"Uncaught Exception BUG! exception in phase 'semantic analysis' in source unit 'Script1.groovy' Unsupported class file major version 69\" – bước 05–08 không chạy. Nguyên văn: transcript dòng 121–252.",
        verdict="INVALID",
        reason="AI dùng JSR223 Groovy mà không kiểm tra JDK (25). Groovy đi kèm JMeter 5.6.3 không đọc được class file Java 25. Bằng chứng: jmeter.log của smoke run. Tham chiếu: Apache JMeter User Manual – Component Reference (JSR223 / Functions: __jexl3).",
        fix="Bỏ JSR223PostProcessor; tính tổng tiền bằng `${__jexl3(${price} * ${quantity})}` trong body Checkout. Smoke lại: 8/8 bước 0% lỗi, đơn hàng tạo đúng tổng tiền.",
    ),
    dict(
        name="Message của Response Assertion",
        time="Claude Code · ~23:28 19/11/2026",
        prompt="cập nhật cho tôi đi",
        output="Bảng phân loại lỗi Stress breakpoint: \"01 Login | Non HTTP response code: org.apache.http.conn.HttpHostConnectException | Sai HTTP status (403 = tài khoản bị khóa / token sai) | 534586\". Nguyên văn: transcript dòng 423–665.",
        verdict="INVALID",
        reason="Message gán sẵn nguyên nhân \"403 = khóa tài khoản\" cho mọi status ≠ 200, trong khi post_run_db.txt cho thấy 0 user bị khóa – lỗi thật là connection refused. Assertion phải mô tả điều kiện kiểm tra, không đoán nguyên nhân (CT-PT ch.2 – thu thập & diễn giải metric).",
        fix="Đổi message thành \"HTTP status khác mong đợi (401/403 = sai credential/bị khóa/token; Non HTTP = lỗi kết nối/timeout)\" trong gen_testplans.py, sinh lại 4 test plan.",
    ),
    dict(
        name="Tham số kịch bản Stress (100→500 VU)",
        time="Claude Code · ~23:00 19/11/2026",
        prompt="(cùng prompt của Artifact #1 – nhiệm vụ 7 \"Thiết kế và chạy 3 kịch bản\")",
        output="Stress 5 bậc × 100 VU, think 0,3–1 s → 0% lỗi, p95 ≤ 35 ms: không tìm được điểm gãy. Nguyên văn: transcript dòng 253–422.",
        verdict="INCOMPLETE",
        reason="Mục tiêu stress test là tìm giới hạn/điểm gãy (ISTQB CT-PT ch.1 – types of performance testing: stress testing). AI ước lượng năng lực Node.js + SQLite quá thấp.",
        fix="Giữ plan làm Stress \"theo thiết kế\", thêm biến thể breakpoint `-Jstep_users=400 -Jthink_min=0 -Jthink_range=200` (400→2000 VU): tìm được bão hòa ~900–950 RPS, gãy ~1.100–1.200 VU.",
    ),
    dict(
        name="Tham số Soak mặc định",
        time="Claude Code · ~23:30 19/11/2026",
        prompt="cập nhật cho tôi đi",
        output="Soak mặc định 150 VU, think 1–2 s ≈ 100 RPS (khoảng 10% năng lực đo được). Nguyên văn: transcript dòng 423–665.",
        verdict="INVALID",
        reason="Endurance test phải ở mức tải duy trì gần ngưỡng thực tế (CT-PT ch.1 – endurance testing); 10% năng lực không cho thông tin về ngưỡng bền.",
        fix="Đổi mặc định thành 400 VU, think 0,3–1 s (~600 RPS ≈ 65% throughput tối đa). Kết quả: suy giảm p95 47 → 393 ms trong 15 phút.",
    ),
    dict(
        name="Script giám sát tài nguyên (run_scenario.sh) + số liệu CPU",
        time="Claude Code · ~23:55 19/11/2026",
        prompt="phần bạn xong chưa, hãy đưa ra hướng dẫn chi tiết các bước làm phần của tôi đi.",
        output="Báo \"CPU 113%\" cho Stress; node_resource.csv có dòng \"23:44:29,113.1,1,065.9\" (dấu phẩy hàng nghìn làm vỡ cột). Nguyên văn: transcript dòng 666–766.",
        verdict="INVALID",
        reason="PowerShell format \"{2:N1}\" chèn dấu phân cách hàng nghìn (Microsoft Docs – Standard numeric format strings, \"N\" vs \"F\"); script còn giả định chu kỳ 5 s trong khi thực tế ~14 s khi máy tải nặng.",
        fix="Đổi sang \"{2:F1}\"; analyze_jtl.py ghép lại cột thừa và tính CPU theo timestamp thật → Stress CPU TB 54% / đỉnh 90% (không phải 113%).",
    ),
    dict(
        name="Báo cáo phân tích (docs/03_Results_Analysis.md)",
        time="Claude Code · ~00:00 20/11/2026, cập nhật 15:35 22/11/2026",
        prompt="ok tôi làm xong bước 2 trong file rồi, các file cần có tôi đã lưu ở root, làm cho tôi từ bước 3 đi.",
        output="Bảng tổng hợp 5 kịch bản, nguyên nhân gốc, 11 đề xuất tối ưu, bẫy diễn giải. Nguyên văn: file docs/03_Results_Analysis.md; transcript dòng 1158–1263.",
        verdict="INCOMPLETE",
        reason="Bản đầu ghi \"95% lỗi ở Login\" (đúng 99,9% = 538.783/539.398) và dựa vào so sánh 2 lần Load mà file .jtl đã bị ghi đè (không còn bằng chứng). Đề yêu cầu mọi kết luận đối chiếu được với .jtl gốc (AI Agreement §11 – Performance results).",
        fix="Sửa thành 99,9%; thay so sánh mất bằng chứng bằng số đo bench_index.md; cập nhật toàn bộ bảng bằng số của 3 lần chạy chính thức 22/11.",
    ),
    dict(
        name="Task 2 – AI phân tích .jtl (docs/task2/ai_analysis_output_raw.md)",
        time="Claude Code subagent · ~15:35 22/11/2026",
        prompt="Nguyên văn đầy đủ: docs/task2/ai_analysis_prompt.md (\"Bạn là chuyên gia performance testing… Câu 1… Câu 2… Câu 3…\")",
        output="Nguyên văn đầy đủ: docs/task2/ai_analysis_output_raw.md.",
        verdict="INCOMPLETE",
        reason="Đọc đúng thống kê nhưng 7 chỗ diễn giải sai (M1–M7 trong ai_analysis_review.md), ví dụ nối 2 phiên chạy khác ngày thành một chuỗi (pre_run_db.txt: breakpoint bắt đầu 28.275 đơn, không phải 28.163), tự đặt SLA 200 ms sau khi xem kết quả. CT-PT ch.2 (aggregating results) – không trộn kết quả từ điều kiện thử khác nhau.",
        fix="docs/task2/ai_analysis_review.md: mỗi lỗi có giá trị đúng trích từ .jtl/console.txt/pre_run_db.txt.",
    ),
    dict(
        name="Task 2 – Đề xuất tối ưu của AI",
        time="Claude Code subagent · ~15:35 22/11/2026",
        prompt="(Câu 3 trong docs/task2/ai_analysis_prompt.md) \"Đề xuất các tối ưu cụ thể cho backend này (ví dụ index database, connection pool, SQLite WAL, cache, cluster...), mỗi đề xuất nêu lợi ích kỳ vọng.\"",
        output="20 đề xuất (index, LIMIT, WAL, prepared statement, cache, cluster ×3–4, better-sqlite3 ×2–5…). Nguyên văn: ai_analysis_output_raw.md – Câu 3.",
        verdict="INCOMPLETE",
        reason="9 feasible (2 đã đo: index 8,9×, LIMIT 59×). \"WAL là điều kiện bắt buộc để cluster SQLite\" là sai: rollback journal vẫn hỗ trợ nhiều process qua file locking (SQLite docs – File Locking And Concurrency, https://www.sqlite.org/lockingv3.html; WAL https://www.sqlite.org/wal.html). 5 hệ số lợi ích không có phép đo.",
        fix="Bảng phân loại feasible/hallucinated trong ai_analysis_review.md §3; chỉ giữ đề xuất có số đo trong khuyến nghị ưu tiên (03_Results_Analysis.md §7).",
    ),
    dict(
        name="CI workflow mẫu (ci/perf-regression.yml)",
        time="Claude Code · ~16:05 22/11/2026",
        prompt="ok làm đi",
        output="yaml.parser.ParserError: while parsing a flow mapping … expected ',' or '}', but got '{' (dòng 70: `with: { name: perf-${{ github.sha }}, … }`). Nguyên văn: transcript dòng 2116–cuối.",
        verdict="INVALID",
        reason="Biểu thức `${{ }}` đặt trong YAML flow mapping `{ }` làm hỏng cú pháp (YAML 1.2 spec – flow mappings; GitHub Docs – Expressions).",
        fix="Viết lại `with:` dạng block (name / path: |). Kiểm tra lại bằng yaml.safe_load: OK, 2 job, 9 step. Chưa chạy thật trên GitHub Actions.",
    ),
    dict(
        name="Cổng hồi quy p95 (scripts/perf_gate.py)",
        time="Claude Code · ~16:00 22/11/2026",
        prompt="ok làm đi",
        output="Case A Load vs chính nó: PASS; Case B Soak: REGRESSION 8/8 (exit 1); Case C Spike: PASS (6 cảnh báo nhiễu); Case D chỉ ngưỡng %: REGRESSION giả 6/8. Nguyên văn: transcript dòng 2116–cuối.",
        verdict="VALID",
        reason="Đã chạy trên 4 bộ .jtl thật; hành vi khớp thiết kế ngưỡng kép. ISTQB CTFL v4.0 §6.2 (benefits and risks of test automation – false positives).",
        fix="Không sửa code; ghi nhận hạn chế: View Order History ở Case C tăng đúng +5 ms (biên ngưỡng) → cần hiệu chỉnh theo độ lệch chuẩn runner.",
    ),
    dict(
        name="Ảnh bằng chứng do AI thao tác (evidence/ReportView_*.png, evidence/*_resource.jpg)",
        time="Claude Code · ~15:31–15:48 22/11/2026",
        prompt="tôi mở jmeter rồi, hoặc bạn tự mở rồi chụp report giúp tôi, tôi cấp toàn quyền.",
        output="3 ảnh JMeter GUI (Summary Report / Aggregate Report / View Results Tree) nạp từ .jtl chính thức; 3 khung hình cắt từ video quay màn hình của sinh viên bằng ffmpeg. Nguyên văn: transcript dòng 1822–1967.",
        verdict="VALID",
        reason="Số trên ảnh khớp .jtl gốc (Load 8.268 sample, 0%; Stress 193.203 sample, p95 45 ms, p99 91 ms) và khớp analysis.md. Ảnh không phải do AI tạo nội dung mà chụp từ dữ liệu thật; tuy vậy được khai báo minh bạch vì do AI thao tác.",
        fix="Ghi chú trong báo cáo: listener Spike đã bỏ tick \"Errors\" để hiển thị mẫu (0 lỗi); plan mở từ test-plans/report-view (bản sao trỏ sẵn .jtl).",
    ),
    dict(
        name="Nội dung 6 GitHub Issue (#2–#7)",
        time="Claude Code · ~15:58 22/11/2026",
        prompt="https://github.com/KTPM2026/HW5 https://youtu.be/Y2VKcs27d3Y",
        output="AI soạn và đăng 6 issue bằng gh CLI. Nguyên văn: docs/05_GitHub_Issues.md và https://github.com/KTPM2026/HW5/issues.",
        verdict="INVALID",
        reason="AI Agreement §11: \"Bug reports: 100% student-written; AI may not draft the description\". Nội dung kỹ thuật đã kiểm chứng (curl, .jtl) nhưng phần mô tả do AI viết – vi phạm quy định dù đúng nội dung.",
        fix="Sinh viên tự viết lại phần \"Mô tả\" của cả 6 issue (22/11/2026); AI chỉ thay nội dung vào issue, giữ nguyên lời sinh viên (chỉ sửa chính tả). Phần bằng chứng (số liệu, biểu đồ, curl) giữ lại bên dưới. Ảnh trang Issues chụp lại sau khi sửa.",
    ),
    dict(
        name="Bản nháp AI Critique (docs/08_AI_Critique.md)",
        time="Claude Code · ~16:08 22/11/2026",
        prompt="ok làm đi",
        output="Đoạn ~290 từ về lỗi của AI và nguyên tắc rút ra. Nguyên văn: transcript dòng 2116–cuối.",
        verdict="INCOMPLETE",
        reason="Nội dung bám đúng các lỗi đã ghi nhận, nhưng phần phản tư phải là của sinh viên (đề HW05 mục 10; AI-04 Reflective Statement câu 5).",
        fix="Bỏ bản nháp của AI. Sinh viên trả lời 3 câu hỏi (lỗi đáng chú ý: CPU 113%, con số lợi ích không đo, Groovy/JDK 25; nguyên nhân: AI lấy số rồi đưa thẳng vào báo cáo, không kiểm tra lại; nguyên tắc: con người giám sát, double-check số liệu, yêu cầu AI rà soát lại) – AI chỉ diễn đạt lại thành đoạn 298 từ (Category 3).",
    ),
]

CONCLUSION = (
    "AI hữu ích nhất ở phần cơ học có thể kiểm chứng ngay: đọc mã nguồn để khảo sát API, sinh dữ liệu và test plan, "
    "chạy JMeter và tính thống kê từ .jtl – các artifact này lỗi là lộ ngay khi chạy. AI kém nhất ở chỗ cần phán đoán "
    "và ngữ cảnh: chọn mức tải, gán nguyên nhân lỗi, so sánh các lần chạy khác điều kiện, và đưa ra hệ số lợi ích không "
    "có phép đo. Khuyến nghị: dùng AI cho bản nháp và tự động hóa, nhưng mọi kết luận về hiệu năng phải truy về một dòng "
    "trong .jtl hoặc một phép đo lặp lại được; prompt phải kèm SLA và điều kiện chạy; các phần quy định là của sinh viên "
    "(bug report, phản tư, video) không giao cho AI."
)

DISCLOSURE = (
    "Test plans, data-preparation and analysis scripts, the API survey and the performance report were initially generated by "
    "Claude Code (Claude Opus 5.5); I reviewed and modified the test-plan calculation (Groovy → __jexl3), the assertion messages, "
    "the Stress and Soak load parameters, the resource-monitor script and the analysis figures, and added the Stress breakpoint "
    "and Soak scenarios; the three JMeter report-view screenshots were captured by Claude Code from my own result files and the "
    "resource screenshots were cut by Claude Code from my own recording; the AI Critique and Reflective answer 5 are based on my own "
    "answers and were only rephrased by Claude Code; the official test executions, the demo video with my own narration, the dxdiag "
    "hardware report and the descriptions of the six GitHub bug reports were written/done entirely by me. "
    "The detailed AI Audit Report is attached as Appendix A. I confirm I did not use AI to generate any artifact listed in the "
    "prohibited category."
)
