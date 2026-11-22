#!/usr/bin/env python3
"""
Cổng hồi quy hiệu năng (Task 3): so sánh p95 theo từng request của 1 lần chạy với baseline.

  # tạo/cập nhật baseline từ 1 lần chạy tốt trên main
  python scripts/perf_gate.py baseline results/<run>/<run>.jtl -o ci/baseline.json
  # kiểm tra 1 lần chạy mới
  python scripts/perf_gate.py check results/<run>/<run>.jtl -b ci/baseline.json [--rel 0.20 --abs 5 --err 1.0]

Quy tắc đánh dấu REGRESSION cho mỗi label (cả 2 điều kiện cùng đúng – để tránh báo động giả):
  p95_new > p95_base * (1 + rel)     (tăng tương đối, mặc định 20%)
  p95_new - p95_base > abs_ms        (tăng tuyệt đối, mặc định 5 ms – "sàn nhiễu")
hoặc error% tăng quá --err điểm phần trăm.
Exit code: 0 = PASS, 1 = REGRESSION, 2 = lỗi đầu vào.
"""
import argparse
import csv
import json
import math
import sys
from collections import defaultdict


def p95(vals):
    vals = sorted(vals)
    return vals[max(0, math.ceil(0.95 * len(vals)) - 1)]


def summarize(jtl):
    by = defaultdict(list)
    err = defaultdict(int)
    for r in csv.DictReader(open(jtl, encoding="utf-8")):
        by[r["label"]].append(int(r["elapsed"]))
        err[r["label"]] += r["success"] != "true"
    return {k: {"n": len(v), "p95": p95(v), "err_pct": round(100 * err[k] / len(v), 3)} for k, v in sorted(by.items())}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["baseline", "check"])
    ap.add_argument("jtl")
    ap.add_argument("-o", "--out")
    ap.add_argument("-b", "--baseline")
    ap.add_argument("--rel", type=float, default=0.20)
    ap.add_argument("--abs", dest="abs_ms", type=float, default=5.0)
    ap.add_argument("--err", type=float, default=1.0)
    a = ap.parse_args()

    cur = summarize(a.jtl)
    if a.mode == "baseline":
        json.dump({"source": a.jtl, "labels": cur}, open(a.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"Baseline ghi vào {a.out} ({len(cur)} label)")
        return 0

    base = json.load(open(a.baseline, encoding="utf-8"))["labels"]
    failed = 0
    print("| Label | p95 base | p95 mới | Δ | err% base→mới | Kết quả |\n|---|---:|---:|---:|---:|---|")
    for label, b in base.items():
        c = cur.get(label)
        if not c:
            print(f"| {label} | {b['p95']} | — | — | — | ❌ THIẾU (request không chạy) |")
            failed += 1
            continue
        d = c["p95"] - b["p95"]
        slow = c["p95"] > b["p95"] * (1 + a.rel) and d > a.abs_ms
        errs = c["err_pct"] - b["err_pct"] > a.err
        verdict = "❌ REGRESSION" if (slow or errs) else ("⚠️ tăng nhưng trong ngưỡng nhiễu" if d > 0 and c["p95"] > b["p95"] * (1 + a.rel) else "✅")
        failed += slow or errs
        print(f"| {label} | {b['p95']} | {c['p95']} | {d:+d} | {b['err_pct']}→{c['err_pct']} | {verdict} |")
    print(f"\n**{'REGRESSION' if failed else 'PASS'}** – {failed} label vi phạm (ngưỡng: +{a.rel:.0%} và +{a.abs_ms:g} ms, hoặc lỗi +{a.err:g} điểm %)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
