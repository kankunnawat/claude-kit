#!/usr/bin/env python3
"""Check portable lifecycle routing and resident safety guards."""

from pathlib import Path
import hashlib
import re
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent
SKILLS = {
    name: ROOT / "skills" / name / "SKILL.md"
    for name in ("define-goal", "pick-driver", "ship", "review-plan", "worktrees")
}
DRIVER_RUNTIME = ROOT / "skills/pick-driver/references/runtime-routing.md"
WORKTREE_BULK = ROOT / "skills/worktrees/references/bulk-cleanup.md"
INSTALL_TEST_SHA = "870f3e2c5fdc2ef0ab8315c0d1c25a0d048a3eb6da9a6dd2d1a8e5186497935d"
PICK_DRIVER_DESCRIPTION = 'Use before non-trivial or multi-step work, before any step runs, to decide who drives it (interactive, goal, or loop). Also use when the user asks "goal or loop?", "how should we run this", or wants a goal line or loop prompt written.'


def read(path):
    return path.read_text(encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frontmatter(path):
    text = read(path)
    assert text.startswith("---\n"), f"missing frontmatter: {path}"
    raw = text.split("---\n", 2)[1]
    lines = raw.rstrip().splitlines()
    assert lines[0] == "name: " + path.parent.name
    assert lines[1].startswith("description:")
    assert all(line.startswith("  ") for line in lines[2:]), f"unexpected YAML key: {path}"
    value = lines[1].partition(":")[2].strip()
    if value == ">-":
        value = " ".join(line.strip() for line in lines[2:])
    assert value, f"empty description: {path}"
    return value


class PortabilityTest(unittest.TestCase):
    def test_protected_inputs_remain_unchanged(self):
        self.assertEqual(frontmatter(SKILLS["pick-driver"]), PICK_DRIVER_DESCRIPTION)
        self.assertEqual(sha(ROOT / "test-install.sh"), INSTALL_TEST_SHA)

    def test_define_goal_description_and_activation_guards(self):
        skill = read(SKILLS["define-goal"])
        self.assertEqual(
            frontmatter(SKILLS["define-goal"]),
            "Define or refine a measurable completion goal when requested. Ordinary implementation does not activate persistence.",
        )
        for guard in ("get_goal", "active matching goal", "unfinished goal conflicts", "token_budget", "explicitly requests"):
            self.assertIn(guard, skill)
        self.assertIn("FIRST line of its own message", skill)

    def test_driver_uses_runtime_metadata_and_observable_tools(self):
        driver = read(SKILLS["pick-driver"])
        runtime = read(DRIVER_RUNTIME)
        self.assertIn("references/runtime-routing.md", driver)
        self.assertIn("missing", driver)
        self.assertIn("metadata", runtime)
        self.assertIn("observable tool", runtime)
        self.assertIn("do not claim persistence", runtime)
        self.assertIn("continue authorized interactive work", runtime)
        self.assertIn("required reviewer", driver)
        self.assertIn("blocks integration", driver)

    def test_ship_and_review_require_portable_independent_review(self):
        ship = read(SKILLS["ship"])
        review = read(SKILLS["review-plan"])
        for text in (ship, review):
            self.assertIn("configured independent reviewer", text)
            self.assertIn("supported runtime mechanism", text)
            self.assertIn("unavailable", text)
            self.assertIn("blocks", text)
        self.assertNotIn("`/code-review` at medium", ship)
        self.assertNotIn("Fable-pinned", review)

    def test_bulk_cleanup_is_conditional_and_deletion_guard_stays_resident(self):
        skill = read(SKILLS["worktrees"])
        self.assertTrue(WORKTREE_BULK.is_file())
        self.assertIn("references/bulk-cleanup.md", skill)
        self.assertIn("missing", skill)
        self.assertIn("blocks the bulk operation", skill)
        self.assertIn("git branch -D <branch>", skill)
        self.assertIn("`git branch -D` is what can orphan them", skill)
        self.assertIn("Measured per-branch, decided per-set.", skill)
        self.assertNotIn("**1. Merge state", skill)

    def test_cloud_claims_require_observed_capabilities(self):
        cloud = read(ROOT / "CLOUD.md")
        readme = read(ROOT / "README.md")
        for text in (cloud, readme):
            self.assertIn("verify", text.lower())
            self.assertIn("environment", text.lower())
        self.assertIn("observed capabilities", cloud)
        self.assertNotIn("only phase with internet", cloud)
        self.assertNotIn("Codex has no subagent tool", cloud)
        self.assertNotIn("both proxies serve anonymous git reads", readme)

    def test_frontmatter_references_and_public_paths_survive_copy(self):
        for path in SKILLS.values():
            self.assertTrue(frontmatter(path))
            text = read(path)
            self.assertNotIn("/Users/bitazza", text)
            self.assertNotIn("~/.dotfiles", text)

        with tempfile.TemporaryDirectory() as tmp:
            copied_root = Path(tmp)
            for name, skill_path in SKILLS.items():
                copied = copied_root / name
                shutil.copytree(skill_path.parent, copied)
                for reference in re.findall(r"references/[a-z0-9-]+\.md", read(copied / "SKILL.md")):
                    self.assertTrue((copied / reference).is_file(), f"missing copied reference: {name}/{reference}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
