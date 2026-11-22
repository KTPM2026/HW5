# 08 – AI Critique (Thành viên 5 – Nguyễn Đức Phát, 23120317)

AI làm tốt phần cơ học (đọc mã, sinh test plan, chạy JMeter, tính thống kê), nhưng sai ở chỗ cần phán đoán. AI dùng Groovy mà không kiểm tra JDK nên test lỗi ngay lần đầu. Nó ước lượng thấp năng lực hệ thống, khiến kịch bản Stress 500 VU không tìm được điểm gãy. Nó còn tự viết message assertion "403 = tài khoản bị khóa", làm bảng lỗi trông như sự cố khóa tài khoản, trong khi thực tế toàn là lỗi kết nối. Ở Task 2, AI đọc đúng số liệu nhưng diễn giải sai ngữ cảnh. Nó nối hai phiên chạy khác ngày thành một chuỗi. Nó tự đặt ngưỡng 200 ms sau khi xem kết quả để chấm Soak "không đạt". Nó quy nút thắt cho event loop dù số đo theo từng bước cho thấy hàng đợi SQLite mới là phần lớn. Nó cũng đưa ra năm con số lợi ích ("×3–4", "+20–40%") không có phép đo nào.

AI không tự phát hiện các lỗi này vì nó suy luận từ kiến thức chung về Node.js và SQLite, thay vì đối chiếu với dữ liệu thô như `pre_run_db.txt`, `timeStamp`, lỗi theo từng label. Prompt của tôi cũng thiếu ngữ cảnh: không nêu SLA định trước và không nói các lần chạy thuộc hai phiên. Khi được hỏi về "lợi ích kỳ vọng", AI có xu hướng điền một con số cho trọn câu trả lời.

Nguyên tắc tôi rút ra: mọi kết luận của AI phải truy về được một dòng trong log gốc. Con số nào không có phép đo thì đánh dấu là giả thuyết. Muốn AI phân tích tốt, prompt phải mang theo ngữ cảnh thực nghiệm, không chỉ dữ liệu.

<!-- ~285 từ. Bản nháp do AI soạn từ các lỗi đã ghi nhận; sinh viên cần đọc lại, sửa theo trải nghiệm và giọng văn của mình trước khi nộp. -->
