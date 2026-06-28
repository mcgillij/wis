#!/usr/bin/env python3
"""Show the While I Sleep queue status."""

from __future__ import annotations

from wislib import ROOT, active_inbox_items, completed_items, reports_by_date, run_notes


def main() -> int:
    queued = active_inbox_items()
    complete = completed_items()
    grouped_reports = reports_by_date()
    reports = [report for items in grouped_reports.values() for report in items]
    runs = run_notes()

    print("While I Sleep queue status")
    print(f"root:     {ROOT}")
    print(f"queued:   {len(queued)}")
    print(f"complete: {len(complete)}")
    print(f"reports:  {len(reports)} across {len(grouped_reports)} day(s)")
    print(f"runs:     {len(runs)}")

    if queued:
        print("\nQueued items:")
        for path in queued:
            print(f"- {path.relative_to(ROOT)}")

    if grouped_reports:
        print("\nOutbox days:")
        for day, items in grouped_reports.items():
            print(f"- {day}: {len(items)} report(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
