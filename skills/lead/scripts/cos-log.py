#!/usr/bin/env python3
"""Append one timed Log line to a record or an area file, or rotate old lines.

Usage: cos-log.py <record.md> <text-file>
       cos-log.py --rotate <record.md> [days]
The text file holds the line without a time. Newlines collapse to spaces.
--rotate moves Log lines older than <days> (default 7) to
<record-stem>.log-<YYYY-MM>.md beside the record, by each line's own month,
appending. It writes and checks the archive before it rewrites the record,
and changes nothing when no line is old. COS_LOG_TODAY=YYYY-MM-DD sets today
(for the test).
"""
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

STAMP = re.compile(r"^- (\d{4}-\d{2}-\d{2}) \d{2}:\d{2}Z ")


def rotate(record: Path, days: int) -> int:
    today = date.fromisoformat(os.environ.get("COS_LOG_TODAY") or datetime.now(timezone.utc).date().isoformat())
    cutoff = (today - timedelta(days=days)).isoformat()
    lines = record.read_text().splitlines(keepends=True)
    heading = next((i for i, line in enumerate(lines) if line.rstrip() == "## Log"), None)
    if heading is None:
        print(f"no Log heading in {record}", file=sys.stderr)
        return 2
    keep, moved = lines[: heading + 1], {}
    for line in lines[heading + 1 :]:
        match = STAMP.match(line)
        if match and match.group(1) < cutoff:
            moved.setdefault(match.group(1)[:7], []).append(line if line.endswith("\n") else line + "\n")
        else:
            keep.append(line)
    if not moved:
        print("rotated=0")
        return 0
    for month, block in sorted(moved.items()):
        archive = record.with_name(f"{record.stem}.log-{month}.md")
        text = "".join(block)
        with archive.open("a") as handle:
            handle.write(text)
        if not archive.read_text().endswith(text):
            print(f"archive check failed, record unchanged: {archive}", file=sys.stderr)
            return 1
    temp = record.with_name(record.name + ".rotating")
    temp.write_text("".join(keep))
    os.replace(temp, record)
    print(f"rotated={sum(len(b) for b in moved.values())}")
    return 0


def main() -> int:
    if len(sys.argv) in (3, 4) and sys.argv[1] == "--rotate":
        record = Path(sys.argv[2])
        days = sys.argv[3] if len(sys.argv) == 4 else "7"
        if not record.is_file() or not days.isdigit():
            print("usage: cos-log.py --rotate <record.md> [days]", file=sys.stderr)
            return 2
        return rotate(record, int(days))
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
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    with record.open("a") as handle:
        handle.write(f"- {stamp} {text}\n")
    print(stamp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
