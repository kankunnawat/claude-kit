# hausback-core additions

Read this in hausback-core before step 1 of the pass.

## Sources

- The sessions board is the newest
  `~/Vault/Outputs/hausback/*-hausback-sessions-board.md`. Write to it only
  through `node ~/.claude/scripts/board.mjs`.
- Owner to-dos: lines in `## To-dos` that end in `· open`.
  List them with
  `awk '/^## To-dos/{p=1;next} /^## /{p=0} p' "$B" | grep -E '· open$'`.
- Owner asks: lines in `## Asks` with `→owner` that are not `closed` or
  `answered`.
- Standing decisions: `docs/agents/standing-decisions.md` and
  `docs/decisions/` on origin/dev.
- The chief of staff (CoS) runs a 24/7 loop; its manual is
  `~/Vault/Outputs/hausback/cos-loop.md`. It keeps one record per Bangkok day,
  `~/Vault/Outputs/hausback/<YYYY-MM-DD>-cos/cos.md` (older ones:
  `<date>-overnight/cos.md`). Read the newest record's Log lines before you
  ask: an ask may already be answered or filed there.

## Owner rules for this pass (board D-31, D-32)

- Quiet hours are 00:00 to 08:00 Bangkok (17:00 to 01:00Z). In quiet hours,
  flag mode files to-dos but sends no ping, except for red dev or anything
  touching uat-1.
- From 08:00 to 00:00 Bangkok, ping (PushNotification) only when a decision
  blocks running work. Routine progress goes in the CoS reports, never a ping.
- Flag-mode to-dos use `--from cos` when the CoS runs the pass.

## Board writes

- Close a stale to-do with `board.mjs todo-done T-<n> --by owner` when the
  user decided. Use `--by unblock-pass` when you closed it as yours to decide.
- Close an ask with
  `board.mjs close A-<n> --status closed "<why>" --by owner`.
- Log a decision with
  `board.mjs decision --quote "<verbatim answers>" --by owner --applies "<what it covers>"`.
  If `--applies` names an `A-<n>` that already has a decision, the command
  refuses and prints only that old D-number. Describe the asks without
  `A-<n>` ids in that case. Check that a new `D-<n>` was printed.
- Add an owner to-do with
  `board.mjs todo --for owner --text .. --why .. --mins N --from <seat>`.
- Only hausback content goes on the board. Keep other projects (client work,
  bitazza-ios) off it.

## Routing

- Overnight and daily lanes (`nite-*`, `review-*-r0`, `scout-*`) belong to the
  chief-of-staff thread that launched them. Relay answers to that thread and
  to the owning PR thread, not to the lanes.
- The owner's quiet-Mac rule: one heavy Mac job at a time (proof runs, browser
  shots, wide test runs). Respect the chief of staff's queue when you relay a
  "merge dev in" or "re-run proof" answer.
- Plane writes go through the Plane connector only
  (`mcp__claude_ai_Plane__*`). Search before filing; the
  `sequence_id` filter is ignored, so use `workitem search` or
  `retrieve_by_identifier`.
