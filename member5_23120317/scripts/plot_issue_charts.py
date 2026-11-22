#!/usr/bin/env python3
"""Vẽ biểu đồ minh họa cho GitHub Issues từ .jtl gốc (Soak và Stress breakpoint).
   python scripts/plot_issue_charts.py  -> evidence/issue_*.png
"""
import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "evidence"
INK, MUTED, GRID = "#1f2937", "#6b7280", "#e5e7eb"
C1, C2 = "#2563eb", "#dc2626"


def p95(v):
    v = sorted(v)
    return v[max(0, math.ceil(0.95 * len(v)) - 1)] if v else 0


def windows(jtl, sec):
    rows = list(csv.DictReader(open(jtl, encoding="utf-8")))
    t0 = min(int(r["timeStamp"]) for r in rows)
    w = defaultdict(list)
    for r in rows:
        w[(int(r["timeStamp"]) - t0) // (sec * 1000)].append(r)
    return [w[k] for k in sorted(w)]


def style(ax, title, xlabel):
    ax.set_title(title, loc="left", fontsize=12, color=INK, fontweight="bold")
    ax.set_xlabel(xlabel, color=MUTED)
    ax.grid(True, color=GRID, linewidth=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED)


# 1. Soak: p95 Order History vs Browse Products theo phút + kích thước response
soak = ROOT / "results/23120317_Soak_20261119/23120317_Soak_20261119.jtl"
ws = windows(soak, 60)
mins = [i + 1 for i in range(len(ws))]
oh = [p95([int(r["elapsed"]) for r in w if r["label"] == "02 View Order History"]) for w in ws]
br = [p95([int(r["elapsed"]) for r in w if r["label"] == "03 Browse Products"]) for w in ws]
kb = [sum(int(r["bytes"]) for r in w if r["label"] == "02 View Order History")
      / max(1, sum(r["label"] == "02 View Order History" for r in w)) / 1024 for w in ws]
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.2), dpi=130)
a.plot(mins, oh, color=C1, lw=2, label="02 View Order History")
a.plot(mins, br, color=MUTED, lw=2, ls="--", label="03 Browse Products")
a.set_ylabel("p95 (ms)", color=MUTED)
a.legend(frameon=False)
style(a, "Soak 400 VU – p95 tăng dần theo thời gian", "phút")
b.plot(mins, kb, color=C1, lw=2)
b.set_ylabel("KB / response", color=MUTED)
style(b, "Kích thước response my-orders", "phút")
fig.tight_layout()
fig.savefig(OUT / "issue1_soak_order_history.png")

# 2. Breakpoint: VU, RPS thành công và error % theo 30s
bp = ROOT / "results/23120317_Stress_20261119_breakpoint/23120317_Stress_20261119.jtl"
ws = windows(bp, 30)[:-1]
t = [(i + 1) * 30 for i in range(len(ws))]
vu = [max(int(r["allThreads"]) for r in w) for w in ws]
ok = [sum(r["success"] == "true" for r in w) / 30 for w in ws]
err = [100 * sum(r["success"] != "true" for r in w) / len(w) for w in ws]
fig, a = plt.subplots(figsize=(12, 4.4), dpi=130)
a.plot(t, ok, color=C1, lw=2, label="Request thành công / s (goodput)")
a.plot(t, vu, color=MUTED, lw=1.5, ls="--", label="Active VU")
a.set_ylabel("req/s  ·  VU", color=MUTED)
b = a.twinx()
b.plot(t, err, color=C2, lw=2, label="Error %")
b.set_ylabel("Error %", color=C2)
b.set_ylim(0, 100)
b.spines["top"].set_visible(False)
h1, l1 = a.get_legend_handles_labels()
h2, l2 = b.get_legend_handles_labels()
a.legend(h1 + h2, l1 + l2, frameon=False, loc="center left")
style(a, "Stress 400→2000 VU – goodput sụp, lỗi tăng vọt từ ~1.100 VU", "giây")
fig.tight_layout()
fig.savefig(OUT / "issue4_breakpoint.png")
print("ok")
