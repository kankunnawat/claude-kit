#!/usr/bin/env python3
"""Offline tests for merge-agent.py. No network: only the pure parts run."""

import base64
import importlib.util
import json
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
        self.assertEqual(hits, [{"file": "AGENTS.md", "heading": "pr GATE", "line": 3, "points_to": []}])

    def test_files_a_gate_section_points_at_are_gate_files(self):
        text = "\n".join([
            "## Setup",
            "See `docs/setup.md`.",
            "### Integration and close-out",
            "PR work: `docs/guides/merge-lane.md`; promotion: [branching](docs/guides/branching.md).",
            "## Notes",
            "Read `docs/notes.md`.",
            "- Close-out: follow `docs/close.md`.",
        ])
        files = ma.gate_files(ma.find_gate_headings(text, "AGENTS.md"))
        self.assertEqual(files, ["AGENTS.md", "docs/close.md", "docs/guides/branching.md", "docs/guides/merge-lane.md"])

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
            "claude.md",
            "pkg/agents.md",
            ".GitHub/workflows/ci.yml",
            ".claude",
            "pkg/.github",
        ):
            self.assertTrue(ma.is_held_file(path), path)

    def test_ordinary_files_are_not_held(self):
        for path in ("src/claude.ts", "README.md", "docs/the-agents.md", "github/ci.yml", "src/.githubrc"):
            self.assertFalse(ma.is_held_file(path), path)

    def test_gate_guide_file_is_held(self):
        self.assertFalse(ma.is_held_file("docs/guides/merge.md"))
        self.assertTrue(ma.is_held_file("docs/guides/merge.md", ["docs/guides/merge.md"]))
        self.assertTrue(ma.is_held_file("Docs/Guides/Merge.md", ["docs/guides/merge.md"]))

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

    def test_other_author_the_owner_approved(self):
        self.assertEqual(ma.proceed_reasons(facts(author="someone", author_is_you=False, author_approved=True)), [])

    def test_pending_checks_block(self):
        pending = {"pass": 2, "fail": 0, "pending": 1, "total": 3, "ran": True}
        self.assertEqual(ma.proceed_reasons(facts(checks_on_head=pending)), ["checks pending on head: 1"])

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


class GuardrailsTest(unittest.TestCase):
    TEXT = "Solo repos (`kankunnawat/kan-brain`, `kankunnawat/agent-bar`).\nIn AlphaOS (duopreneur/AlphaOS), squash.\n"

    def test_exact_repo_name_matches_any_case(self):
        self.assertEqual(len(ma.guardrails_lines("duopreneur/alphaos", self.TEXT)), 1)
        self.assertEqual(len(ma.guardrails_lines("kankunnawat/kan-brain", self.TEXT)), 1)

    def test_a_prefix_or_suffix_of_a_named_repo_does_not_match(self):
        for repo in ("kankunnawat/kan", "kankunnawat/agent", "duopreneur/alpha", "unnawat/kan-brain"):
            self.assertEqual(ma.guardrails_lines(repo, self.TEXT), [], repo)


class Done:
    def __init__(self, returncode, stdout, stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class FakeGh:
    """Stands in for subprocess.run: answers each gh call from a table and records every call."""

    def __init__(self, answers):
        self.answers = answers
        self.calls = []

    def __call__(self, args, **kwargs):
        self.calls.append(list(args))
        for needle, payload in self.answers:
            if any(needle in word for word in args):
                return Done(0, payload if isinstance(payload, str) else json.dumps(payload))
        return Done(1, "", "HTTP 404: Not Found")


class GithubReadTest(unittest.TestCase):
    def fake(self, answers):
        real_run = ma.subprocess.run
        self.addCleanup(lambda: setattr(ma.subprocess, "run", real_run))
        gh = FakeGh(answers)
        ma.subprocess.run = gh
        return gh

    def pr_answers(self, author="me", head=HEAD, files=None, check_runs=None):
        claude = base64.b64encode(b"## PR gate\nRules: `docs/gate.md`\n").decode()
        if check_runs is None:
            check_runs = [{"status": "completed", "conclusion": "success"}]
        return [
            ("nameWithOwner", {"nameWithOwner": "o/r", "defaultBranchRef": {"name": "dev"}}),
            ("contents/CLAUDE.md", {"type": "file", "content": claude}),
            ("/files", [files or [{"filename": "src/a.py"}]]),
            ("/check-runs", [{"check_runs": check_runs}]),
            ("/status", {"statuses": []}),
            ("headRefOid", {"number": 7, "state": "OPEN", "author": {"login": author}, "headRefOid": head,
                            "isDraft": False, "mergeable": "MERGEABLE", "baseRefName": "dev", "labels": []}),
            ("user", "me\n"),
        ]

    def precheck(self, *argv):
        return ma.precheck(ma.build_parser().parse_args(["precheck", "7", "--repo", "o/r", *argv]))

    def test_clean_pr_at_the_reviewed_head_may_proceed(self):
        self.fake(self.pr_answers())
        out = self.precheck("--reviewed-head", HEAD)
        self.assertTrue(out["ok_to_proceed"], out["reasons"])
        self.assertTrue(out["base_is_default"])

    def test_moved_head_blocks(self):
        self.fake(self.pr_answers(head="b" * 40))
        out = self.precheck("--reviewed-head", HEAD)
        self.assertIn("head moved since the reviewed commit", out["reasons"])

    def test_renamed_instruction_file_and_linked_gate_file_hold_the_pr(self):
        files = [{"filename": "docs/old.md", "previous_filename": "CLAUDE.md"}, {"filename": "docs/gate.md"}]
        self.fake(self.pr_answers(files=files))
        self.assertEqual(self.precheck()["held_files"], ["CLAUDE.md", "docs/gate.md"])

    def test_no_checks_on_head_warns(self):
        self.fake(self.pr_answers(check_runs=[]))
        out = self.precheck()
        self.assertFalse(out["checks_on_head"]["ran"])
        self.assertEqual(len(out["warnings"]), 1)

    def test_other_author_blocks_unless_that_login_is_approved(self):
        self.fake(self.pr_answers(author="someone"))
        self.assertIn("not the author: opened by someone", self.precheck()["reasons"])
        self.assertIn("not the author: opened by someone", self.precheck("--approved-author", "another")["reasons"])
        self.assertTrue(self.precheck("--approved-author", "someone")["ok_to_proceed"])

    def test_every_call_is_a_known_read(self):
        gh = self.fake(self.pr_answers())
        self.precheck()
        self.assertTrue(gh.calls)
        for call in gh.calls:
            self.assertIsNone(ma.read_only_refusal(call), call)


class ReadOnlyTest(unittest.TestCase):
    def test_reads_are_allowed(self):
        for args in (
            ["gh", "repo", "view", "--json", "nameWithOwner"],
            ["gh", "pr", "list", "--repo", "o/r", "--json", "number"],
            ["gh", "pr", "view", "7", "--repo", "o/r", "--json", "state"],
            ["gh", "api", "repos/o/r/pulls/7/files?per_page=100"],
            ["gh", "api", "--paginate", "--slurp", "repos/o/r/commits/abc/check-runs"],
            ["gh", "api", "user", "--jq", ".login"],
        ):
            self.assertIsNone(ma.read_only_refusal(args), args)

    def test_writes_are_refused_before_they_run(self):
        ran = []
        real_run = ma.subprocess.run
        self.addCleanup(lambda: setattr(ma.subprocess, "run", real_run))
        ma.subprocess.run = lambda *a, **k: ran.append(a)
        for args in (
            ["gh", "pr", "merge", "7", "--squash"],
            ["gh", "pr", "comment", "7", "--body", "x"],
            ["gh", "pr", "edit", "7", "--add-label", "x"],
            ["gh", "api", "--method", "POST", "repos/o/r/issues/7/comments"],
            ["gh", "api", "-X", "DELETE", "repos/o/r/git/refs/heads/x"],
            ["gh", "api", "repos/o/r/issues/7/comments", "-f", "body=x"],
            ["gh", "api", "repos/o/r/issues/7/labels", "--input", "file.json"],
            ["gh", "api", "graphql", "-F", "query=mutation"],
            ["gh", "api", "graphql"],
            ["git", "push", "origin", "main"],
            ["git", "status"],
        ):
            with self.assertRaises(ma.Failure, msg=args):
                ma.run(args)
        self.assertEqual(ran, [])

    def test_script_never_uses_a_shell(self):
        self.assertNotIn("shell=True", SCRIPT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
