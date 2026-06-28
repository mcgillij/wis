#!/usr/bin/env python3
"""Add an item to the While I Sleep inbox."""

from __future__ import annotations

import argparse

from wislib import write_inbox_item


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("title", help="Short title for the inbox item")
    parser.add_argument("body", nargs="*", help="Prompt/body text. If omitted, read from stdin.")
    args = parser.parse_args()

    body = " ".join(args.body).strip()
    if not body:
        try:
            body = input().strip()
        except EOFError:
            body = ""
    if not body:
        parser.error("body text is required, either as arguments or stdin")

    path = write_inbox_item(args.title, body)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
