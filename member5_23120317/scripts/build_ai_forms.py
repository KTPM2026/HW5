#!/usr/bin/env python3
"""Sinh các biểu mẫu AI theo template FIT@HCMUS (AI-02..AI-05) + prompt log, dạng Markdown và .docx.
   python scripts/build_ai_forms.py "<thư mục chứa AI Templates/*.docx>"
"""
import copy
import sys
from collections import Counter
from pathlib import Path

import docx

sys.path.insert(0, str(Path(__file__).parent))
from ai_forms_data import ARTIFACTS, CONCLUSION, DISCLOSURE, STUDENT, TOOLS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS, FORMS = ROOT / "docs", ROOT / "ai-forms"
TPL = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "_ai_templates" / "AI Templates"
S = STUDENT

# ------------------------------------------------------------------ prompt log (Appendix A)
PROMPTS = [  # (thời gian ~, prompt nguyên văn, dòng transcript, việc AI làm)
    ("19/11/2026 ~21:35", "Đọc HW05, tôi là thành viên 5, chịu trách nhiệm về các phần sau: Người 5 Workflow 5 Login → View Order History → Browse Products → Add to Cart → Checkout Truy xuất lịch sử đơn hàng và tạo đơn mới / Người 5 – Kiểm thử lịch sử đơn hàng / Phụ trách: 1. Khảo sát API đăng nhập. 2. Khảo sát API Order History. 3. Khảo sát API sản phẩm. 4. Khảo sát API Cart. 5. Khảo sát API Checkout. 6. Chuẩn bị dữ liệu tài khoản và đơn hàng. 7. Thiết kế và chạy 3 kịch bản Performance Testing. 8. Phân tích kết quả và đề xuất tối ưu.", 10, "Đọc đề, clone SUT, khảo sát API, viết script dữ liệu, sinh test plan"),
    ("19/11/2026 ~22:58", "Máy tôi có Jmeter rồi, ở D/Tools", 121, "Dùng JMeter có sẵn; smoke test lỗi Groovy/JDK 25 → sửa __jexl3; chạy Load/Stress/Spike lần 1"),
    ("19/11/2026 ~23:05", "1. MSSV: 23120317, tên: Nguyễn Đức Phát. 2. Có bắt buộc tôi phải tự chạy không, hay bạn chạy cho tôi được ?", 253, "Đổi tên test plan theo MSSV; giải thích phần bắt buộc sinh viên tự làm"),
    ("19/11/2026 ~23:25", "cập nhật cho tôi đi", 423, "Báo kết quả, chạy Stress breakpoint, sửa assertion message, chạy Soak"),
    ("19/11/2026 ~23:55", "phần bạn xong chưa, hãy đưa ra hướng dẫn chi tiết các bước làm phần của tôi đi.", 666, "Phân tích Soak, đo index trên bản sao DB, viết báo cáo + hướng dẫn"),
    ("22/11/2026 ~14:55", "làm phần quay video này đơn giản hơn đi, nó đang khá phức tạp so với đề bài yêu cầu", 767, "Viết record_demo.sh, rút gọn hướng dẫn quay"),
    ("22/11/2026 ~15:30", "ok tôi làm xong bước 2 trong file rồi, các file cần có tôi đã lưu ở root, làm cho tôi từ bước 3 đi.", 1158, "Phân tích lần chạy chính thức, cắt ảnh từ video, Task 2 (subagent), soạn issue, Git"),
    ("22/11/2026 ~15:40", "đặt tiêu đề video là gì", 1264, "Đề xuất tiêu đề + mô tả YouTube"),
    ("22/11/2026 ~15:42", "tôi mở jmeter rồi, hoặc bạn tự mở rồi chụp report giúp tôi, tôi cấp toàn quyền.", 1822, "Mở JMeter GUI, chụp 3 report view"),
    ("22/11/2026 ~15:55", "https://github.com/KTPM2026/HW5 https://youtu.be/Y2VKcs27d3Y", 1968, "Fork + PR #1, vẽ biểu đồ, đăng issue #2–#7, README"),
    ("22/11/2026 ~16:00", "ok làm đi", 2116, "Task 3, Agent Skill, AI Audit Report, bản nháp AI Critique"),
    ("22/11/2026 ~16:09", "ok tôi xuất rồi, điền hộ cho tôi full điểm trừ Agent skill, sau đó zip và đưa tôi file nộp", None, "Điền tự đánh giá 90, PDF, đóng gói zip"),
    ("22/11/2026 ~16:13", "Xem lại D:\\University\\Testing\\HW05\\AI Templates-20261122T091219Z-1-001.zip, và tuân thủ theo đi. Rà soát bài nộp một lần nữa xem có thiếu gì không.", None, "Đối chiếu 6 template, viết lại Audit Report theo AI-02, thêm Disclosure/Reflective/Privacy, prompt log, ảnh trang Issues"),
    ("22/11/2026 ~16:25", "hỏi tôi từng câu cho tôi trả lời rồi paraphrase lại đưa vô", None, "Hỏi lần lượt các câu cho Critique / Reflective / bug report / checklist"),
    ("22/11/2026 ~16:27", "- CPU báo 113% do script giám sát đọc sai. - AI ở Task 2 đưa con số lợi ích (×3–4, +20–40%) không có số đo. - Test plan dùng Groovy nên chạy lỗi trên JDK 25.", None, "Ghi nhận – Critique câu 1"),
    ("22/11/2026 ~16:29", "(Critique câu 2 – chọn lại 3 nguyên nhân gợi ý) + \"Thêm nữa là AI chỉ lấy số nó nhận được rồi bỏ vào, không có giám sát hay double check\"", None, "Ghi nhận – Critique câu 2"),
    ("22/11/2026 ~16:31", "Khi làm việc với AI phải có con người giám sát và double check lại các số liệu nó đưa ra, yêu cầu AI check lại toàn bộ khi làm xong.", None, "Diễn đạt lại thành AI Critique 298 từ"),
    ("22/11/2026 ~16:34", "- Hiểu ra sự khác nhau giữa Load, Stress, Spike và Soak khi nhìn số liệu thật. - Biết cách đọc file .jtl, hoặc biết cách tìm điểm gãy. AI chạy các bài test để hiểu hơn về cách kiểm thử được thực hiện, các bài sau sẽ giữ nguyên tắt review lại output của AI, và hỏi lại AI từ những output nó đưa ra để hiểu bài hơn.", None, "Diễn đạt lại thành Reflective câu 5"),
    ("22/11/2026 ~16:36", "API này trả về toàn bộ đơn, trong khi chỉ cần một số ít đơn, không có phân trang. Toàn bộ đơn được truy vấn làm tăng đỗ trễ và kích thước response", None, "Giữ nguyên văn làm mô tả Issue #2 (chỉ sửa chính tả)"),
    ("22/11/2026 ~16:38", "Còn nhiều không, đưa ra hết để tôi trả lời một lượt.", None, "Liệt kê các câu còn lại"),
    ("22/11/2026 ~16:40", "(Mô tả Issue #3–#7 do sinh viên viết – nguyên văn trong docs/05_GitHub_Issues.md, mục \"Mô tả\") + \"Phần 4 xác nhận có hết cho tôi.\"", None, "Cập nhật nguyên văn mô tả issue #3–#7 lên GitHub; tick Privacy Checklist"),
]
SUBAGENT = ("22/11/2026 ~15:35", "docs/task2/ai_analysis_prompt.md", "docs/task2/ai_analysis_output_raw.md")


def prompt_log_md():
    out = ["# Appendix A – prompt_log.md (Thành viên 5 – 23120317)", "",
           f"- **Công cụ:** {TOOLS[0]}", f"- **Subagent:** {TOOLS[1]}",
           "- **Output nguyên văn:** `docs/ai_session_transcript.txt` (xuất bằng `/export` của Claude Code). Cột *Dòng* là số dòng bắt đầu lượt đó trong transcript.",
           "- **Thời gian:** giờ địa phương GMT+7; transcript không ghi giờ nên giờ được ước lượng từ thời điểm tạo file/commit trong lượt đó (`git_commit_log.txt`).", "",
           "| # | Thời gian | Prompt (nguyên văn) | Dòng | AI đã làm |", "|---:|---|---|---:|---|"]
    for i, (t, p, line, did) in enumerate(PROMPTS, 1):
        out.append(f"| {i} | {t} | {p} | {line or '(sau khi export)'} | {did} |")
    out += ["", "## Subagent Task 2", "", f"| Thời gian | Prompt | Output |\n|---|---|---|\n| {SUBAGENT[0]} | `{SUBAGENT[1]}` (nguyên văn) | `{SUBAGENT[2]}` (nguyên văn) |"]
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ AI-02 Audit Report
def counts():
    c = Counter(a["verdict"] for a in ARTIFACTS)
    n = len(ARTIFACTS)
    return n, [(k, c[k], f"{100 * c[k] / n:.0f}%") for k in ("VALID", "INVALID", "INCOMPLETE")]


INFO_ROWS = [("Student name (printed):", S["name"]), ("Student ID:", S["id"]), ("Class / Cohort:", S["cohort"]),
             ("Assignment ID (e.g., HW#00, HW#02):", S["assignment_id"]), ("Assignment date:", S["date"]),
             ("AI tool(s) used:", "; ".join(TOOLS))]
SIGN_ROWS = [("Student name (printed):", S["name"]), ("Student ID:", S["id"]), ("Class / Cohort:", S["cohort"]),
             ("Course:", S["course"]), ("Instructor:", S["instructor"]), ("Date:", S["date"]), ("Signature:", "")]


def esc(t):
    return str(t).replace("|", "\\|").replace("\n", " ")


def audit_md():
    n, rows = counts()
    o = ["# AI Audit Report — 5-section Template per Artifact (HW05 – Thành viên 5)", "",
         "> Theo mẫu **[AI-02] FIT@HCMUS – AI Audit Report** (bản .docx đã điền: `ai-forms/[AI-02] AI Audit Report – 23120317.docx`).", "",
         "## 1. Student Information", "", "| Field | Value |", "|---|---|"]
    o += [f"| {k} | {esc(v)} |" for k, v in INFO_ROWS] + ["| AI used? | [x] Yes  [ ] No |", "",
          "## 2. Instructions (đã tuân thủ)", "",
          "- Mỗi artifact do AI tạo là một hàng. Prompt **nguyên văn** (không diễn giải).",
          "- AI output: trích đoạn chính + vị trí **nguyên văn** trong `docs/ai_session_transcript.txt` (số dòng) hoặc file artifact.",
          "- Verdict: VALID / INVALID / INCOMPLETE; lý do trích ISTQB / tài liệu kỹ thuật / bằng chứng log gốc; cột 5 là bản sửa của sinh viên.",
          "- Prompt log có thời gian: `docs/prompt_log.md` (Appendix A).", "",
          "## 3. Audit Table — one row per artifact", "",
          "| # | (1) Prompt + Tool | (2) AI Output | (3) Verdict | (4) Reasoning | (5) Student Fix |", "|---:|---|---|---|---|---|"]
    for i, a in enumerate(ARTIFACTS, 1):
        o.append(f"| {i} | **{esc(a['name'])}**<br>Tool/Time: {esc(a['time'])}<br>Prompt: \"{esc(a['prompt'])}\" | {esc(a['output'])} | **{a['verdict']}** | {esc(a['reason'])} | {esc(a['fix'])} |")
    o += ["", "## 4. Summary of AI Accuracy", "", "| Metric | Count | Percentage |", "|---|---:|---:|",
          f"| Total AI-generated artifacts audited | {n} | 100% |"]
    o += [f"| {k} ({'correct, accepted as-is' if k == 'VALID' else 'wrong; rejected' if k == 'INVALID' else 'acceptable after edits'}) | {c} | {p} |" for k, c, p in rows]
    o += ["", "## 5. Conclusion — When should AI be used (or not)?", "", CONCLUSION, "",
          "## 6. Mandatory Disclosure", "", f"\"{DISCLOSURE}\"", "", "## Signature", "", "| Field | Value |", "|---|---|"]
    o += [f"| {k} | {esc(v)} |" for k, v in SIGN_ROWS]
    o += ["", "## References", "",
          "- Kharbach, M. (2026). AI Use Policy Templates for Higher Education. CC BY-NC-SA 4.0.",
          "- ISTQB Certified Tester Foundation Level Syllabus v4.0 – §2.2.2 Test Types, §5.5 Defect Management, §6.2 Benefits and Risks of Test Automation.",
          "- ISTQB Certified Tester Performance Testing (CT-PT) Syllabus – ch.1 Basic Concepts (types of performance testing), ch.2 Performance Measurement Fundamentals, ch.4 Performance Testing Tasks.",
          "- Apache JMeter User Manual – Component Reference & Functions (https://jmeter.apache.org/usermanual/).",
          "- SQLite – EXPLAIN QUERY PLAN (https://www.sqlite.org/eqp.html), Write-Ahead Logging (https://www.sqlite.org/wal.html), File Locking (https://www.sqlite.org/lockingv3.html).",
          "- Microsoft Docs – Standard numeric format strings (N vs F).",
          "- Hardman, P. (2025). A Post-AI Learning Taxonomy.",
          "", "> Lưu ý cho sinh viên: hãy tự kiểm tra lại số mục ISTQB theo đúng phiên bản syllabus dùng trên lớp trước khi ký."]
    return "\n".join(o) + "\n"


# ------------------------------------------------------------------ AI-03 Disclosure / AI-04 Reflective / AI-05 Privacy
DISC = {
    "1. AI tool(s) used:": "\n".join(f"- {t}" for t in TOOLS),
    "2. Stage(s) of the assignment where AI was used:": "[x] brainstorming  [x] outlining  [x] drafting  [ ] feedback  [x] revision  [x] coding  [x] data analysis  [x] visual design  [x] other: chạy JMeter CLI, thao tác Git/GitHub, chụp ảnh JMeter GUI",
    "3. Main prompts or tasks given to the AI:": "\n".join(f"- \"{PROMPTS[i][1]}\"" for i in (0, 6, 10)) + "\n- Toàn bộ prompt: Appendix A `docs/prompt_log.md`; transcript `docs/ai_session_transcript.txt`.",
    "4. Specific parts of the work AI contributed to:": (
        "AI tạo: khảo sát API (01), script dữ liệu + CSV, bộ sinh 4 test plan .jmx, script chạy/giám sát/phân tích, thiết kế kịch bản (02), "
        "báo cáo phân tích + đề xuất tối ưu (03), Task 2 (AI phân tích + bản review đầu), Task 3 (06, perf_gate.py, CI mẫu), Agent Skill, biểu đồ, "
        "ảnh 3 report view, cắt ảnh tài nguyên từ video, đăng PR/issue, bản nháp AI Critique. "
        "AI KHÔNG làm: chạy chính thức 3 kịch bản và quay video có thuyết minh (sinh viên), ảnh dxdiag (sinh viên). "
        "Sinh viên tự viết: mô tả 6 bug report (#2–#7). AI Critique và câu 5 Reflective: ý của sinh viên (trả lời câu hỏi), AI chỉ diễn đạt lại."),
    "5. How I reviewed, revised, or verified the AI output:": (
        "Chạy smoke test trước mọi lần chạy thật; đối chiếu mọi số trong báo cáo với .jtl gốc bằng analyze_jtl.py; kiểm tra lockout và các bug bằng curl trên SUT; "
        "kiểm tra pre_run_db.txt/post_run_db.txt (số đơn, user bị khóa); đo lại đề xuất index/LIMIT trên bản sao DB; dùng một AI phiên mới (không ngữ cảnh) để phân tích độc lập rồi đối chiếu; "
        "kiểm tra cú pháp YAML; đối chiếu ảnh report view với số mẫu trong .jtl. 15 artifact được gán verdict trong AI Audit Report."),
    "6. Citation (if required by course style guide):": "Anthropic. (2026). Claude Opus 5.5 via Claude Code v2.1.329 [Large language model / coding agent]. https://claude.com/claude-code",
}
REFL = {
    "1. How did AI support your work?": "AI làm trợ lý agent trong toàn bộ quy trình: đọc mã SUT để khảo sát 5 API, sinh dữ liệu CSV và test plan JMeter, chạy JMeter CLI và thu RAM/CPU, tính thống kê và timeline từ .jtl, kiểm chứng đề xuất index trên bản sao DB, soạn tài liệu, đề xuất mô hình kiểm thử liên tục kèm cổng hồi quy p95, và một AI phiên mới phân tích độc lập cho Task 2.",
    "2. What did you accept, reject, or revise from AI outputs?": "Chấp nhận: dữ liệu CSV, cổng perf_gate.py, ảnh report view (đã đối chiếu số mẫu). Từ chối/sửa: Groovy → __jexl3; message assertion \"403 = khóa tài khoản\"; tham số Stress (thêm breakpoint) và Soak (150 → 400 VU); format CPU N1 → F1; các số sai trong báo cáo (CPU 113%, 95% lỗi). Từ Task 2 giữ 9 đề xuất feasible, loại khẳng định \"WAL bắt buộc cho cluster\" và 5 hệ số lợi ích không có phép đo.",
    "3. What errors, biases, or limitations did you notice in the AI outputs?": "Không kiểm tra môi trường (JDK 25); ước lượng thấp năng lực SUT; gán sẵn nguyên nhân lỗi trong assertion; đọc sai CSV do định dạng số; trộn kết quả hai phiên chạy khác ngày; tự đặt SLA sau khi xem kết quả; quy nút thắt cho event loop dù số đo theo bước chỉ ra hàng đợi SQLite; đưa hệ số lợi ích (×3–4, +20–40%) không có phép đo; lỗi cú pháp YAML.",
    "4. How did you verify information, sources, or claims provided by AI?": "Chạy trên SUT thật (smoke + 3 lần chính thức có video), đối chiếu với .jtl/console.txt/pre_run_db.txt, kiểm chứng bug bằng curl, đo lại tối ưu trên bản sao DB, so sánh với phân tích của một AI phiên mới, kiểm tra tài liệu SQLite về locking/WAL.",
    "5. What did you learn through this project that you could not have learned by simply accepting AI output?": "Nhìn số liệu thật từ các lần chạy, tôi hiểu rõ sự khác nhau giữa bốn loại kiểm thử: Load cho biết hệ thống ở tải bình thường (50 VU, p95 5 ms), Stress đẩy dần để tìm điểm gãy (bão hòa khoảng 900–950 RPS, gãy ở khoảng 1.100 VU), Spike xem hệ thống chịu và hồi phục sau đột biến, còn Soak cho thấy hệ thống chậm dần theo thời gian dù không có lỗi. Tôi cũng biết cách đọc file .jtl và tìm điểm gãy qua các mốc throughput ngừng tăng và tỉ lệ lỗi tăng vọt. Việc để AI chạy các bài test giúp tôi thấy kiểm thử được thực hiện thế nào trong thực tế. Nguyên tắc tôi giữ cho các bài sau: luôn review lại output của AI, và hỏi ngược lại AI về chính những gì nó đưa ra để hiểu bài sâu hơn. (Ý của sinh viên; Claude Code diễn đạt lại.)",
}
PRIV = [  # (mục, trạng thái, ghi chú bằng chứng)
    ("I confirmed the AI Use Category assigned to this assignment.", True, "Cat. 4 – AI-Assisted Production (AI Agreement: áp dụng cho HW#00–HW#08)"),
    ("I have declared which AI tool(s) I will use in my prompt log.", True, "docs/prompt_log.md"),
    ("I have read the AI Use Agreement for this course.", True, "Sinh viên xác nhận 22/11/2026"),
    ("I understand which artifacts MUST NOT be AI-generated.", True, "Sinh viên xác nhận 22/11/2026"),
    ("I did not enter personal data of classmates, customers, or patients.", True, "Chỉ dữ liệu giả lập perf5_user_*; tên đăng nhập GitHub công khai của nhóm xuất hiện khi kiểm tra quyền repo"),
    ("I did not paste copyrighted reading materials wholesale into the AI.", True, "AI đọc đề HW05 và repo SUT công khai do giảng viên cung cấp"),
    ("I did not paste proprietary employer or open-source license-restricted code.", True, "Chỉ dùng repo SUT công khai của môn học"),
    ("I logged each prompt + AI response into prompt_log.md with timestamp.", True, "docs/prompt_log.md + docs/ai_session_transcript.txt"),
    ("All AI-generated artifacts are tagged in the AI Audit Report.", True, "15 artifact – docs/07_AI_Audit_Report.md"),
    ("All citations from AI have been verified (sources actually exist).", True, "Sinh viên xác nhận 22/11/2026"),
    ("All AI-generated code has been executed and tested.", False, "Đã chạy mọi script/test plan; riêng ci/perf-regression.yml mới kiểm tra cú pháp, chưa chạy trên GitHub Actions"),
    ("My 200–300-word AI Critique is included in the report.", True, "Sinh viên xác nhận 22/11/2026"),
    ("The Mandatory Disclosure paragraph is at the end of my report.", True, "Cuối docs/00_Main_Report.md và docs/07_AI_Audit_Report.md"),
    ("I attached the AI Use Disclosure Form.", True, "docs/09_AI_Disclosure_Form.md + ai-forms/"),
    ("I am ready for a 5–7-min random oral defense the week after submission.", True, "Sinh viên xác nhận 22/11/2026"),
]
PRIV_SECTIONS = [("1. Before I use AI", 0, 4), ("2. While I am using AI", 4, 8), ("3. Before I submit my work", 8, 15)]


def box(v):
    return "[x]" if v is True else "[ ]"


def info_md(title, rows):
    return [f"## {title}", "", "| Field | Value |", "|---|---|"] + [f"| {k} | {esc(v)} |" for k, v in rows] + [""]


def disclosure_md():
    o = ["# AI Use Disclosure Form (HW05 – Thành viên 5)", "", "> Theo mẫu **[AI-03]**; bản .docx: `ai-forms/[AI-03] AI Disclosure Form – 23120317.docx`.", ""]
    o += info_md("1. Course & Student Info", [("Course:", S["course"]), ("Assignment ID:", S["assignment_id"]), ("Assignment Title:", S["assignment_title"]),
                                             ("AI Use Category (1–5):", "Category " + S["category"]), ("Date:", S["date"]), ("Student name:", S["name"]), ("Student ID:", S["id"])])
    o += ["## 2. Disclosure Questions", ""]
    for q, a in DISC.items():
        o += [f"### {q}", "", a, ""]
    o += ["## 3. Statement of Honesty", "", "By signing below, I confirm that the disclosure above is accurate and complete. I understand that undisclosed or false disclosure of AI use is treated as academic misconduct and may result in a 0 grade for the assignment and disciplinary referral.", ""]
    o += info_md("Signature", SIGN_ROWS)
    return "\n".join(o)


def reflective_md():
    o = ["# Reflective AI Use Statement (HW05 – Thành viên 5)", "", "> Theo mẫu **[AI-04]** (bắt buộc với Category 4). Câu 5 do sinh viên tự viết.", ""]
    o += info_md("1. Project & Author Info", [("Course:", S["course"]), ("Project / Capstone title:", S["assignment_title"]),
                                             ("Team members (if group):", "Nhóm KTPM2026 (5 thành viên) – phần này của thành viên 5"),
                                             ("Student name:", S["name"]), ("Student ID:", S["id"]), ("Submission date:", S["date"])])
    o += ["## 2. Reflection Questions", ""]
    for q, a in REFL.items():
        o += [f"### {q}", "", a, ""]
    o += ["## 3. AI Categories Used", "", "- [ ] Cat. 1 – No AI", "- [ ] Cat. 2 – AI for preparation only", "- [ ] Cat. 3 – AI for feedback / revision",
          "- [x] Cat. 4 – AI-assisted production", "- [ ] Cat. 5 – AI-integrated work", "",
          "## 4. Author Signature", "", "By signing below, I confirm that this reflective statement is honest and accurately represents how AI was used in this project. I take full intellectual responsibility for the final submission.", ""]
    o += info_md("Signature", SIGN_ROWS)
    return "\n".join(o)


def privacy_md():
    o = ["# Privacy & Responsible AI Use Checklist (HW05 – Thành viên 5)", "",
         "> Theo mẫu **[AI-05]**. [x] = đã có bằng chứng; [ ] kèm \"Sinh viên tự xác nhận\" = sinh viên phải tự tick sau khi kiểm tra.", ""]
    for title, a, b in PRIV_SECTIONS:
        o += [f"## {title}", ""] + [f"- {box(v)} {t} — *{n}*" for t, v, n in PRIV[a:b]] + [""]
    o += ["## 4. Final Statement", "", "Final responsibility for the accuracy, originality, and integrity of this submission rests with me. Any undisclosed AI use is treated as academic misconduct.", ""]
    o += info_md("Signature", SIGN_ROWS)
    return "\n".join(o)


# ------------------------------------------------------------------ .docx filling
def fill_kv_table(t, rows):
    m = dict(rows)
    for r in t.rows:
        k = r.cells[0].text.strip()
        if k in m and len(r.cells) > 1:
            r.cells[-1].text = m[k]


def fill_questions(d, answers):
    """Sau mỗi Heading 3 có trong answers: ghi câu trả lời vào dòng ____ đầu tiên, xóa các dòng ____ còn lại."""
    ps = d.paragraphs
    i = 0
    while i < len(ps):
        p = ps[i]
        if p.style.name.startswith("Heading 3") and p.text.strip() in answers:
            ans = answers[p.text.strip()]
            j, first = i + 1, True
            while j < len(ps) and not ps[j].style.name.startswith("Heading"):
                if set(ps[j].text.strip()) == {"_"}:
                    if first:
                        ps[j].text = ans
                        first = False
                    else:
                        ps[j]._element.getparent().remove(ps[j]._element)
                j += 1
            ps = d.paragraphs
        i += 1


def fill_underscores_after(d, heading, text):
    ps = d.paragraphs
    for i, p in enumerate(ps):
        if p.text.strip().startswith(heading):
            first = True
            for q in ps[i + 1:]:
                if q.style.name.startswith("Heading"):
                    break
                if set(q.text.strip()) == {"_"}:
                    if first:
                        q.text = text
                        first = False
                    else:
                        q._element.getparent().remove(q._element)
            return


def replace_para(d, startswith, text):
    for p in d.paragraphs:
        if p.text.strip().startswith(startswith):
            p.text = text
            return


def tick_lines(d, mapping):
    for p in d.paragraphs:
        t = p.text.strip()
        for item, v, note in mapping:
            if t == f"[ ] {item}":
                p.text = f"{box(v)} {item}  ({note})"


def build_docx():
    FORMS.mkdir(exist_ok=True)
    tpl = {k: next(TPL.glob(f"[[]{k}]*.docx")) for k in ("AI-02", "AI-03", "AI-04", "AI-05")}

    # AI-02
    d = docx.Document(tpl["AI-02"])
    t_info, t_audit, t_sum, t_sign = d.tables
    fill_kv_table(t_info, INFO_ROWS)
    t_info.rows[-1].cells[-1].text = "[x] Yes  [ ] No"
    while len(t_audit.rows) > 1:  # xóa mẫu + hàng trống, giữ header
        t_audit._tbl.remove(t_audit.rows[1]._tr)
    for i, a in enumerate(ARTIFACTS, 1):
        cells = t_audit.add_row().cells
        cells[0].text = f"Artifact #{i}: {a['name']}\nTool/Time: {a['time']}\nPrompt: \"{a['prompt']}\""
        cells[1].text = a["output"]
        cells[2].text = a["verdict"]
        cells[3].text = a["reason"]
        cells[4].text = a["fix"]
    n, rows = counts()
    t_sum.rows[1].cells[1].text = str(n)
    if len(t_sum.rows[1].cells) > 2:
        t_sum.rows[1].cells[2].text = "100%"
    for r, (_, c, p) in zip(t_sum.rows[2:], rows):
        r.cells[1].text, r.cells[2].text = str(c), p
    fill_underscores_after(d, "Write 80–150 words", CONCLUSION)
    replace_para(d, '"[Test cases', f"\"{DISCLOSURE}\"")
    fill_kv_table(t_sign, SIGN_ROWS)
    d.save(FORMS / f"[AI-02] AI Audit Report – {S['id']}.docx")

    # AI-03
    d = docx.Document(tpl["AI-03"])
    fill_kv_table(d.tables[0], [("Assignment ID:", S["assignment_id"]), ("Assignment Title:", S["assignment_title"]),
                                ("AI Use Category (1–5):", "Category " + S["category"]), ("Date:", S["date"]),
                                ("Student name:", S["name"]), ("Student ID:", S["id"])])
    fill_questions(d, DISC)
    fill_kv_table(d.tables[1], SIGN_ROWS)
    d.save(FORMS / f"[AI-03] AI Disclosure Form – {S['id']}.docx")

    # AI-04
    d = docx.Document(tpl["AI-04"])
    fill_kv_table(d.tables[0], [("Project / Capstone title:", S["assignment_title"]), ("Team members (if group):", "Nhóm KTPM2026 – thành viên 5"),
                                ("Student name:", S["name"]), ("Student ID:", S["id"]), ("Submission date:", S["date"])])
    fill_questions(d, REFL)
    for p in d.paragraphs:
        if p.text.strip() == "[ ] Cat. 4 – AI-assisted production":
            p.text = "[x] Cat. 4 – AI-assisted production"
    fill_kv_table(d.tables[1], SIGN_ROWS)
    d.save(FORMS / f"[AI-04] AI Reflective Statement – {S['id']}.docx")

    # AI-05
    d = docx.Document(tpl["AI-05"])
    tick_lines(d, PRIV)
    fill_kv_table(d.tables[0], SIGN_ROWS)
    d.save(FORMS / f"[AI-05] AI Privacy Checklist – {S['id']}.docx")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    (DOCS / "prompt_log.md").write_text(prompt_log_md(), encoding="utf-8")
    (DOCS / "07_AI_Audit_Report.md").write_text(audit_md(), encoding="utf-8")
    (DOCS / "09_AI_Disclosure_Form.md").write_text(disclosure_md(), encoding="utf-8")
    (DOCS / "10_AI_Reflective_Statement.md").write_text(reflective_md(), encoding="utf-8")
    (DOCS / "11_AI_Privacy_Checklist.md").write_text(privacy_md(), encoding="utf-8")
    build_docx()
    print("ok:", *sorted(p.name for p in FORMS.glob("*.docx")), sep="\n  ")
