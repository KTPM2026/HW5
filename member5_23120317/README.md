# HW05 – Performance Testing – Thành viên 5

**Nguyễn Đức Phát – MSSV 23120317**
**Workflow 5:** Login → View Order History → Browse Products → Add to Cart → Checkout (truy xuất lịch sử đơn hàng và tạo đơn mới)
**Công cụ:** Apache JMeter 5.6.3 · Node.js 22 · SUT: [eshop-sut](https://github.com/ttbhanh/eshop-sut)
**Video demo (Unlisted):** https://youtu.be/Y2VKcs27d3Y

## Test summary report

| Hạng mục | Kết quả |
|---|---|
| Kịch bản đã chạy | Load (50 VU), Stress (100→500 VU), Spike (20→320 VU) – chính thức 22/11/2026, có video. Stress breakpoint (400→2000 VU) và Soak 15 phút – khảo sát 19/11/2026 |
| Nhóm endpoint | Auth-heavy: `POST /api/login` · Read-heavy: `GET /api/orders/my-orders`, `/api/products`, `/api/products?search=`, `/api/products/:id` · Transactional: `POST/GET /api/cart`, `POST /api/checkout` |
| Dữ liệu | CSV 500 tài khoản + 1.500 đơn lịch sử (`data/`), sinh bằng `scripts/prepare_data.js` |
| Load | 8.268 request, 23,2 RPS, p95 5 ms, 0% lỗi |
| Stress | 193.203 request, đỉnh ~735 RPS, p95 45 ms (bậc 500 VU: 80–90 ms), 0% lỗi |
| Spike | 13 → ~202 → 13 RPS, p95 6–7 ms, 0% lỗi, hồi phục ngay |
| **Ngưỡng chịu tải** | Throughput tối đa **~900–950 RPS** (SLA p95 ≤ 500 ms tới ~400 VU); bão hòa từ 800 VU; **gãy ở ~1.100–1.200 VU** (connection refused) |
| **Ngưỡng bền (soak 15 phút)** | **~540 RPS**, 0% lỗi, p95 tổng 244 ms nhưng trôi 47 → 393 ms; RAM node tối đa **127 MB** (đỉnh tuyệt đối 188 MB khi quá tải) |
| Bug / performance issue | 6 (xem `docs/05_GitHub_Issues.md` và GitHub Issues) |

## Cấu trúc

| Thư mục / file | Nội dung |
|---|---|
| `docs/01_API_Survey.md` | Khảo sát API Login, Order History, Products, Cart, Checkout |
| `docs/02_Test_Design.md` | Thiết kế 3 kịch bản, tham số, SLA, xử lý lockout |
| `docs/03_Results_Analysis.md` | Kết quả, nguyên nhân gốc, đề xuất tối ưu (đã kiểm chứng) |
| `docs/task2/` | Task 2: prompt, output AI nguyên văn, review diễn giải sai |
| `docs/05_GitHub_Issues.md` | Nội dung 6 issue ([GitHub Issues #2–#7](https://github.com/KTPM2026/HW5/issues)) |
| `docs/06_Task3_Continuous_Performance_Testing.md` | Task 3: lưu đồ, cổng hồi quy p95, đánh đổi chi phí / báo động giả |
| `ci/` | `perf-regression.yml` (GitHub Actions mẫu), `baseline.json` |
| `skill/perf-testing-workflow/SKILL.md` | Agent Skill tái sử dụng quy trình cho nhóm endpoint khác |
| `docs/07_AI_Audit_Report.md` | AI Audit Report |
| `docs/08_AI_Critique.md` | AI Critique (200–300 từ) |
| `docs/ai_session_transcript.txt` | Transcript đầy đủ phiên Claude Code (`/export`) |
| `pdf/` | Bản PDF của báo cáo chính, AI Critique, AI Audit Report |
| `test-plans/` | `23120317_{Load,Stress,Spike,Soak}_20261119.jmx` |
| `data/` | `users.csv`, `products.csv` |
| `results/<plan>/` | `.jtl`, `html-report/`, `node_resource.csv`, `analysis.md` |
| `evidence/` | dxdiag, ảnh tool + Task Manager, ảnh 3 report view |
| `scripts/` | Sinh test plan, chuẩn bị dữ liệu, reset lockout, chạy, phân tích, đo index, cổng hồi quy `perf_gate.py`, vẽ biểu đồ |

> Hai file `.jtl` > 50 MB (Soak, Stress breakpoint) không đưa lên GitHub. Chúng được nén nộp kèm trên Moodle.

## Self-assessment

> Agent Skill: đã có `skill/perf-testing-workflow/SKILL.md` nhưng chưa có video demo dùng skill trên một nhóm endpoint hoàn chỉnh như đề yêu cầu → tự chấm 0.

| No. | Criteria | Grade | Self-assessed |
|---|---|---:|---:|
| 1 | Task 1 – Load testing | 30 | 30 |
| 2 | Task 1 – Stress testing | 20 | 20 |
| 3 | Task 1 – Spike testing | 20 | 20 |
| 4 | Task 2 – AI analysis + misinterpretation hunt | 10 | 10 |
| 5 | Task 3 – Continuous Performance Testing proposal | 10 | 10 |
| 6 | Agent Skills | 10 | 0 |
| | **Total** | **100** | **90** |
