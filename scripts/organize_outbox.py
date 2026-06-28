#!/usr/bin/env python3
"""Normalize root-level outbox reports into date folders."""

from __future__ import annotations

from wislib import ROOT, organize_outbox


def main() -> int:
    moved = organize_outbox()
    if not moved:
        print("No root-level reports needed moving.")
        return 0
    print(f"Moved {len(moved)} report(s):")
    for src, dst in moved:
        print(f"- {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
