#!/usr/bin/env python3
"""Read-only facts for the merge-agent skill.

Subcommands: doctor, queue, precheck. Each prints one JSON object on stdout.
On failure it prints {"error": ..., "next": ...} and exits 1.

Every call below is a read: `gh repo view`, `gh pr list`, `gh pr view`,
`gh api` GET requests and local file reads. The agent types any write itself,
so the merge guard sees it.
"""

import argparse
import base64
import fnmatch
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

INSTRUCTION_FILES = ("CLAUDE.md", "AGENTS.md")
SKILL_DIRS = (".claude/skills", ".agents/skills")
HELD_DIRS = {".claude", ".agents", ".github"}
HELD_BASENAMES = ("CLAUDE*.md", "AGENTS*.md")

# Prefix match on purpose: "Review" also finds "Reviewers", "Merge" finds "Merge lane".
GATE_HEADING = re.compile(r"\b(pr gate|close-out|integration and close-out|review|merge)", re.IGNORECASE)
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
CLOSE_OUT_LINE = re.compile(r"^\s*(?:[-*+]\s+)?(?:\*\*)?close-out:", re.IGNORECASE)
FENCE = re.compile(r"^\s*(```|~~~)")
IMPORT_LINE = re.compile(r"^@(\S+)\s*$")
REVIEW_WORD = re.compile(r"\breview", re.IGNORECASE)
MERGE_WORD = re.compile(r"\bmerg", re.IGNORECASE)

CHECK_PASS = {"SUCCESS", "NEUTRAL", "SKIPPED"}
CHECK_FAIL = {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE"}


class Failure(Exception):
    def __init__(self, error, next_step):
        super().__init__(error)
        self.error = error
        self.next_step = next_step


# ---------------------------------------------------------------- pure parts


def find_gate_headings(text, file):
    """Gate headings and Close-out lines in one Markdown file, outside code fences."""
    found = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = HEADING.match(line)
        if heading and GATE_HEADING.search(heading.group(2)):
            found.append({"file": file, "heading": heading.group(2), "line": number})
        elif CLOSE_OUT_LINE.match(line):
            found.append({"file": file, "heading": "Close-out:", "line": number})
    return found


def review_rules_hint(texts, gate_guide):
    """True when no gate heading matched but the text still talks about review and merging."""
    if gate_guide:
        return False
    joined = "\n".join(texts)
    return bool(REVIEW_WORD.search(joined) and MERGE_WORD.search(joined))


def find_imports(text, file):
    """Repo-relative paths of `@path` imports in one file. Home and absolute paths are skipped."""
    base = os.path.dirname(file)
    paths = []
    for line in text.splitlines():
        match = IMPORT_LINE.match(line.strip())
        if not match:
            continue
        target = match.group(1)
        if target.startswith(("~", "/")) or "://" in target:
            continue
        path = os.path.normpath(os.path.join(base, target))
        if not path.startswith(".."):
            paths.append(path)
    return paths


def is_held_file(path, gate_files=()):
    """A changed file that holds the PR for the owner."""
    parts = path.split("/")
    if any(part in HELD_DIRS for part in parts[:-1]):
        return True
    if any(fnmatch.fnmatchcase(parts[-1], pattern) for pattern in HELD_BASENAMES):
        return True
    return path in set(gate_files)


def held_files(paths, gate_files=()):
    return sorted({path for path in paths if is_held_file(path, gate_files)})


def hold_labels(labels):
    return [label for label in labels if "flag" in label.lower() or "hold" in label.lower()]


def summarize_checks(items):
    """Count pass, fail and pending over check runs and commit statuses."""
    counts = {"pass": 0, "fail": 0, "pending": 0}
    for item in items:
        if "state" in item and "status" not in item:
            state = (item.get("state") or "").upper()
            outcome = "pass" if state == "SUCCESS" else "fail" if state in CHECK_FAIL else "pending"
        else:
            status = (item.get("status") or "").upper()
            conclusion = (item.get("conclusion") or "").upper()
            if status != "COMPLETED" or not conclusion:
                outcome = "pending"
            elif conclusion in CHECK_PASS:
                outcome = "pass"
            elif conclusion in CHECK_FAIL:
                outcome = "fail"
            else:
                outcome = "pending"
        counts[outcome] += 1
    counts["total"] = counts["pass"] + counts["fail"] + counts["pending"]
    return counts


def proceed_reasons(facts):
    """Reasons the agent may not go on with this PR. Empty means ok to proceed."""
    if facts["state"] == "MERGED":
        return ["already merged"]
    reasons = []
    if facts["state"] != "OPEN":
        reasons.append(f"not open: {facts['state']}")
    if not facts["author_is_you"]:
        reasons.append(f"not the author: opened by {facts['author']}")
    if facts["is_draft"]:
        reasons.append("draft")
    if facts["head_matches_reviewed"] is False:
        reasons.append("head moved since the reviewed commit")
    if facts["held_files"]:
        reasons.append("held files: " + ", ".join(facts["held_files"]))
    flagged = hold_labels(facts["labels"])
    if flagged:
        reasons.append("hold label: " + ", ".join(flagged))
    if facts["checks_on_head"]["fail"]:
        reasons.append(f"checks failing on head: {facts['checks_on_head']['fail']}")
    if facts["mergeable"] != "MERGEABLE":
        reasons.append(f"not mergeable: {facts['mergeable']}")
    return reasons


# ---------------------------------------------------------------- gh and git reads


def run(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        raise Failure(f"{args[0]} is not installed", f"install {args[0]}, run `gh auth login`, then retry")
    return result


def gh_json(args, next_step):
    result = run(["gh", *args])
    if result.returncode != 0:
        raise Failure(f"gh {' '.join(args)} failed: {result.stderr.strip()}", next_step)
    return json.loads(result.stdout) if result.stdout.strip() else None


def gh_get(path, next_step, missing_ok=False):
    """GET one REST path. Returns None on HTTP 404 when missing_ok."""
    result = run(["gh", "api", path])
    if result.returncode != 0:
        if missing_ok and ("HTTP 404" in result.stderr or "Not Found" in result.stderr):
            return None
        raise Failure(f"gh api {path} failed: {result.stderr.strip()}", next_step)
    return json.loads(result.stdout)


def gh_get_pages(path, next_step):
    """GET every page of a REST list. Returns one flat list."""
    result = run(["gh", "api", "--paginate", "--slurp", path])
    if result.returncode != 0:
        raise Failure(f"gh api {path} failed: {result.stderr.strip()}", next_step)
    pages = json.loads(result.stdout)
    items = []
    for page in pages:
        items.extend(page if isinstance(page, list) else [page])
    return items


def resolve_repo(repo):
    args = ["repo", "view", *([repo] if repo else []), "--json", "nameWithOwner,defaultBranchRef"]
    data = gh_json(args, "run inside a GitHub checkout or pass --repo owner/name, and check `gh auth status`")
    return data["nameWithOwner"], data["defaultBranchRef"]["name"]


def resolve_login(author):
    if author:
        return author
    result = run(["gh", "api", "user", "--jq", ".login"])
    if result.returncode != 0 or not result.stdout.strip():
        raise Failure("cannot read your GitHub login", "run `gh auth login` or pass --author LOGIN")
    return result.stdout.strip()


def remote_text(repo, branch, path):
    """One file from the remote branch, or None when it is absent."""
    quoted = urllib.parse.quote(path)
    ref = urllib.parse.quote(branch, safe="")
    data = gh_get(f"repos/{repo}/contents/{quoted}?ref={ref}", "check `gh auth status` and access to the repo", missing_ok=True)
    if not isinstance(data, dict) or data.get("type") != "file" or not data.get("content"):
        return None
    return base64.b64decode(data["content"]).decode("utf-8", errors="replace")


def remote_dir_names(repo, branch, path):
    ref = urllib.parse.quote(branch, safe="")
    data = gh_get(f"repos/{repo}/contents/{path}?ref={ref}", "check `gh auth status` and access to the repo", missing_ok=True)
    if not isinstance(data, list):
        return []
    return [entry["name"] for entry in data]


def guardrails_name_repo(repo):
    path = Path(os.environ.get("HOME", "")) / ".claude/rules/agent-guardrails.md"
    if not path.is_file():
        return "unknown"
    return repo.lower() in path.read_text(encoding="utf-8", errors="replace").lower()


# ---------------------------------------------------------------- subcommands


def discover(repo, branch):
    """Read the instruction files from the remote branch and find the gate guide."""
    texts = {}
    seen = list(INSTRUCTION_FILES)
    for name in INSTRUCTION_FILES:
        text = remote_text(repo, branch, name)
        if text is not None:
            texts[name] = text
    for name in list(texts):
        for imported in find_imports(texts[name], name):
            if imported not in seen:
                seen.append(imported)
                text = remote_text(repo, branch, imported)
                if text is not None:
                    texts[imported] = text
    gate_guide = [hit for name, text in texts.items() for hit in find_gate_headings(text, name)]
    return texts, gate_guide


def doctor(args):
    repo, branch = resolve_repo(args.repo)
    texts, gate_guide = discover(repo, branch)
    verification = [
        f"{directory}/{name}"
        for directory in SKILL_DIRS
        for name in remote_dir_names(repo, branch, directory)
        if "verif" in name.lower()
    ]
    return {
        "repo": repo,
        "default_branch": branch,
        "instruction_files_read": sorted(texts),
        "gate_guide": gate_guide,
        "review_rules_hint": review_rules_hint(list(texts.values()), gate_guide),
        "verification_skill": verification,
        "guardrails_name_repo": guardrails_name_repo(repo),
        "guard_present": (Path(os.environ.get("HOME", "")) / ".claude/hooks/no-merge-guard.py").is_file(),
    }


def changed_files(repo, number):
    """Every changed path of a PR, old names of renamed files included."""
    files = gh_get_pages(f"repos/{repo}/pulls/{number}/files?per_page=100", "check the PR number and `gh auth status`")
    paths = set()
    for entry in files:
        paths.add(entry["filename"])
        if entry.get("previous_filename"):
            paths.add(entry["previous_filename"])
    return sorted(paths)


def gate_files(gate_guide):
    return sorted({hit["file"] for hit in gate_guide})


def queue(args):
    repo, branch = resolve_repo(args.repo)
    login = resolve_login(args.author)
    _, gate_guide = discover(repo, branch)
    fields = "number,title,headRefOid,baseRefName,isDraft,labels,mergeable,statusCheckRollup,author,createdAt"
    prs = gh_json(
        ["pr", "list", "--repo", repo, "--author", login, "--state", "open", "--limit", "500", "--json", fields],
        "check `gh auth status` and access to the repo",
    )
    mine = sorted((pr for pr in prs if pr["author"]["login"].lower() == login.lower()), key=lambda pr: pr["createdAt"])
    rows = []
    for pr in mine:
        labels = [label["name"] for label in pr["labels"]]
        held = held_files(changed_files(repo, pr["number"]), gate_files(gate_guide))
        reasons = []
        if pr["isDraft"]:
            reasons.append("draft")
        if held:
            reasons.append("held files: " + ", ".join(held))
        flagged = hold_labels(labels)
        if flagged:
            reasons.append("hold label: " + ", ".join(flagged))
        rows.append({
            "number": pr["number"],
            "title": pr["title"],
            "head": pr["headRefOid"],
            "base": pr["baseRefName"],
            "isDraft": pr["isDraft"],
            "labels": labels,
            "mergeable": pr["mergeable"],
            "checks": summarize_checks(pr["statusCheckRollup"] or []),
            "held_files": held,
            "hold_reasons": reasons,
        })
    return {"repo": repo, "default_branch": branch, "author": login, "open_prs": rows}


def checks_on_head(repo, head):
    """Check runs and commit statuses reported for this exact commit."""
    runs = gh_get_pages(f"repos/{repo}/commits/{head}/check-runs?per_page=100", "check `gh auth status`")
    items = [run_ for page in runs for run_ in page.get("check_runs", [])]
    status = gh_get(f"repos/{repo}/commits/{head}/status", "check `gh auth status`")
    items.extend({"state": entry["state"]} for entry in status.get("statuses", []))
    counts = summarize_checks(items)
    counts["ran"] = counts["total"] > 0
    return counts


def precheck(args):
    repo, branch = resolve_repo(args.repo)
    login = resolve_login(args.author)
    _, gate_guide = discover(repo, branch)
    pr = gh_json(
        ["pr", "view", str(args.pr), "--repo", repo, "--json", "number,state,author,headRefOid,isDraft,mergeable,baseRefName,labels"],
        "check the PR number and `gh auth status`",
    )
    head = pr["headRefOid"]
    facts = {
        "repo": repo,
        "number": pr["number"],
        "state": pr["state"],
        "author": pr["author"]["login"],
        "author_is_you": pr["author"]["login"].lower() == login.lower(),
        "head": head,
        "head_matches_reviewed": None if not args.reviewed_head else head == args.reviewed_head,
        "is_draft": pr["isDraft"],
        "mergeable": pr["mergeable"],
        "base": pr["baseRefName"],
        "checks_on_head": checks_on_head(repo, head),
        "held_files": held_files(changed_files(repo, pr["number"]), gate_files(gate_guide)),
        "labels": [label["name"] for label in pr["labels"]],
    }
    reasons = proceed_reasons(facts)
    facts["ok_to_proceed"] = not reasons
    facts["reasons"] = reasons
    return facts


# ---------------------------------------------------------------- entry point


class JsonParser(argparse.ArgumentParser):
    def error(self, message):
        raise Failure(f"bad arguments: {message}", "run merge-agent.py --help for usage")


def build_parser():
    parser = JsonParser(prog="merge-agent.py", description="Read-only facts for the merge-agent skill.")
    sub = parser.add_subparsers(dest="command", required=True, parser_class=JsonParser)

    p_doctor = sub.add_parser("doctor", help="find the repo's gate guide and verification skill")
    p_doctor.add_argument("--repo", help="owner/name; default is the current checkout's repo")
    p_doctor.set_defaults(handler=doctor)

    p_queue = sub.add_parser("queue", help="list your open PRs, oldest first")
    p_queue.add_argument("--repo", help="owner/name; default is the current checkout's repo")
    p_queue.add_argument("--author", help="GitHub login; default is the signed-in user")
    p_queue.set_defaults(handler=queue)

    p_pre = sub.add_parser("precheck", help="check one PR before review and before merge")
    p_pre.add_argument("pr", type=int, help="PR number")
    p_pre.add_argument("--repo", help="owner/name; default is the current checkout's repo")
    p_pre.add_argument("--reviewed-head", help="full SHA the review read")
    p_pre.add_argument("--author", help="GitHub login; default is the signed-in user")
    p_pre.set_defaults(handler=precheck)
    return parser


def main(argv=None):
    try:
        args = build_parser().parse_args(argv)
        output = args.handler(args)
    except Failure as failure:
        print(json.dumps({"error": failure.error, "next": failure.next_step}, indent=2))
        return 1
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
