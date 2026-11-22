#!/usr/bin/env python3
"""
Phân tích file .jtl (CSV) của JMeter -> bảng Markdown, dùng làm "giá trị gốc" để đối chiếu với phân tích của AI.

  python scripts/analyze_jtl.py results/<plan>/<plan>.jtl [--window 30] [--resource results/<plan>/node_resource.csv]

In ra:
  1. Bảng thống kê theo label: n, err%, avg, p50, p90, p95, p99, max, throughput
  2. Timeline theo cửa sổ thời gian: active threads, RPS, avg, p95, err%
  3. Phân loại lỗi theo label + response code + message
  4. (tùy chọn) RAM/CPU tiến trình node
"""
import argparse
import collections
import csv
import math
from pathlib import Path


def pct(sorted_vals, p):
    if not sorted_vals:
        return 0
    k = max(0, math.ceil(p / 100 * len(sorted_vals)) - 1)  # nearest-rank (giống JMeter)
    return sorted_vals[k]


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---:" if i else "---" for i in range(len(headers))) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def stats_row(label, samples, dur_s):
    el = sorted(int(s["elapsed"]) for s in samples)
    err = sum(s["success"] != "true" for s in samples)
    return [label, len(samples), f"{100 * err / len(samples):.2f}%", f"{sum(el) / len(el):.1f}",
            pct(el, 50), pct(el, 90), pct(el, 95), pct(el, 99), el[-1], f"{len(samples) / dur_s:.1f}"]


def main():
    import sys; sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("jtl")
    ap.add_argument("--window", type=int, default=30)
    ap.add_argument("--resource")
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.jtl, encoding="utf-8")))
    rows.sort(key=lambda r: int(r["timeStamp"]))
    t0 = int(rows[0]["timeStamp"])
    t_end = max(int(r["timeStamp"]) + int(r["elapsed"]) for r in rows)
    dur = (t_end - t0) / 1000

    print(f"# Phân tích `{Path(a.jtl).name}`\n")
    print(f"- Tổng sample: **{len(rows)}**, thời lượng: **{dur:.0f}s**, "
          f"max active threads: **{max(int(r['allThreads']) for r in rows)}**\n")

    by = collections.defaultdict(list)
    for r in rows:
        by[r["label"]].append(r)
    H = ["Label", "n", "Error %", "Avg (ms)", "p50", "p90", "p95", "p99", "Max", "Throughput (/s)"]
    body = [stats_row(k, v, dur) for k, v in sorted(by.items())] + [stats_row("**TOTAL**", rows, dur)]
    print("## 1. Thống kê theo request\n")
    print(table(H, body) + "\n")

    print(f"## 2. Timeline (cửa sổ {a.window}s)\n")
    win = collections.defaultdict(list)
    for r in rows:
        win[(int(r["timeStamp"]) - t0) // (a.window * 1000)].append(r)
    tl = []
    for w in sorted(win):
        s = win[w]
        el = sorted(int(x["elapsed"]) for x in s)
        tl.append([f"{w * a.window}-{(w + 1) * a.window}s", max(int(x["allThreads"]) for x in s),
                   f"{len(s) / a.window:.1f}", f"{sum(el) / len(el):.1f}", pct(el, 95), el[-1],
                   f"{100 * sum(x['success'] != 'true' for x in s) / len(s):.2f}%"])
    print(table(["Window", "Threads", "RPS", "Avg (ms)", "p95", "Max", "Error %"], tl) + "\n")

    # checkout transactions per second ~ "business throughput"
    co = by.get("08 Checkout", [])
    if co:
        ok = sum(r["success"] == "true" for r in co)
        print(f"- Đơn hàng tạo thành công (08 Checkout OK): **{ok}** (~{ok / dur:.2f} đơn/s)\n")

    errs = collections.Counter(
        (r["label"], r["responseCode"], (r.get("failureMessage") or r["responseMessage"])[:90])
        for r in rows if r["success"] != "true")
    print("## 3. Phân loại lỗi\n")
    if errs:
        print(table(["Label", "Code", "Message", "Count"], [[*k, v] for k, v in errs.most_common(15)]) + "\n")
    else:
        print("Không có lỗi.\n")

    if a.resource and Path(a.resource).exists():
        # bản cũ của monitor dùng định dạng N1 -> "1,065.9" làm vỡ CSV; ghép lại các cột thừa
        res = []
        for line in open(a.resource, encoding="utf-8").read().splitlines()[1:]:
            parts = line.split(",")
            if len(parts) >= 3:
                res.append({"time": parts[0], "working_set_MB": parts[1], "cpu_seconds": "".join(parts[2:])})
        if res:
            ws = [float(r["working_set_MB"]) for r in res]
            cpu = [float(r["cpu_seconds"].replace(",", "")) for r in res]
            # dùng cột thời gian thật (mỗi lần gọi powershell mất thêm ~1s nên chu kỳ không đúng 5s)
            secs = []
            for r in res:
                h, m, s_ = map(int, r["time"].split(":"))
                secs.append(h * 3600 + m * 60 + s_)
            span = max(1, secs[-1] - secs[0])
            print("## 4. Tài nguyên tiến trình backend (node, port 3000)\n")
            print(f"- RAM (Working Set): đầu **{ws[0]:.1f} MB**, đỉnh **{max(ws):.1f} MB**, cuối **{ws[-1]:.1f} MB**")
            deltas = [100 * (cpu[i + 1] - cpu[i]) / max(1, secs[i + 1] - secs[i]) for i in range(len(cpu) - 1)]
            print(f"- CPU trung bình ≈ **{100 * (cpu[-1] - cpu[0]) / span:.0f}%**, "
                  f"đỉnh (giữa 2 mẫu) ≈ **{max(deltas or [0]):.0f}%** "
                  "(100% = 1 logical core; có thể >100% vì sqlite3 chạy trên libuv threadpool, "
                  "nhưng JS/JSON/JWT chỉ dùng 1 luồng event loop)\n")


if __name__ == "__main__":
    main()
