#!/usr/bin/env python3
"""Check portable lifecycle routing and resident safety guards."""

from pathlib import Path
import re
import shutil
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parent
SKILLS = {
    name: ROOT / "skills" / name / "SKILL.md"
    for name in ("define-goal", "pick-driver", "ship", "review-plan", "worktrees")
}
DRIVER_RUNTIME = ROOT / "skills/pick-driver/references/runtime-routing.md"
WORKTREE_BULK = ROOT / "skills/worktrees/references/bulk-cleanup.md"


def read(path):
    return path.read_text(encoding="utf-8")


def frontmatter(path):
    text = read(path)
    assert text.startswith("---\n"), f"missing frontmatter: {path}"
    raw = text.split("---\n", 2)[1]
    data = yaml.safe_load(raw)
    assert isinstance(data, dict), f"invalid YAML frontmatter: {path}"
    assert data.get("name") == path.parent.name, f"wrong skill name: {path}"
    assert isinstance(data.get("description"), str) and data["description"], f"missing description: {path}"
    return data


class PortabilityTest(unittest.TestCase):
    def test_skill_metadata_is_valid_yaml(self):
        for path in SKILLS.values():
            frontmatter(path)

    def test_define_goal_description_and_activation_guards(self):
        skill = read(SKILLS["define-goal"])
        self.assertEqual(
            frontmatter(SKILLS["define-goal"])["description"],
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
        self.assertNotIn("judge reads ONLY the transcript", driver)
        self.assertIn("judge reads only the conversation transcript", runtime)
        for obligation in ("4,000", "wall-clock", "max-wakes", "one repair round", "never edits its own program", "1200", "480"):
            self.assertIn(obligation, runtime)
        self.assertIn("In Claude Code, `/clear` clears both the goal and loop", runtime)

    def test_ship_self_review_and_required_independent_review_stay_distinct(self):
        ship = read(SKILLS["ship"])
        review = read(SKILLS["review-plan"])
        self.assertIn("**Self review**", ship)
        self.assertIn("configured supported runtime mechanism", ship)
        self.assertIn("cannot substitute for any independently required review", ship)
        self.assertNotIn("**Independent review**", ship)
        self.assertIn("configured independent reviewer", review)
        self.assertIn("supported runtime mechanism", review)
        self.assertIn("unavailable", review)
        self.assertIn("blocks", review)
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
        self.assertIn("Do not use network during the run", cloud)
        self.assertIn("Tool presence or reachability does not grant permission", cloud)
        self.assertIn("Reset cache", cloud)
        self.assertIn("about seven days", cloud)
        self.assertNotIn("**Plan first, then execute.** (Claude only.)", cloud)
        self.assertNotIn("**Delegation.** (Claude only.)", cloud)
        self.assertNotIn("Codex has no subagent tool", cloud)
        self.assertNotIn("both proxies serve anonymous git reads", readme)

    def test_frontmatter_references_and_public_paths_survive_copy(self):
        for path in SKILLS.values():
            frontmatter(path)
            markdown_files = [path, *path.parent.glob("references/**/*.md")]
            for markdown_file in markdown_files:
                text = read(markdown_file)
                self.assertIsNone(
                    re.search(r"/Users/[A-Za-z0-9._-]+(?:/|$)", text),
                    f"private macOS home path: {markdown_file}",
                )
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
