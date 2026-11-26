# Sessions on this Mac

True for every area. Read before the first launch or send.

## Sessions

- Start: `scripts/cos-launch.sh`, which wraps
  `~/.t3/bin/t3 thread start --title .. [--worktree <full sha>] --json . -`.
  The plain form runs the session default.
  `--provider P --model M` starts the session
  on the provider an area's roster row names.
- The script reads the machine budget first and refuses a start with no
  room. Pass this machine's flags from the roster after `--`.
- Thread ids carry the `mcp:` prefix in `t3 thread show` and
  `t3_thread_organize`.
- Send: `~/.t3/bin/t3 thread send <id> - < <file>`. Read the reply
  ("Sent." or "Queued."). A busy thread gets it as its next turn; nothing
  is interrupted.
- Workers report with one `t3 thread send`, in the fixed format the brief
  gives, to the area's inbox thread when its manual names one, otherwise to
  the lead's thread.
- Reuse a lane's thread for a fix round only when state lives in its
  worktree, and then with a fresh context.

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
