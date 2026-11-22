# Reflective AI Use Statement (HW05 – Thành viên 5)

> Theo mẫu **[AI-04]** (bắt buộc với Category 4). Câu 5 do sinh viên tự viết.

## 1. Project & Author Info

| Field | Value |
|---|---|
| Course: | CS423 / CSC13003 – Software Testing |
| Project / Capstone title: | HW05 – Performance Testing (Workflow 5: Login → View Order History → Browse Products → Add to Cart → Checkout) |
| Team members (if group): | Nhóm KTPM2026 (5 thành viên) – phần này của thành viên 5 |
| Student name: | Nguyễn Đức Phát |
| Student ID: | 23120317 |
| Submission date: | 22/11/2026 |

## 2. Reflection Questions

### 1. How did AI support your work?

AI làm trợ lý agent trong toàn bộ quy trình: đọc mã SUT để khảo sát 5 API, sinh dữ liệu CSV và test plan JMeter, chạy JMeter CLI và thu RAM/CPU, tính thống kê và timeline từ .jtl, kiểm chứng đề xuất index trên bản sao DB, soạn tài liệu, đề xuất mô hình kiểm thử liên tục kèm cổng hồi quy p95, và một AI phiên mới phân tích độc lập cho Task 2.

### 2. What did you accept, reject, or revise from AI outputs?

Chấp nhận: dữ liệu CSV, cổng perf_gate.py, ảnh report view (đã đối chiếu số mẫu). Từ chối/sửa: Groovy → __jexl3; message assertion "403 = khóa tài khoản"; tham số Stress (thêm breakpoint) và Soak (150 → 400 VU); format CPU N1 → F1; các số sai trong báo cáo (CPU 113%, 95% lỗi). Từ Task 2 giữ 9 đề xuất feasible, loại khẳng định "WAL bắt buộc cho cluster" và 5 hệ số lợi ích không có phép đo.

### 3. What errors, biases, or limitations did you notice in the AI outputs?

Không kiểm tra môi trường (JDK 25); ước lượng thấp năng lực SUT; gán sẵn nguyên nhân lỗi trong assertion; đọc sai CSV do định dạng số; trộn kết quả hai phiên chạy khác ngày; tự đặt SLA sau khi xem kết quả; quy nút thắt cho event loop dù số đo theo bước chỉ ra hàng đợi SQLite; đưa hệ số lợi ích (×3–4, +20–40%) không có phép đo; lỗi cú pháp YAML.

### 4. How did you verify information, sources, or claims provided by AI?

Chạy trên SUT thật (smoke + 3 lần chính thức có video), đối chiếu với .jtl/console.txt/pre_run_db.txt, kiểm chứng bug bằng curl, đo lại tối ưu trên bản sao DB, so sánh với phân tích của một AI phiên mới, kiểm tra tài liệu SQLite về locking/WAL.

### 5. What did you learn through this project that you could not have learned by simply accepting AI output?

Nhìn số liệu thật từ các lần chạy, tôi hiểu rõ sự khác nhau giữa bốn loại kiểm thử: Load cho biết hệ thống ở tải bình thường (50 VU, p95 5 ms), Stress đẩy dần để tìm điểm gãy (bão hòa khoảng 900–950 RPS, gãy ở khoảng 1.100 VU), Spike xem hệ thống chịu và hồi phục sau đột biến, còn Soak cho thấy hệ thống chậm dần theo thời gian dù không có lỗi. Tôi cũng biết cách đọc file .jtl và tìm điểm gãy qua các mốc throughput ngừng tăng và tỉ lệ lỗi tăng vọt. Việc để AI chạy các bài test giúp tôi thấy kiểm thử được thực hiện thế nào trong thực tế. Nguyên tắc tôi giữ cho các bài sau: luôn review lại output của AI, và hỏi ngược lại AI về chính những gì nó đưa ra để hiểu bài sâu hơn. (Ý của sinh viên; Claude Code diễn đạt lại.)

## 3. AI Categories Used

- [ ] Cat. 1 – No AI
- [ ] Cat. 2 – AI for preparation only
- [ ] Cat. 3 – AI for feedback / revision
- [x] Cat. 4 – AI-assisted production
- [ ] Cat. 5 – AI-integrated work

## 4. Author Signature

By signing below, I confirm that this reflective statement is honest and accurately represents how AI was used in this project. I take full intellectual responsibility for the final submission.

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
