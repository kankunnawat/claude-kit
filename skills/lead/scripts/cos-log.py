#!/usr/bin/env python3
"""Append one timed Log line to a record or an area file, or rotate old lines.

Usage: cos-log.py <record.md> <text-file>
       cos-log.py --rotate <record.md> [days]
The text file holds the line without a time. Newlines collapse to spaces.
--rotate moves Log lines older than <days> (default 7) to
<record-stem>.log-<YYYY-MM>.md beside the record, by each line's own month,
appending, and prints each archive path. It reads only the Log section, up to
the next "## " heading. Unstamped lines directly under a moved line (up to a
blank line) move with it. It writes each archive through a temp file, skips
an entry the archive already holds, and checks the archive before it rewrites
the record, so a rerun after a failed run adds no duplicate. It changes
nothing when no line is old. COS_LOG_TODAY=YYYY-MM-DD sets today (for the
test).
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
    end = next((i for i in range(heading + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    keep, moved, entry = lines[: heading + 1], {}, None
    for line in lines[heading + 1 : end]:
        match = STAMP.match(line)
        if match and match.group(1) < cutoff:
            entry = []
            moved.setdefault(match.group(1)[:7], []).append(entry)
        elif match or not line.strip():
            entry = None
        if entry is None:
            keep.append(line)
        else:
            entry.append(line if line.endswith("\n") else line + "\n")
    keep += lines[end:]
    if not moved:
        print("rotated=0")
        return 0
    for month, entries in sorted(moved.items()):
        archive = record.with_name(f"{record.stem}.log-{month}.md")
        try:
            held = archive.read_text() if archive.exists() else ""
            if held and not held.endswith("\n"):
                held += "\n"
            texts = ["".join(e) for e in entries]
            new = [t for t in texts if "\n" + t not in "\n" + held]
            temp = archive.with_name(archive.name + ".rotating")
            temp.write_text(held + "".join(new))
            os.replace(temp, archive)
            written = "\n" + archive.read_text()
        except OSError as error:
            print(f"archive write failed, record unchanged: {archive}: {error}", file=sys.stderr)
            return 1
        if any("\n" + t not in written for t in texts):
            print(f"archive check failed, record unchanged: {archive}", file=sys.stderr)
            return 1
        print(f"archive={archive}")
    temp = record.with_name(record.name + ".rotating")
    temp.write_text("".join(keep))
    os.replace(temp, record)
    print(f"rotated={sum(len(e) for es in moved.values() for e in es)}")
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
