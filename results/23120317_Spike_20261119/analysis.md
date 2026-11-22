# Phân tích `23120317_Spike_20261119.jtl`

- Tổng sample: **15247**, thời lượng: **298s**, max active threads: **320**

## 1. Thống kê theo request

| Label | n | Error % | Avg (ms) | p50 | p90 | p95 | p99 | Max | Throughput (/s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 01 Login | 2004 | 0.00% | 3.4 | 3 | 6 | 7 | 13 | 32 | 6.7 |
| 02 View Order History | 1997 | 0.00% | 4.6 | 4 | 7 | 8 | 11 | 23 | 6.7 |
| 03 Browse Products | 1991 | 0.00% | 1.5 | 1 | 3 | 4 | 8 | 16 | 6.7 |
| 04 Search Products | 1966 | 0.00% | 1.3 | 1 | 2 | 4 | 6 | 12 | 6.6 |
| 05 Product Detail | 1925 | 0.00% | 1.3 | 1 | 2 | 3 | 6 | 10 | 6.5 |
| 06 Add to Cart | 1858 | 0.00% | 1.5 | 1 | 2 | 3 | 4 | 6 | 6.2 |
| 07 View Cart | 1784 | 0.00% | 1.4 | 1 | 2 | 2 | 4 | 12 | 6.0 |
| 08 Checkout | 1722 | 0.00% | 5.2 | 5 | 7 | 8 | 12 | 36 | 5.8 |
| **TOTAL** | 15247 | 0.00% | 2.5 | 2 | 5 | 6 | 9 | 36 | 51.1 |

## 2. Timeline (cửa sổ 30s)

| Window | Threads | RPS | Avg (ms) | p95 | Max | Error % |
|---|---:|---:|---:|---:|---:|---:|
| 0-30s | 20 | 11.5 | 3.2 | 6 | 36 | 0.00% |
| 30-60s | 20 | 13.2 | 2.9 | 6 | 21 | 0.00% |
| 60-90s | 20 | 13.6 | 2.6 | 5 | 10 | 0.00% |
| 90-120s | 110 | 13.3 | 2.3 | 6 | 9 | 0.00% |
| 120-150s | 320 | 201.3 | 2.4 | 6 | 32 | 0.00% |
| 150-180s | 320 | 203.0 | 2.5 | 7 | 23 | 0.00% |
| 180-210s | 20 | 13.3 | 2.5 | 6 | 7 | 0.00% |
| 210-240s | 20 | 13.0 | 2.6 | 6 | 10 | 0.00% |
| 240-270s | 20 | 13.4 | 2.4 | 6 | 8 | 0.00% |
| 270-300s | 20 | 12.6 | 2.5 | 6 | 11 | 0.00% |

- Đơn hàng tạo thành công (08 Checkout OK): **1722** (~5.77 đơn/s)

## 3. Phân loại lỗi

Không có lỗi.

## 4. Tài nguyên tiến trình backend (node, port 3000)

- RAM (Working Set): đầu **64.7 MB**, đỉnh **102.8 MB**, cuối **74.0 MB**
- CPU trung bình ≈ **9%**, đỉnh (giữa 2 mẫu) ≈ **46%** (100% = 1 logical core; có thể >100% vì sqlite3 chạy trên libuv threadpool, nhưng JS/JSON/JWT chỉ dùng 1 luồng event loop)

