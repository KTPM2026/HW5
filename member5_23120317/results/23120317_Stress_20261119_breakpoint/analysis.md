# Phân tích `23120317_Stress_20261119.jtl`

- Tổng sample: **765531**, thời lượng: **451s**, max active threads: **2000**

## 1. Thống kê theo request

| Label | n | Error % | Avg (ms) | p50 | p90 | p95 | p99 | Max | Throughput (/s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 01 Login | 567676 | 94.91% | 398.2 | 236 | 528 | 590 | 3316 | 30512 | 1258.9 |
| 02 View Order History | 28599 | 0.06% | 1282.5 | 829 | 2780 | 5512 | 10910 | 14535 | 63.4 |
| 03 Browse Products | 28515 | 0.09% | 1269.5 | 826 | 2745 | 5492 | 10910 | 14564 | 63.2 |
| 04 Search Products | 28419 | 0.10% | 1275.7 | 830 | 2817 | 5654 | 10861 | 14567 | 63.0 |
| 05 Product Detail | 28323 | 0.11% | 1313.4 | 839 | 2796 | 5755 | 11205 | 14661 | 62.8 |
| 06 Add to Cart | 28256 | 0.97% | 450.6 | 275 | 959 | 1796 | 3573 | 22989 | 62.7 |
| 07 View Cart | 27937 | 0.47% | 430.9 | 269 | 803 | 1611 | 3733 | 16633 | 62.0 |
| 08 Checkout | 27806 | 0.39% | 1168.4 | 813 | 2148 | 4676 | 8251 | 14367 | 61.7 |
| **TOTAL** | 765531 | 70.46% | 561.2 | 275 | 946 | 1321 | 6979 | 30512 | 1697.7 |

## 2. Timeline (cửa sổ 30s)

| Window | Threads | RPS | Avg (ms) | p95 | Max | Error % |
|---|---:|---:|---:|---:|---:|---:|
| 0-30s | 400 | 840.6 | 144.9 | 355 | 539 | 0.00% |
| 30-60s | 400 | 966.7 | 312.9 | 468 | 626 | 0.00% |
| 60-90s | 409 | 918.6 | 335.4 | 505 | 759 | 0.00% |
| 90-120s | 800 | 906.3 | 575.2 | 953 | 1599 | 0.00% |
| 120-150s | 800 | 868.9 | 819.3 | 1293 | 1964 | 0.00% |
| 150-180s | 818 | 853.7 | 838.4 | 1301 | 1803 | 0.00% |
| 180-210s | 1200 | 1063.2 | 857.7 | 2252 | 4070 | 23.72% |
| 210-240s | 1200 | 2207.6 | 468.9 | 2171 | 12981 | 73.23% |
| 240-270s | 1300 | 1919.6 | 512.3 | 3198 | 16839 | 90.23% |
| 270-300s | 1600 | 2370.9 | 535.7 | 2544 | 25277 | 91.77% |
| 300-330s | 1600 | 2590.7 | 483.3 | 323 | 22180 | 95.86% |
| 330-360s | 1982 | 2571.5 | 560.1 | 1345 | 30156 | 94.77% |
| 360-390s | 2000 | 2517.2 | 619.4 | 441 | 30464 | 97.44% |
| 390-420s | 2000 | 2465.6 | 644.2 | 612 | 30512 | 98.23% |
| 420-450s | 2000 | 2456.3 | 651.0 | 629 | 25743 | 98.03% |
| 450-480s | 1583 | 0.3 | 174.7 | 199 | 199 | 100.00% |

- Đơn hàng tạo thành công (08 Checkout OK): **27698** (~61.42 đơn/s)

## 3. Phân loại lỗi

| Label | Code | Message | Count |
|---|---:|---:|---:|
| 01 Login | Non HTTP response code: org.apache.http.conn.HttpHostConnectException | Sai HTTP status (403 = tài khoản bị khóa / token sai) | 534586 |
| 01 Login | Non HTTP response code: java.net.BindException | Sai HTTP status (403 = tài khoản bị khóa / token sai) | 3999 |
| 06 Add to Cart | Non HTTP response code: org.apache.http.conn.HttpHostConnectException | Sai HTTP status (403 = tài khoản bị khóa / token sai) | 275 |
| 01 Login | Non HTTP response code: java.net.SocketTimeoutException | Sai HTTP status (403 = tài khoản bị khóa / token sai) | 198 |
| 07 View Cart | Non HTTP response code: org.apache.http.conn.HttpHostConnectException | Sai HTTP status (403 = tài khoản bị khóa / token sai) | 122 |
| 08 Checkout | Non HTTP response code: org.apache.http.conn.HttpHostConnectException | Sai HTTP status (403 = tài khoản bị khóa / token sai) | 108 |
| 05 Product Detail | Non HTTP response code: java.net.SocketException | Sai HTTP status (403 = tài khoản bị khóa / token sai) | 30 |
| 04 Search Products | Non HTTP response code: java.net.SocketException | Sai HTTP status (403 = tài khoản bị khóa / token sai) | 29 |
| 03 Browse Products | Non HTTP response code: java.net.SocketException | Sai HTTP status (403 = tài khoản bị khóa / token sai) | 27 |
| 02 View Order History | Non HTTP response code: java.net.SocketException | Sai HTTP status (403 = tài khoản bị khóa / token sai) | 16 |
| 07 View Cart | Non HTTP response code: java.net.SocketException | Sai HTTP status (403 = tài khoản bị khóa / token sai) | 8 |

## 4. Tài nguyên tiến trình backend (node, port 3000)

- RAM (Working Set): đầu **68.4 MB**, đỉnh **188.5 MB**, cuối **111.4 MB**
- CPU trung bình ≈ **67%**, đỉnh (giữa 2 mẫu) ≈ **126%** (100% = 1 logical core; có thể >100% vì sqlite3 chạy trên libuv threadpool, nhưng JS/JSON/JWT chỉ dùng 1 luồng event loop)

