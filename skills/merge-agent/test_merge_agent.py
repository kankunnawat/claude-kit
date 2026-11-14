#!/usr/bin/env python3
"""Offline tests for merge-agent.py. No network: only the pure parts run."""

import importlib.util
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve().parent / "merge-agent.py"
_spec = importlib.util.spec_from_file_location("merge_agent", SCRIPT)
ma = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ma)

HEAD = "a" * 40


def facts(**overrides):
    base = {
        "state": "OPEN",
        "author": "me",
        "author_is_you": True,
        "head": HEAD,
        "head_matches_reviewed": True,
        "is_draft": False,
        "mergeable": "MERGEABLE",
        "checks_on_head": {"pass": 3, "fail": 0, "pending": 0, "total": 3, "ran": True},
        "held_files": [],
        "labels": [],
    }
    base.update(overrides)
    return base


class GateHeadingTest(unittest.TestCase):
    def headings(self, text):
        return [hit["heading"] for hit in ma.find_gate_headings(text, "CLAUDE.md")]

    def test_finds_each_gate_heading(self):
        text = "\n".join([
            "# Repo",
            "## PR gate",
            "### Fresh review",
            "### Integration and close-out",
            "## Merge",
            "## Close-out",
            "## Setup",
        ])
        self.assertEqual(
            self.headings(text),
            ["PR gate", "Fresh review", "Integration and close-out", "Merge", "Close-out"],
        )

    def test_reports_file_and_line(self):
        hits = ma.find_gate_headings("intro\n\n## pr GATE\n", "AGENTS.md")
        self.assertEqual(hits, [{"file": "AGENTS.md", "heading": "pr GATE", "line": 3}])

    def test_close_out_line_plain_and_bulleted(self):
        text = "Close-out: commit and push.\n- Close-out: branch, PR, review.\n* **Close-out:** merge.\n"
        hits = ma.find_gate_headings(text, "CLAUDE.md")
        self.assertEqual([hit["line"] for hit in hits], [1, 2, 3])
        self.assertTrue(all(hit["heading"] == "Close-out:" for hit in hits))

    def test_ignores_unrelated_headings_and_code_fences(self):
        text = "## Checks\n## Data\n```bash\n# merge the branch\nClose-out: fake\n```\n## Emerge\n"
        self.assertEqual(self.headings(text), [])

    def test_review_rules_hint_only_without_a_heading(self):
        text = "Every change needs a review before you merge it."
        self.assertTrue(ma.review_rules_hint([text], []))
        self.assertFalse(ma.review_rules_hint([text], [{"file": "CLAUDE.md", "heading": "Merge", "line": 1}]))
        self.assertFalse(ma.review_rules_hint(["Run the tests."], []))

    def test_imports_resolve_relative_and_skip_home_paths(self):
        text = "@AGENTS.md\n@~/.claude/x.md\n@/abs/y.md\n@../outside.md\nsee @inline.md\n"
        self.assertEqual(ma.find_imports(text, "CLAUDE.md"), ["AGENTS.md"])
        self.assertEqual(ma.find_imports("@rules.md\n", "docs/CLAUDE.md"), ["docs/rules.md"])


class HeldFileTest(unittest.TestCase):
    def test_instruction_and_config_files_are_held(self):
        for path in (
            "CLAUDE.md",
            "AGENTS.md",
            "pkg/CLAUDE.local.md",
            "apps/web/AGENTS.override.md",
            ".claude/settings.json",
            ".agents/skills/x/SKILL.md",
            ".github/workflows/ci.yml",
            "docs/.github/x",
            "a/b/.claude/c/d.txt",
        ):
            self.assertTrue(ma.is_held_file(path), path)

    def test_ordinary_files_are_not_held(self):
        for path in ("src/claude.ts", "README.md", "docs/agents.md", "github/ci.yml", "src/.githubrc"):
            self.assertFalse(ma.is_held_file(path), path)

    def test_gate_guide_file_is_held(self):
        self.assertFalse(ma.is_held_file("docs/guides/merge.md"))
        self.assertTrue(ma.is_held_file("docs/guides/merge.md", ["docs/guides/merge.md"]))

    def test_held_files_filters_and_sorts(self):
        paths = ["src/a.py", ".github/ci.yml", "CLAUDE.md", "src/a.py"]
        self.assertEqual(ma.held_files(paths), [".github/ci.yml", "CLAUDE.md"])

    def test_hold_labels(self):
        self.assertEqual(ma.hold_labels(["bug", "merge-lane:flagged", "On-Hold", "module:ui"]), ["merge-lane:flagged", "On-Hold"])


class ChecksTest(unittest.TestCase):
    def test_counts_check_runs_and_statuses(self):
        items = [
            {"status": "COMPLETED", "conclusion": "SUCCESS"},
            {"status": "COMPLETED", "conclusion": "SKIPPED"},
            {"status": "COMPLETED", "conclusion": "FAILURE"},
            {"status": "IN_PROGRESS", "conclusion": ""},
            {"state": "SUCCESS"},
            {"state": "PENDING"},
            {"state": "ERROR"},
        ]
        self.assertEqual(ma.summarize_checks(items), {"pass": 3, "fail": 2, "pending": 2, "total": 7})


class ProceedTest(unittest.TestCase):
    def test_clean_pr_may_proceed(self):
        self.assertEqual(ma.proceed_reasons(facts()), [])

    def test_merged_pr_reports_only_already_merged(self):
        merged = facts(state="MERGED", author_is_you=False, is_draft=True, held_files=["CLAUDE.md"], mergeable="UNKNOWN")
        self.assertEqual(ma.proceed_reasons(merged), ["already merged"])

    def test_other_author(self):
        reasons = ma.proceed_reasons(facts(author="someone", author_is_you=False))
        self.assertEqual(reasons, ["not the author: opened by someone"])

    def test_moved_head(self):
        self.assertEqual(ma.proceed_reasons(facts(head_matches_reviewed=False)), ["head moved since the reviewed commit"])
        self.assertEqual(ma.proceed_reasons(facts(head_matches_reviewed=None)), [])

    def test_draft(self):
        self.assertEqual(ma.proceed_reasons(facts(is_draft=True)), ["draft"])

    def test_flagged_label(self):
        reasons = ma.proceed_reasons(facts(labels=["bug", "merge-lane:flagged"]))
        self.assertEqual(reasons, ["hold label: merge-lane:flagged"])

    def test_held_files_failing_checks_conflicts_and_closed(self):
        reasons = ma.proceed_reasons(facts(
            state="CLOSED",
            held_files=["CLAUDE.md"],
            mergeable="CONFLICTING",
            checks_on_head={"pass": 1, "fail": 2, "pending": 0, "total": 3, "ran": True},
        ))
        self.assertEqual(reasons, [
            "not open: CLOSED",
            "held files: CLAUDE.md",
            "checks failing on head: 2",
            "not mergeable: CONFLICTING",
        ])


class ReadOnlyTest(unittest.TestCase):
    def test_script_has_no_write_commands(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for banned in ("pr merge", "pr comment", "-X", "git push", "shell=True"):
            self.assertNotIn(banned, source, f"merge-agent.py must stay read-only: found {banned!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
