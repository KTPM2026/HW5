# AI Use Disclosure Form (HW05 – Thành viên 5)

> Theo mẫu **[AI-03]**; bản .docx: `ai-forms/[AI-03] AI Disclosure Form – 23120317.docx`.

## 1. Course & Student Info

| Field | Value |
|---|---|
| Course: | CS423 / CSC13003 – Software Testing |
| Assignment ID: | HW05 |
| Assignment Title: | HW05 – Performance Testing (Workflow 5: Login → View Order History → Browse Products → Add to Cart → Checkout) |
| AI Use Category (1–5): | Category 4 – AI-Assisted Production |
| Date: | 22/11/2026 |
| Student name: | Nguyễn Đức Phát |
| Student ID: | 23120317 |

## 2. Disclosure Questions

### 1. AI tool(s) used:

- Claude Code v2.1.329 (CLI, Windows) – model Claude Opus 5.5 (claude-opus-5-5), Anthropic – trợ lý chính, chạy dạng agent (đọc file, chạy lệnh, ghi file)
- Claude Code subagent `general-purpose` (Claude Opus 5.5) – phiên mới không kế thừa ngữ cảnh, dùng cho Task 2 (AI phân tích .jtl)

### 2. Stage(s) of the assignment where AI was used:

[x] brainstorming  [x] outlining  [x] drafting  [ ] feedback  [x] revision  [x] coding  [x] data analysis  [x] visual design  [x] other: chạy JMeter CLI, thao tác Git/GitHub, chụp ảnh JMeter GUI

### 3. Main prompts or tasks given to the AI:

- "Đọc HW05, tôi là thành viên 5, chịu trách nhiệm về các phần sau: Người 5 Workflow 5 Login → View Order History → Browse Products → Add to Cart → Checkout Truy xuất lịch sử đơn hàng và tạo đơn mới / Người 5 – Kiểm thử lịch sử đơn hàng / Phụ trách: 1. Khảo sát API đăng nhập. 2. Khảo sát API Order History. 3. Khảo sát API sản phẩm. 4. Khảo sát API Cart. 5. Khảo sát API Checkout. 6. Chuẩn bị dữ liệu tài khoản và đơn hàng. 7. Thiết kế và chạy 3 kịch bản Performance Testing. 8. Phân tích kết quả và đề xuất tối ưu."
- "ok tôi làm xong bước 2 trong file rồi, các file cần có tôi đã lưu ở root, làm cho tôi từ bước 3 đi."
- "ok làm đi"
- Toàn bộ prompt: Appendix A `docs/prompt_log.md`; transcript `docs/ai_session_transcript.txt`.

### 4. Specific parts of the work AI contributed to:

AI tạo: khảo sát API (01), script dữ liệu + CSV, bộ sinh 4 test plan .jmx, script chạy/giám sát/phân tích, thiết kế kịch bản (02), báo cáo phân tích + đề xuất tối ưu (03), Task 2 (AI phân tích + bản review đầu), Task 3 (06, perf_gate.py, CI mẫu), Agent Skill, biểu đồ, ảnh 3 report view, cắt ảnh tài nguyên từ video, đăng PR/issue, bản nháp AI Critique. AI KHÔNG làm: chạy chính thức 3 kịch bản và quay video có thuyết minh (sinh viên), ảnh dxdiag (sinh viên). Sinh viên tự viết: mô tả 6 bug report (#2–#7). AI Critique và câu 5 Reflective: ý của sinh viên (trả lời câu hỏi), AI chỉ diễn đạt lại.

### 5. How I reviewed, revised, or verified the AI output:

Chạy smoke test trước mọi lần chạy thật; đối chiếu mọi số trong báo cáo với .jtl gốc bằng analyze_jtl.py; kiểm tra lockout và các bug bằng curl trên SUT; kiểm tra pre_run_db.txt/post_run_db.txt (số đơn, user bị khóa); đo lại đề xuất index/LIMIT trên bản sao DB; dùng một AI phiên mới (không ngữ cảnh) để phân tích độc lập rồi đối chiếu; kiểm tra cú pháp YAML; đối chiếu ảnh report view với số mẫu trong .jtl. 15 artifact được gán verdict trong AI Audit Report.

### 6. Citation (if required by course style guide):

Anthropic. (2026). Claude Opus 5.5 via Claude Code v2.1.329 [Large language model / coding agent]. https://claude.com/claude-code

## 3. Statement of Honesty

By signing below, I confirm that the disclosure above is accurate and complete. I understand that undisclosed or false disclosure of AI use is treated as academic misconduct and may result in a 0 grade for the assignment and disciplinary referral.

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
