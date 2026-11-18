#!/usr/bin/env python3
"""Append one timed Log line to a CoS day record.

Usage: cos-log.py <record.md> <text-file>
The text file holds the line without a time. Newlines collapse to spaces.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: cos-log.py <record.md> <text-file>", file=sys.stderr)
        return 2
    record, source = Path(sys.argv[1]), Path(sys.argv[2])
    if not record.is_file():
        print(f"record not found: {record}", file=sys.stderr)
        return 2
    text = " ".join(source.read_text().split())
    if text.startswith("- "):
        text = text[2:]
    if not text:
        print("empty log line", file=sys.stderr)
        return 2
    stamp = datetime.now(timezone.utc).strftime("%H:%MZ")
    with record.open("a") as handle:
        handle.write(f"- {stamp} {text}\n")
    print(stamp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
