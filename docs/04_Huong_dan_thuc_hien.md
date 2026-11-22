# 04 – Hướng dẫn thực hiện phần Người 5 (MSSV 23120317)

> Lệnh `bash` chạy trong **Git Bash**, thư mục gốc `D:\University\Testing\HW05`.

## Bước 1 – Chụp cấu hình máy (2 phút)

`Win+R` → `dxdiag` → chụp tab **System** (thấy *Computer Name: VICTUS16*) → bấm **Save All Information** lưu `member5/evidence/dxdiag.txt`.

## Bước 2 – Quay video (1 lần quay, 1 lệnh, ~20 phút)

**Đề chỉ yêu cầu:** video ≥ 6 phút, thấy tool (JMeter) và Task Manager trong cùng khung hình, giọng bạn thuyết minh tiếng Việt.

1. **Mở server** (Git Bash cửa sổ 1, để nguyên):
   ```bash
   cd /d/University/Testing/HW05/eshop-sut/backend && node server.js
   ```
   > Nếu báo port 3000 đã dùng: server cũ vẫn chạy – dùng luôn, bỏ qua bước này.
2. **Mở Task Manager** (`Ctrl+Shift+Esc`) → tab **Performance** (hoặc **Details**, tìm `node.exe`). Đặt cạnh cửa sổ Git Bash thứ 2.
3. **Bấm quay** (`Win+Alt+R` bằng Xbox Game Bar, hoặc OBS – nhớ bật micro).
4. **Git Bash cửa sổ 2:**
   ```bash
   cd /d/University/Testing/HW05/member5 && bash scripts/record_demo.sh
   ```
   Script tự chuẩn bị dữ liệu (nếu cần), reset khóa tài khoản rồi chạy **Load → Stress → Spike** liên tiếp, xuất `.jtl` + HTML report cho từng kịch bản.
5. **Thuyết minh ngắn** khi mỗi banner `1/3`, `2/3`, `3/3` hiện ra (gợi ý bên dưới), rồi chờ tới `XONG` → dừng quay.
6. Trong lúc chạy, chụp **1 ảnh màn hình mỗi kịch bản** (`Win+Shift+S`) → `member5/evidence/Load.png`, `Stress.png`, `Spike.png`.
7. Upload YouTube chế độ **Unlisted**. Video dài có thể tua nhanh đoạn giữa, chỉ cần giữ giọng thuyết minh.

**Gợi ý thuyết minh (nói tự nhiên theo ý mình):**
- *Mở đầu:* "Em là Nguyễn Đức Phát, 23120317. Workflow 5: đăng nhập, xem lịch sử đơn hàng, xem sản phẩm, thêm vào giỏ, thanh toán. Bên trái là JMeter, bên phải là Task Manager theo dõi tiến trình node."
- *Load:* "50 người dùng, mỗi bước nghỉ 1–3 giây. Dòng summary cho thấy khoảng 25 request/giây, lỗi 0%, CPU node rất thấp."
- *Stress:* "Cứ 90 giây tăng thêm 100 người dùng, tới 500. Throughput tăng theo, thời gian phản hồi bắt đầu tăng ở bậc 300 người dùng, CPU node tăng rõ."
- *Spike:* "20 người dùng nền, tới giây 120 có thêm 300 người dùng trong 5 giây, sau 60 giây rút ra. Hệ thống không lỗi và trở lại bình thường ngay."
- *Kết:* "Kết quả nằm trong thư mục results, mỗi kịch bản có file .jtl và HTML report."

> Soak 15 phút và Stress breakpoint **không cần quay**. Đã có kết quả trong `results/`; muốn chạy lại thì chạy `bash scripts/run_scenario.sh Soak` lúc nào rảnh.

## Bước 3 – Chụp 3 report view (5 phút)

Mở JMeter GUI (`D:/Tools/apache-jmeter-5.6.3/bin/jmeter.bat`) → **File → Open** test plan → bấm vào listener → **Browse...** chọn file `.jtl` tương ứng trong `results/` → chụp:

| Test plan | Listener |
|---|---|
| `23120317_Load_20261119.jmx` | Summary Report |
| `23120317_Stress_20261119.jmx` | Aggregate Report |
| `23120317_Spike_20261119.jmx` | View Results Tree |

## Bước 4 – Cập nhật số liệu

Gửi cho Claude các file `results/*/analysis.md` mới (hoặc tự chạy `python scripts/analyze_jtl.py ...`) để cập nhật `docs/03_Results_Analysis.md`. Bạn phải **tự kiểm tra lại từng con số**.

## Bước 5 – Task 2, Issues, Git

- **Task 2:** mở một phiên AI **mới**, đưa `analysis.md` cho nó phân tích. Lưu nguyên văn prompt/output. So với §6 và §7 trong `03_Results_Analysis.md` để chỉ ra chỗ AI đọc sai và đề xuất nào khả thi.
- **GitHub Issues:** 5 issue theo §8 `03_Results_Analysis.md`, kèm ảnh.
- **Git:** commit theo từng bước (khảo sát API, dữ liệu, từng test plan, kết quả, phân tích), rồi chạy `git log --stat > git_commit_log.txt`. File `.jtl` lớn (breakpoint ~250 MB) không đưa lên GitHub mà nén nộp Moodle.

## Checklist

- [ ] Ảnh dxdiag + `dxdiag.txt`
- [ ] Link video YouTube (Unlisted)
- [ ] 3 ảnh terminal + Task Manager (Load / Stress / Spike)
- [ ] 3 ảnh report view (Summary / Aggregate / View Results Tree)
- [ ] `results/` có `.jtl` + `html-report/` mỗi kịch bản
- [ ] `03_Results_Analysis.md` đã cập nhật và tự kiểm tra
- [ ] AI Audit log, GitHub Issues, `git_commit_log.txt`
