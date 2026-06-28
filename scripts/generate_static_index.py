#!/usr/bin/env python3
"""Generate static browsable index pages for the WIS inbox and outbox."""

from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path

from wislib import ROOT, OUTBOX, active_inbox_items, completed_items, reports_by_date, run_notes

CSS = """
:root { color-scheme: dark; --bg:#0f1220; --panel:#171a2c; --muted:#a9b1d6; --text:#e6e8f5; --accent:#7aa2f7; --border:#2b3151; }
body { margin:0; font-family: Inter, system-ui, -apple-system, Segoe UI, sans-serif; background:var(--bg); color:var(--text); }
main { max-width: 1120px; margin: 0 auto; padding: 2rem; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 1rem 1.2rem; margin: 1rem 0; }
.grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }
ul { padding-left: 1.2rem; }
.muted { color: var(--muted); }
.badge { display:inline-block; padding:.15rem .45rem; border:1px solid var(--border); border-radius:999px; color:var(--muted); font-size:.85rem; }
""".strip()


def page(title: str, body: str) -> str:
    generated = datetime.now().isoformat(timespec="seconds")
    return f"""<!doctype html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{html.escape(title)}</title><style>{CSS}</style></head>
<body><main><header><h1>{html.escape(title)}</h1><p class=\"muted\">Generated {generated}</p></header>{body}</main></body></html>\n"""


def rel_link(from_dir: Path, target: Path) -> str:
    return html.escape(target.relative_to(from_dir).as_posix() if target.is_relative_to(from_dir) else target.relative_to(ROOT).as_posix())


def generate_indexes() -> list[Path]:
    grouped = reports_by_date()
    queued = active_inbox_items()
    complete = completed_items()
    runs = run_notes()
    written: list[Path] = []

    day_cards = []
    for day, reports in grouped.items():
        day_index = OUTBOX / day / "index.html"
        report_items = "\n".join(
            f'<li><a href="{html.escape(report.filename)}">{html.escape(report.title)}</a> <span class="badge">{report.size // 1024} KB</span></li>'
            for report in reports
        )
        day_index.write_text(page(f"WIS outbox — {day}", f'<p><a href="../index.html">← All days</a></p><div class="card"><h2>{len(reports)} report(s)</h2><ul>{report_items}</ul></div>'), encoding="utf-8")
        written.append(day_index)
        day_cards.append(f'<li><a href="{html.escape(day)}/index.html">{html.escape(day)}</a> <span class="badge">{len(reports)} report(s)</span></li>')

    queued_items = "\n".join(f"<li>{html.escape(p.name)}</li>" for p in queued) or '<li class="muted">No active inbox items.</li>'
    complete_items = "\n".join(f"<li>{html.escape(p.name)}</li>" for p in complete[-20:]) or '<li class="muted">No completed items.</li>'
    run_items = "\n".join(f"<li>{html.escape(p.name)}</li>" for p in runs[:10]) or '<li class="muted">No run notes.</li>'
    days = "\n".join(day_cards) or '<li class="muted">No reports yet.</li>'
    body = f"""
<div class=\"grid\">
  <section class=\"card\"><h2>Inbox</h2><p><span class=\"badge\">{len(queued)} queued</span> <span class=\"badge\">{len(complete)} complete</span></p><h3>Queued</h3><ul>{queued_items}</ul><h3>Recently completed</h3><ul>{complete_items}</ul></section>
  <section class=\"card\"><h2>Outbox by day</h2><ul>{days}</ul></section>
  <section class=\"card\"><h2>Recent runs</h2><ul>{run_items}</ul></section>
</div>
"""
    index = OUTBOX / "index.html"
    index.write_text(page("WIS inbox/outbox index", body), encoding="utf-8")
    written.append(index)
    return written


def main() -> int:
    written = generate_indexes()
    print(f"Generated {len(written)} index page(s):")
    for path in written:
        print(f"- {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
