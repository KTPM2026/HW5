# Appendix A – prompt_log.md (Thành viên 5 – 23120317)

- **Công cụ:** Claude Code v2.1.329 (CLI, Windows) – model Claude Opus 5.5 (claude-opus-5-5), Anthropic – trợ lý chính, chạy dạng agent (đọc file, chạy lệnh, ghi file)
- **Subagent:** Claude Code subagent `general-purpose` (Claude Opus 5.5) – phiên mới không kế thừa ngữ cảnh, dùng cho Task 2 (AI phân tích .jtl)
- **Output nguyên văn:** `docs/ai_session_transcript.txt` (xuất bằng `/export` của Claude Code). Cột *Dòng* là số dòng bắt đầu lượt đó trong transcript.
- **Thời gian:** giờ địa phương GMT+7; transcript không ghi giờ nên giờ được ước lượng từ thời điểm tạo file/commit trong lượt đó (`git_commit_log.txt`).

| # | Thời gian | Prompt (nguyên văn) | Dòng | AI đã làm |
|---:|---|---|---:|---|
| 1 | 19/11/2026 ~21:35 | Đọc HW05, tôi là thành viên 5, chịu trách nhiệm về các phần sau: Người 5 Workflow 5 Login → View Order History → Browse Products → Add to Cart → Checkout Truy xuất lịch sử đơn hàng và tạo đơn mới / Người 5 – Kiểm thử lịch sử đơn hàng / Phụ trách: 1. Khảo sát API đăng nhập. 2. Khảo sát API Order History. 3. Khảo sát API sản phẩm. 4. Khảo sát API Cart. 5. Khảo sát API Checkout. 6. Chuẩn bị dữ liệu tài khoản và đơn hàng. 7. Thiết kế và chạy 3 kịch bản Performance Testing. 8. Phân tích kết quả và đề xuất tối ưu. | 10 | Đọc đề, clone SUT, khảo sát API, viết script dữ liệu, sinh test plan |
| 2 | 19/11/2026 ~22:58 | Máy tôi có Jmeter rồi, ở D/Tools | 121 | Dùng JMeter có sẵn; smoke test lỗi Groovy/JDK 25 → sửa __jexl3; chạy Load/Stress/Spike lần 1 |
| 3 | 19/11/2026 ~23:05 | 1. MSSV: 23120317, tên: Nguyễn Đức Phát. 2. Có bắt buộc tôi phải tự chạy không, hay bạn chạy cho tôi được ? | 253 | Đổi tên test plan theo MSSV; giải thích phần bắt buộc sinh viên tự làm |
| 4 | 19/11/2026 ~23:25 | cập nhật cho tôi đi | 423 | Báo kết quả, chạy Stress breakpoint, sửa assertion message, chạy Soak |
| 5 | 19/11/2026 ~23:55 | phần bạn xong chưa, hãy đưa ra hướng dẫn chi tiết các bước làm phần của tôi đi. | 666 | Phân tích Soak, đo index trên bản sao DB, viết báo cáo + hướng dẫn |
| 6 | 22/11/2026 ~14:55 | làm phần quay video này đơn giản hơn đi, nó đang khá phức tạp so với đề bài yêu cầu | 767 | Viết record_demo.sh, rút gọn hướng dẫn quay |
| 7 | 22/11/2026 ~15:30 | ok tôi làm xong bước 2 trong file rồi, các file cần có tôi đã lưu ở root, làm cho tôi từ bước 3 đi. | 1158 | Phân tích lần chạy chính thức, cắt ảnh từ video, Task 2 (subagent), soạn issue, Git |
| 8 | 22/11/2026 ~15:40 | đặt tiêu đề video là gì | 1264 | Đề xuất tiêu đề + mô tả YouTube |
| 9 | 22/11/2026 ~15:42 | tôi mở jmeter rồi, hoặc bạn tự mở rồi chụp report giúp tôi, tôi cấp toàn quyền. | 1822 | Mở JMeter GUI, chụp 3 report view |
| 10 | 22/11/2026 ~15:55 | https://github.com/KTPM2026/HW5 https://youtu.be/Y2VKcs27d3Y | 1968 | Fork + PR #1, vẽ biểu đồ, đăng issue #2–#7, README |
| 11 | 22/11/2026 ~16:00 | ok làm đi | 2116 | Task 3, Agent Skill, AI Audit Report, bản nháp AI Critique |
| 12 | 22/11/2026 ~16:09 | ok tôi xuất rồi, điền hộ cho tôi full điểm trừ Agent skill, sau đó zip và đưa tôi file nộp | (sau khi export) | Điền tự đánh giá 90, PDF, đóng gói zip |
| 13 | 22/11/2026 ~16:13 | Xem lại D:\University\Testing\HW05\AI Templates-20261122T091219Z-1-001.zip, và tuân thủ theo đi. Rà soát bài nộp một lần nữa xem có thiếu gì không. | (sau khi export) | Đối chiếu 6 template, viết lại Audit Report theo AI-02, thêm Disclosure/Reflective/Privacy, prompt log, ảnh trang Issues |
| 14 | 22/11/2026 ~16:25 | hỏi tôi từng câu cho tôi trả lời rồi paraphrase lại đưa vô | (sau khi export) | Hỏi lần lượt các câu cho Critique / Reflective / bug report / checklist |
| 15 | 22/11/2026 ~16:27 | - CPU báo 113% do script giám sát đọc sai. - AI ở Task 2 đưa con số lợi ích (×3–4, +20–40%) không có số đo. - Test plan dùng Groovy nên chạy lỗi trên JDK 25. | (sau khi export) | Ghi nhận – Critique câu 1 |
| 16 | 22/11/2026 ~16:29 | (Critique câu 2 – chọn lại 3 nguyên nhân gợi ý) + "Thêm nữa là AI chỉ lấy số nó nhận được rồi bỏ vào, không có giám sát hay double check" | (sau khi export) | Ghi nhận – Critique câu 2 |
| 17 | 22/11/2026 ~16:31 | Khi làm việc với AI phải có con người giám sát và double check lại các số liệu nó đưa ra, yêu cầu AI check lại toàn bộ khi làm xong. | (sau khi export) | Diễn đạt lại thành AI Critique 298 từ |
| 18 | 22/11/2026 ~16:34 | - Hiểu ra sự khác nhau giữa Load, Stress, Spike và Soak khi nhìn số liệu thật. - Biết cách đọc file .jtl, hoặc biết cách tìm điểm gãy. AI chạy các bài test để hiểu hơn về cách kiểm thử được thực hiện, các bài sau sẽ giữ nguyên tắt review lại output của AI, và hỏi lại AI từ những output nó đưa ra để hiểu bài hơn. | (sau khi export) | Diễn đạt lại thành Reflective câu 5 |
| 19 | 22/11/2026 ~16:36 | API này trả về toàn bộ đơn, trong khi chỉ cần một số ít đơn, không có phân trang. Toàn bộ đơn được truy vấn làm tăng đỗ trễ và kích thước response | (sau khi export) | Giữ nguyên văn làm mô tả Issue #2 (chỉ sửa chính tả) |
| 20 | 22/11/2026 ~16:38 | Còn nhiều không, đưa ra hết để tôi trả lời một lượt. | (sau khi export) | Liệt kê các câu còn lại |
| 21 | 22/11/2026 ~16:40 | (Mô tả Issue #3–#7 do sinh viên viết – nguyên văn trong docs/05_GitHub_Issues.md, mục "Mô tả") + "Phần 4 xác nhận có hết cho tôi." | (sau khi export) | Cập nhật nguyên văn mô tả issue #3–#7 lên GitHub; tick Privacy Checklist |

## Subagent Task 2

| Thời gian | Prompt | Output |
|---|---|---|
| 22/11/2026 ~15:35 | `docs/task2/ai_analysis_prompt.md` (nguyên văn) | `docs/task2/ai_analysis_output_raw.md` (nguyên văn) |
