# hausback-core additions

Read this before acting on `/cos` in hausback-core.

## Homes

- **Manual (the rules):** `~/Vault/Outputs/hausback/cos-loop.md`. It holds
  the clock, the Mac limits, the reports, the pings, the holder's thread id,
  the scheduled task ids and the status page URL. Read ids from it; do not
  copy them here.
- **Inbox:** the manual names the inbox thread and
  `~/Vault/Outputs/hausback/cos-inbox.md`. Lanes, reviewers and scouts
  report to the inbox thread, never to the holder's thread. The inbox logs
  each report and wakes the holder only when no hold file exists. Read the
  inbox file on "resume" and at each tick.
- **Hold file:** `~/Vault/Outputs/hausback/cos-hold.md`. It exists while
  the owner has the loop on hold. Both scheduled reports check it first.
- **Loop mechanics:** `.agents/skills/hausback-loop/SKILL.md` in the repo.
- **Record:** `~/Vault/Outputs/hausback/<YYYY-MM-DD>-cos/cos.md`, one per
  Bangkok day, sections CURRENT STATE, Lanes, Log. Briefs, lane state files
  and review reports go in the same folder.
- **Board:** the newest `~/Vault/Outputs/hausback/*-hausback-sessions-board.md`,
  written only through `board.mjs` (see
  `unblock-decisions/references/hausback.md` for the commands).
- **Shared brief rules:** the newest `lane-brief-common.md` and
  `review-brief-common.md` under `~/Vault/Outputs/hausback/`. Briefs point at
  them and add only what is new.
- **Reviewer checklists:** `.claude/agents/ui-test-reviewer.md` (tier T1 UI
  and tests) and `.claude/agents/kernel-reviewer.md` (SQL, RLS, kernel
  boundary).

## Sessions

- Start: `scripts/cos-launch.sh`, which wraps
  `~/.t3/bin/t3 thread start --title .. [--worktree <full sha>] --json . -`.
  The plain form runs Opus high.
- Machine limits for the launch: `--max-load 12 --min-free-gib 20` by day,
  `--max-load 6 --min-free-gib 20` in quiet hours (00:00 to 08:00 Bangkok,
  17:00 to 01:00 UTC). Lane briefs carry the same numbers.
- Thread ids carry the `mcp:` prefix in `t3 thread show` and
  `t3_thread_organize`.
- Send: `~/.t3/bin/t3 thread send <id> - < <file>`. Read the reply
  ("Sent." or "Queued."). A busy thread gets it as its next turn; nothing
  is interrupted.
- Lanes report with one `t3 thread send` to the inbox thread id, in the
  fixed format the brief gives.
- Reuse a lane's thread for a fix round only when state lives in its
  worktree, and then with a fresh context.

## Tracker

- Plane through the connector only, project HB. Resolve state, member, label
  and cycle ids from the connector at use time.
- Before a lane starts: item In Progress, assigned, in the active cycle,
  labelled, read back. This is a write under the owner's name: ask for the
  items by key.
- The standing rule in the manual names the two write kinds that need no
  per-batch approval. Everything else asks first.

## Repo rules the CoS enforces on lanes

- One PR per seat per Bangkok day; lanes push a lane branch and open no PR.
- The integration lane owns pin and ratchet JSON, generated pairs and commit
  subjects over 72 characters.
- Commits and PR text never cite board decision numbers. Write "owner ruling
  <date> (HB-xxxx)".
- Never: merge, arm auto-merge, touch uat-1, force-push, comment on someone
  else's PR.
- Hold new worktrees when free disk is under 20 GiB.

## Brief blanks

Fill the project blanks of [briefs.md](briefs.md) with these lines.

- Project lane rules: "If a gate needs a pin or ratchet change, stop and
  report. If a claim is refused, stop and report who holds it. Do not ask
  another lane to release it."
- Project start step: "claim your files first and read the surface count
  back."
- Project commit rules: "no board decision numbers".
- Gate baselines are the pin and ratchet JSON files.

## Guard traps

- A Bash call whose text has "push" or "merge" inside a heredoc is blocked.
  Put the text in a file and send the file.
- Shell redirects into home paths are blocked. Write files with the Write
  tool or python.
- `git restore`, `git checkout -- <file>`, `reset --hard`, `branch -D` and
  `rm -rf` are blocked. A lane that must drop local changes stops and
  reports.
- A pipe hides a failed command's exit code. Read the code of the command
  that matters, unpiped.
