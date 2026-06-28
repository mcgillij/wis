#!/usr/bin/env python3
"""Shared helpers for the While I Sleep filesystem queue."""

from __future__ import annotations

import re
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "inbox"
COMPLETE = INBOX / "complete"
OUTBOX = ROOT / "outbox"
RUNS = ROOT / "runs"
ACTIVE_EXTS = (".md", ".txt")
DATE_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})(?:[-_](?P<rest>.+))?$")


@dataclass(frozen=True)
class Report:
    path: Path
    date: str
    title: str
    size: int
    mtime: float

    @property
    def relpath(self) -> str:
        return self.path.relative_to(ROOT).as_posix()

    @property
    def filename(self) -> str:
        return self.path.name


def ensure_dirs() -> None:
    for path in (INBOX, COMPLETE, OUTBOX, RUNS):
        path.mkdir(parents=True, exist_ok=True)


def slugify(value: str, max_len: int = 90) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return (slug[:max_len].strip("-") or "item")


def titleize_slug(value: str) -> str:
    stem = Path(value).stem
    match = DATE_RE.match(stem)
    if match and match.group("rest"):
        stem = match.group("rest")
    return stem.replace("-", " ").replace("_", " ").strip().title() or stem


def unique_path(directory: Path, stem: str, suffix: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    candidate = directory / f"{stem}{suffix}"
    counter = 2
    while candidate.exists():
        candidate = directory / f"{stem}-{counter}{suffix}"
        counter += 1
    return candidate


def write_inbox_item(title: str, body: str) -> Path:
    ensure_dirs()
    day = datetime.now().strftime("%Y-%m-%d")
    path = unique_path(INBOX, f"{day}-{slugify(title)}", ".md")
    path.write_text(f"# {title.strip()}\n\n{body.strip()}\n", encoding="utf-8")
    return path


def active_inbox_items() -> list[Path]:
    ensure_dirs()
    return sorted(
        p for p in INBOX.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in ACTIVE_EXTS
    )


def completed_items() -> list[Path]:
    ensure_dirs()
    return sorted(
        p for p in COMPLETE.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in ACTIVE_EXTS
    )


def run_notes() -> list[Path]:
    ensure_dirs()
    return sorted((p for p in RUNS.glob("*.md") if p.is_file() and not p.name.startswith(".")), reverse=True)


def date_from_report_path(path: Path) -> str | None:
    if path.parent.parent == OUTBOX and re.match(r"^\d{4}-\d{2}-\d{2}$", path.parent.name):
        return path.parent.name
    match = DATE_RE.match(path.stem)
    if match:
        return match.group("date")
    return None


def report_path_for_slug(slug: str, day: str | None = None) -> Path:
    day = day or datetime.now().strftime("%Y-%m-%d")
    return unique_path(OUTBOX / day, slugify(slug), ".html")


def all_report_files() -> list[Path]:
    ensure_dirs()
    reports: list[Path] = []
    for path in OUTBOX.rglob("*.html"):
        if not path.is_file() or path.name.startswith("."):
            continue
        # Static index files are navigation aids, not generated research reports.
        if path.name == "index.html":
            continue
        reports.append(path)
    return sorted(reports, key=lambda p: (date_from_report_path(p) or "0000-00-00", p.name), reverse=True)


def reports_by_date() -> dict[str, list[Report]]:
    grouped: dict[str, list[Report]] = defaultdict(list)
    for path in all_report_files():
        day = date_from_report_path(path) or datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
        stat = path.stat()
        grouped[day].append(Report(path=path, date=day, title=titleize_slug(path.name), size=stat.st_size, mtime=stat.st_mtime))
    return {day: sorted(items, key=lambda r: r.path.name) for day, items in sorted(grouped.items(), reverse=True)}


def legacy_root_reports() -> list[Path]:
    ensure_dirs()
    return sorted(
        p for p in OUTBOX.glob("*.html")
        if p.is_file() and not p.name.startswith(".") and p.name != "index.html"
    )


def organize_outbox() -> list[tuple[Path, Path]]:
    """Move root-level HTML reports into outbox/YYYY-MM-DD/ folders.

    Existing reports named YYYY-MM-DD-slug.html become outbox/YYYY-MM-DD/slug.html.
    Undated reports fall back to their filesystem mtime date and keep their slug.
    """
    ensure_dirs()
    moved: list[tuple[Path, Path]] = []
    for src in legacy_root_reports():
        day = date_from_report_path(src) or datetime.fromtimestamp(src.stat().st_mtime).strftime("%Y-%m-%d")
        stem = src.stem
        prefix = f"{day}-"
        if stem.startswith(prefix):
            stem = stem[len(prefix):] or "report"
        dst = unique_path(OUTBOX / day, slugify(stem), src.suffix)
        shutil.move(str(src), str(dst))
        moved.append((src, dst))
    return moved
