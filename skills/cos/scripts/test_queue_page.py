#!/usr/bin/env python3
"""Tests for queue_page.py. Run: python3 skills/cos/scripts/test_queue_page.py"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue_page.py")

RECORD = """# Chief of staff record, 2030-01-02

Committed at each report and at handoff, not at every tick.
A line the brain adds to its header.

## CURRENT STATE

- Old state.

## Log

- 2030-01-02 01:00Z Morning report.
- 2030-01-02 05:00Z Unblock pass.
"""


def items(n=10, **over):
    d = {
        "date": "2030-01-02",
        "report": "Evening report",
        "stamp": "2030-01-02 23:30 Bangkok (16:30Z)",
        "shown": 8,
        "counts": ["oldest **12 h**"],
        "notes": ["Not shown, 2 more."],
        "log": "2030-01-02 16:30Z Evening report.",
        "state_before": ["Holder: this thread."],
        "state_after": ["Answered, do not ask again: none."],
        "machine": {"name": "mac-a", "budget": "slots=4", "note": "Room for 4 sessions."},
        "areas": [{"name": "alpha", "state": "active", "text": "Lead runs. See [PR 1](https://example.org/1)."},
                  {"name": "beta", "state": "hold", "text": "On hold since 2030-01-01."}],
        "items": [{"area": "alpha", "item": f"Item {i} <b>", "why": "Because.", "rec": "Say `yes`.", "mins": 2,
                   "asks": 3, "record": f"record line {i}", "links": [{"text": "thread", "url": "https://example.org/t"}]}
                  for i in range(1, n + 1)],
    }
    d.update(over)
    return d


class QueuePage(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.record = self.path("record.md", RECORD)
        self.banned = self.path("banned.txt", "# names that must not leave\nSecretCo\nnpm \n")
        self.page = os.path.join(self.dir.name, "page.html")

    def path(self, name, text):
        p = os.path.join(self.dir.name, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p

    def run_script(self, data, *extra, banned=None):
        return subprocess.run(
            [sys.executable, SCRIPT, "--items", self.path("items.json", json.dumps(data)), "--record", self.record,
             "--page", self.page, "--banned", banned or self.banned, *extra],
            capture_output=True, text=True)

    def read(self, p):
        with open(p, encoding="utf-8") as f:
            return f.read()

    def test_page_shows_first_eight_and_counts_all(self):
        r = self.run_script(items(10))
        self.assertEqual(r.returncode, 0, r.stderr)
        page = self.read(self.page)
        self.assertEqual(page.count("<li>"), 8)
        self.assertIn("<b>10</b> waiting on you, 8 shown", page)
        self.assertIn("about <b>20 min</b> to clear", page)
        self.assertIn("<span>oldest <b>12 h</b></span>", page)
        self.assertIn("Item 1 &lt;b&gt;", page)
        self.assertIn("Say <code>yes</code>.", page)
        self.assertIn('<a href="https://example.org/1">PR 1</a>', page)
        self.assertIn('class="state hold"', page)
        self.assertIn("one_by_one=30", r.stdout)

    def test_record_keeps_header_and_log_and_lists_every_ask(self):
        self.run_script(items(10))
        rec = self.read(self.record)
        self.assertIn("A line the brain adds to its header.", rec)
        self.assertNotIn("Old state.", rec)
        self.assertIn("- Open owner asks (10), in queue order; the page shows the first 8:", rec)
        self.assertIn("  10. alpha: record line 10", rec)
        self.assertTrue(rec.endswith("- 2030-01-02 01:00Z Morning report.\n- 2030-01-02 05:00Z Unblock pass.\n"
                                     "- 2030-01-02 16:30Z Evening report.\n"))

    def test_state_line_with_two_spaces_stays_a_sub_bullet(self):
        self.run_script(items(1, state_after=["Retro.", "  - P1, a proposal."]))
        self.assertIn("- Retro.\n  - P1, a proposal.\n", self.read(self.record))

    def test_second_run_changes_nothing(self):
        self.run_script(items(10))
        first = (self.read(self.page), self.read(self.record))
        self.run_script(items(10))
        self.assertEqual(first, (self.read(self.page), self.read(self.record)))

    def test_banned_string_stops_the_run_and_writes_nothing(self):
        for field in ("state_after", "notes"):
            r = self.run_script(items(10, **{field: ["A word from SecretCo."]}))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("refuse: banned strings", r.stderr)
        self.assertFalse(os.path.exists(self.page))
        self.assertEqual(self.read(self.record), RECORD)

    def test_banned_string_keeps_its_trailing_space(self):
        self.assertEqual(self.run_script(items(2, notes=["the npm"])).returncode, 0)
        self.assertNotEqual(self.run_script(items(2, notes=["run npm install"])).returncode, 0)

    def test_old_log_lines_are_not_scanned(self):
        self.record = self.path("record.md", RECORD + "- 2030-01-02 06:00Z A line that names SecretCo.\n")
        self.assertEqual(self.run_script(items(2)).returncode, 0)

    def test_missing_or_empty_banned_file_stops_the_run(self):
        for banned in (os.path.join(self.dir.name, "none.txt"), self.path("empty.txt", "# only a comment\n")):
            r = self.run_script(items(2), banned=banned)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("refuse:", r.stderr)

    def test_items_file_without_a_required_key_stops_the_run(self):
        data = items(1)
        del data["items"]
        r = self.run_script(data)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("refuse: the items file lacks ['items']", r.stderr)

    def test_dry_run_writes_nothing(self):
        r = self.run_script(items(3), "--dry")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.startswith("dry:"))
        self.assertFalse(os.path.exists(self.page))
        self.assertEqual(self.read(self.record), RECORD)

    def test_new_record_gets_a_header(self):
        os.remove(self.record)
        self.run_script(items(1))
        self.assertTrue(self.read(self.record).startswith("# Chief of staff record, 2030-01-02\n"))


if __name__ == "__main__":
    unittest.main()
