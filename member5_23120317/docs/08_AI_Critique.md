# 08 – AI Critique (Thành viên 5 – Nguyễn Đức Phát, 23120317)

AI sai ở ba chỗ tôi thấy đáng chú ý nhất. Thứ nhất, khi sinh test plan JMeter, AI dùng Groovy mà không kiểm tra máy tôi chạy JDK 25, nên lần chạy thử đầu tiên lỗi "Unsupported class file major version 69". Thứ hai, script giám sát tài nguyên do AI viết in số CPU có dấu phẩy phân cách hàng nghìn (ví dụ "1,065.9"), làm vỡ cột trong file CSV. AI vẫn đọc file đó và báo CPU tiến trình node là 113%, trong khi đúng ra chỉ khoảng 54% trung bình, 90% lúc cao nhất. Thứ ba, ở Task 2, AI đề xuất các cách tối ưu kèm những con số lợi ích như "nhanh hơn 3–4 lần" hay "tăng 20–40% năng lực" mà không có phép đo nào chứng minh.

Nguyên nhân chung là AI lấy con số nhận được rồi đưa thẳng vào báo cáo, không có bước giám sát hay kiểm tra lại. Với con số CPU, AI tin vào kết quả script trả về mà không tự hỏi con số đó có hợp lý không, cũng không để ý đến định dạng số của PowerShell. Với Groovy, AI không kiểm tra môi trường thật. Với các con số lợi ích, vì tôi hỏi "lợi ích kỳ vọng" nên AI điền một con số cho đủ câu trả lời, dựa vào kiến thức chung chứ không dựa vào đo đạc.

Nguyên tắc tôi rút ra là khi làm việc với AI luôn phải có con người giám sát và kiểm tra lại các số liệu nó đưa ra, đối chiếu với dữ liệu gốc như file .jtl. Ngoài ra, sau khi AI làm xong, tôi sẽ yêu cầu nó tự rà soát lại toàn bộ kết quả trước khi tôi chấp nhận.

<!-- Nội dung do sinh viên trả lời qua 3 câu hỏi (prompt log #14–#17); Claude Code chỉ diễn đạt lại thành đoạn văn (Category 3 – feedback/revision). -->
