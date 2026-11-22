#!/usr/bin/env bash
# Chạy 1 kịch bản: reset lockout -> JMeter CLI -> .jtl + HTML report + snapshot RAM tiến trình node
#   bash scripts/run_scenario.sh Load|Stress|Spike|Soak [extra -J props...]
set -euo pipefail
KIND="$1"; shift || true
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JMETER="${JMETER_HOME:-D:/Tools/apache-jmeter-5.6.3}/bin/jmeter.bat"
PLAN=$(ls "$ROOT"/test-plans/*_"${KIND}"_*.jmx | head -1)
NAME=$(basename "$PLAN" .jmx)
OUT="$ROOT/results/$NAME${RUN_TAG:+_$RUN_TAG}"
rm -rf "$OUT"; mkdir -p "$OUT"

echo "== [$NAME] reset lockout (FR-02) =="
node "$ROOT/scripts/reset_lockout.js" --report | tee "$OUT/pre_run_db.txt"

echo "time,working_set_MB,cpu_seconds" > "$OUT/node_resource.csv"
# Ghi RAM/CPU của tiến trình node (backend) mỗi 5s trong suốt lần chạy
( while true; do
    powershell -NoProfile -Command "Get-Process -Id (Get-NetTCPConnection -LocalPort 3000 -State Listen).OwningProcess | ForEach-Object { '{0},{1},{2:F1}' -f (Get-Date -Format HH:mm:ss), [math]::Round(\$_.WS/1MB,1), \$_.CPU }" >> "$OUT/node_resource.csv" 2>/dev/null
    sleep 5
  done ) &
MON=$!
trap 'kill $MON 2>/dev/null || true' EXIT

cd "$ROOT/test-plans"
"$JMETER" -n -t "$PLAN" -l "$OUT/$NAME.jtl" -j "$OUT/jmeter.log" -e -o "$OUT/html-report" \
  -Jjmeter.reportgenerator.apdex_satisfied_threshold=500 \
  -Jjmeter.reportgenerator.apdex_tolerated_threshold=1500 "$@" | tee "$OUT/console.txt"

node "$ROOT/scripts/reset_lockout.js" --report | tee "$OUT/post_run_db.txt"
echo "== done: $OUT =="
