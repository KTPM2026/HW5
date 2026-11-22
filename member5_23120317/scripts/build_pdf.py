#!/usr/bin/env python3
"""Ghép báo cáo chính (Markdown) và xuất PDF bằng Chrome headless.
   python scripts/build_pdf.py  -> docs/00_Main_Report.md, pdf/*.pdf
"""
import re
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
MAIN_PARTS = ["README.md", "docs/01_API_Survey.md", "docs/02_Test_Design.md", "docs/03_Results_Analysis.md",
              "docs/task2/ai_analysis_review.md", "docs/06_Task3_Continuous_Performance_Testing.md",
              "docs/05_GitHub_Issues.md", "docs/08_AI_Critique.md"]

CSS = """
body{font-family:'Segoe UI',Arial,sans-serif;font-size:10.5pt;line-height:1.5;color:#1f2937;max-width:100%;margin:0}
h1{font-size:18pt;border-bottom:2px solid #2563eb;padding-bottom:4px;margin-top:28px}
h2{font-size:14pt;color:#1e3a8a;margin-top:22px}h3{font-size:12pt}
table{border-collapse:collapse;width:100%;margin:8px 0;font-size:9pt;page-break-inside:auto}
th,td{border:1px solid #d1d5db;padding:3px 6px;vertical-align:top}th{background:#eff6ff}
code{background:#f3f4f6;padding:0 3px;border-radius:3px;font-size:9pt}
pre{background:#f3f4f6;padding:8px;border-radius:4px;white-space:pre-wrap;font-size:8.5pt}
pre code{background:none;padding:0}
blockquote{border-left:3px solid #93c5fd;margin:8px 0;padding:2px 10px;color:#374151;background:#f8fafc}
img{max-width:100%}.pb{page-break-before:always}
@page{size:A4;margin:16mm 14mm}
"""


def to_html(md_text, title):
    md_text = re.sub(r"<!--.*?-->", "", md_text, flags=re.S)
    # Mermaid không render ổn định trong Chrome headless -> thay bằng ảnh đã render sẵn (docs/img)
    img = (ROOT / "docs/img/task3_flowchart.png").as_uri()
    md_text = re.sub(r"```mermaid\n.*?```", f'<img src="{img}" style="max-height:230mm;display:block;margin:auto">',
                     md_text, flags=re.S)
    md_text = re.sub(r"\n> Bản ảnh của lưu đồ.*?\n", "\n", md_text)
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "md_in_html"])
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title><style>{CSS}</style>
</head><body>{body}</body></html>"""


def pdf(html_text, out):
    tmp = out.with_suffix(".html")
    tmp.write_text(html_text, encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=15000",
                    f"--print-to-pdf={out}", tmp.as_uri()], check=True, capture_output=True)
    tmp.unlink()
    print("wrote", out.relative_to(ROOT), f"{out.stat().st_size // 1024} KB")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    (ROOT / "pdf").mkdir(exist_ok=True)
    parts = []
    for i, p in enumerate(MAIN_PARTS):
        txt = (ROOT / p).read_text(encoding="utf-8")
        parts.append(("" if i == 0 else '\n\n<div class="pb"></div>\n\n') + txt)
    main_md = ("# HW05 – Performance Testing – Báo cáo chính (Thành viên 5 – 23120317)\n\n"
               "> File ghép tự động từ README và các tài liệu trong `docs/` bằng `scripts/build_pdf.py`.\n\n"
               + "".join(parts))
    (ROOT / "docs/00_Main_Report.md").write_text(main_md, encoding="utf-8")
    pdf(to_html(main_md, "23120317 HW05 Main Report"), ROOT / "pdf/23120317_HW05_Main_Report.pdf")
    for src, name in [("docs/08_AI_Critique.md", "23120317_HW05_AI_Critique.pdf"),
                      ("docs/07_AI_Audit_Report.md", "23120317_HW05_AI_Audit_Report.pdf")]:
        pdf(to_html((ROOT / src).read_text(encoding="utf-8"), name), ROOT / "pdf" / name)


if __name__ == "__main__":
    main()
