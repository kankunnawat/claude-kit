#!/usr/bin/env python3
"""Tests for cos-log.py --rotate. Run: python3 skills/lead/scripts/test_cos_log.py"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "cos-log.py"

RECORD = """# alpha

## CURRENT STATE

- Open owner asks: none.
- 2020-01-01 09:00Z a dated line above the Log stays.

## Log

- 2020-01-15 10:00Z January line.
- 2020-02-03 11:00Z February line.
a hand-written line without a time
- 2020-02-25 12:00Z recent line.
- 2020-02-26 08:00Z newest line.
"""


class RotateTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.record = Path(self.dir.name) / "alpha.md"
        self.record.write_text(RECORD)

    def rotate(self, *extra, today="2020-02-27"):
        env = dict(os.environ, COS_LOG_TODAY=today)
        return subprocess.run([sys.executable, str(SCRIPT), "--rotate", str(self.record), *extra],
                              capture_output=True, text=True, env=env)

    def archive(self, month):
        return Path(self.dir.name) / f"alpha.log-{month}.md"

    def test_old_lines_move_to_their_month_and_none_is_lost(self):
        out = self.rotate()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("rotated=2", out.stdout)
        self.assertEqual(self.archive("2020-01").read_text(), "- 2020-01-15 10:00Z January line.\n")
        self.assertEqual(self.archive("2020-02").read_text(), "- 2020-02-03 11:00Z February line.\n")
        record = self.record.read_text()
        for kept in ("## CURRENT STATE", "a dated line above the Log stays", "a hand-written line",
                     "recent line.", "newest line."):
            self.assertIn(kept, record)
        self.assertNotIn("January line", record)
        everything = record + self.archive("2020-01").read_text() + self.archive("2020-02").read_text()
        self.assertEqual(sorted(everything.splitlines()), sorted(RECORD.splitlines()))

    def test_nothing_old_changes_nothing(self):
        out = self.rotate(today="2020-01-16")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("rotated=0", out.stdout)
        self.assertEqual(self.record.read_text(), RECORD)
        self.assertEqual(sorted(p.name for p in Path(self.dir.name).iterdir()), ["alpha.md"])

    def test_a_second_run_appends_to_the_archive(self):
        self.archive("2020-01").write_text("- 2020-01-02 10:00Z earlier archived line.\n")
        self.rotate()
        self.assertEqual(self.archive("2020-01").read_text(),
                         "- 2020-01-02 10:00Z earlier archived line.\n- 2020-01-15 10:00Z January line.\n")
        self.assertIn("rotated=0", self.rotate().stdout)

    def test_days_sets_the_cutoff(self):
        self.assertIn("rotated=3", self.rotate("1").stdout)
        self.assertIn("newest line.", self.record.read_text())

    def test_a_record_without_a_log_heading_is_refused(self):
        self.record.write_text("# alpha\n\n- 2020-01-15 10:00Z January line.\n")
        out = self.rotate()
        self.assertEqual(out.returncode, 2)
        self.assertIn("January line", self.record.read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
