#!/usr/bin/env bash
# Chạy liền Load -> Stress -> Spike để quay video 1 lần duy nhất (~20 phút).
#   bash scripts/record_demo.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

banner() { echo; echo "#############################################################"; echo "###  $1"; echo "#############################################################"; echo; }

# 1. Server phải đang chạy
curl -sf localhost:3000/api/products >/dev/null || { echo "Server chưa chạy: mở terminal khác và chạy  cd eshop-sut/backend && node server.js"; exit 1; }

# 2. Dữ liệu: nếu chưa có user test (server vừa khởi động lại) thì tự tạo
if ! curl -sf -H 'Content-Type: application/json' -d '{"email":"perf5_user_001@eshop.test","password":"Perf5@1234"}' localhost:3000/api/login >/dev/null; then
  banner "Chuẩn bị dữ liệu: 500 user, mỗi user 3 đơn"
  node scripts/prepare_data.js --users 500 --orders 3
fi

banner "1/3  LOAD   – 50 VU, khoảng 6 phút"
bash scripts/run_scenario.sh Load

banner "2/3  STRESS – tăng dần 100 -> 500 VU, khoảng 8 phút"
bash scripts/run_scenario.sh Stress

banner "3/3  SPIKE  – 20 VU, đột biến +300 VU tại giây 120, khoảng 5 phút"
bash scripts/run_scenario.sh Spike

banner "XONG – kết quả trong thư mục results/"
ls -d results/*_20261119
