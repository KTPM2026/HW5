# Task 2 – Prompt gửi AI phân tích

- **Công cụ:** Claude Code – subagent `general-purpose` (Claude Opus 5.5), phiên mới, không kế thừa ngữ cảnh
- **Thời gian:** 22/11/2026 ~15:35 (GMT+7)
- **Chủ đích:** AI chỉ nhận dữ liệu thô + mã nguồn, **không** được xem báo cáo `03_Results_Analysis.md` của nhóm, để phân tích độc lập.

```text
Bạn là chuyên gia performance testing. Tôi đã chạy JMeter (CLI) trên một backend e-commerce
(Node.js + Express + SQLite) với workflow 8 bước: 01 Login → 02 View Order History →
03 Browse Products → 04 Search Products → 05 Product Detail → 06 Add to Cart → 07 View Cart →
08 Checkout. JMeter và server chạy cùng một laptop (Ryzen 5 6600H 6 core/12 thread, 16 GB RAM, Windows 11).

Dữ liệu (chỉ đọc, KHÔNG sửa file nào):
- Mã nguồn backend: eshop-sut\backend\server.js và database.js
- Tóm tắt từng lần chạy (thống kê theo request, timeline, phân loại lỗi, RAM/CPU tiến trình node):
  Load / Stress / Stress mạnh (400→2000 VU) / Spike / Soak 15 phút: results\<plan>\analysis.md
- Có thể xem vài dòng đầu file .jtl gốc trong cùng thư mục nếu cần (file lớn, đừng đọc hết).

Hãy trả lời lần lượt 3 câu hỏi, mỗi câu một mục riêng, bằng tiếng Việt:

Câu 1. Phân tích kết quả từng kịch bản (Load, Stress, Stress mạnh, Spike, Soak): hệ thống hoạt động
thế nào, có vấn đề gì? Đề xuất ngưỡng hiệu năng (p95, error rate, throughput) phù hợp cho hệ thống này.

Câu 2. Điểm gãy (breaking point) của hệ thống ở đâu, nguyên nhân gây lỗi là gì? Hệ thống có ổn định
khi chạy lâu (soak) không?

Câu 3. Đề xuất các tối ưu cụ thể cho backend này (ví dụ index database, connection pool, SQLite WAL,
cache, cluster...), mỗi đề xuất nêu lợi ích kỳ vọng.
```
