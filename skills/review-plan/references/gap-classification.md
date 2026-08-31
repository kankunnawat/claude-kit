# Gap Classification

When the rubric finds a gap, classify it before deciding what to do with it.

## Two axes

**Axis 1 — who can resolve it:**
- **Claude can resolve** — the fix is obvious from the existing context
- **User must decide** — the fix requires a design choice, scope call, or risk acceptance

**Axis 2 — severity:**
- 🚫 **Blocker** — will cause failure or wrong behavior if not addressed
- ⚠️ **Risk** — could go wrong, but may be acceptable depending on context
- 💭 **Assumption** — taken-for-granted fact that should be explicitly validated
- ❓ **Open question** — document is silent; execution will need the answer

## Action matrix

| | Blocker (🚫) | Risk (⚠️) | Assumption (💭) | Open question (❓) |
|---|---|---|---|---|
| **Claude can resolve** | Fix inline, note in commit | Add callout to doc | Add validation step | Answer inline |
| **User must decide** | Surface, wait for decision | Surface grouped | Ask to validate | Ask for input |

## When to auto-fix vs. surface

Auto-fix only when all three are true:

1. The fix is derivable from the existing document plus the codebase
2. There is exactly one reasonable way to do it
3. A reasonable reviewer would not want to be consulted about it

If any of those is uncertain, surface instead. The cost of asking is low; the cost of silently making a wrong call is high.

## Examples

### Auto-fix (trivial)

- Plan task says "Add the client" but doesn't name the file. Other tasks cite `Packages/DomainKit/Sources/FooClient.swift`. → Add the file path to the task.
- Plan has tasks for feature X and feature Y but no "Verification" section. The verification for each is obvious (tests pass, screen renders). → Add a verification subsection per task.
- Spec lists 5 goals but no non-goals. Implicit non-goals are clear from scope. → Add a "Non-goals" section.
- Plan task #7 references `handleLogin()` but the actual function is `onLogin()` (typo). → Fix the reference.

### Surface (decision-required)

- Spec says "handle token refresh failures gracefully" — two viable interpretations (retry once vs. log out immediately). → Ask.
- Plan has a regression risk on Dashboard render path but no mitigation. Mitigation choice affects scope. → Ask.
- Spec is silent on pagination. Feature could work either way. → Ask, with the tradeoffs.
- Plan step modifies shared auth code; rollback path is missing and could be one of three strategies. → Ask.

## Format when surfacing

Group by severity symbol, one concrete claim per bullet, reference the section / task / line:

```
🚫 Blockers (1)
- §2 Task 4 modifies AuthClient.refresh() but provides no rollback path. Required before execution.

⚠️ Risks (2)
- §3 Task 7 runs `terraform apply` before the state-backup step — a partial apply strands state with no recovery path. Reorder, or gate the apply on a saved plan file.
- §4 scope includes Wallet aggregation refactor not present in the underlying spec.

💭 Assumptions (1)
- §1 assumes the Backend /v2/balances endpoint returns Decimal strings. Validate against a sample response before execution.

❓ Open questions (1)
- Spec is silent on whether offline mode is supported. Affects cache semantics in §3 Task 5.
```

Ask the user to work through one group at a time — start with 🚫 Blockers.
