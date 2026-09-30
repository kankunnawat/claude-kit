# Usage

Invoke the skill in Codex with `$build-landing-auto` or in Claude Code with `/build-landing-auto`.
Choose a level and endpoint in the same request.
Use project context for business facts, visual constraints, stack, and supported delivery tools.

## Examples

```text
$build-landing-auto 75%: Build the landing page from this project's brief. Deliver a verified local preview.

/build-landing-auto 50%: Build the service landing page. Review the brief, static direction, and browser prototype with me. Deliver locally.

$build-landing-auto 100%: Build the site from the complete brief. Use the existing approved repository and linked deployment target.

/build-landing-auto hands-free: Build from the portfolio context. Choose the direction and evaluate the prototype. Deliver a verified local preview.

$build-landing-auto 100%: Prepare the landing page, but stop after the verified browser prototype for my review.
```

75% is the default.
"Hands-free" and "fully automatic" select 100% unless an explicit level says otherwise.
A requested checkpoint or stop condition overrides that preset.
"Review-only" limits the task to review findings and any explicitly requested review artifacts.

## Delivery and goals

A level delegates creative decisions within the existing authorized scope.
A named deployment target alone does not prove publication approval.
Reuse exact prior approval when the action, target, and scope match.
When the request and project context name no endpoint, deliver a verified local preview.

For goal-backed work, request a measurable goal explicitly and use `define-goal` through the current runtime's supported mechanism.
In Codex, for example:

```text
Use $define-goal with $build-landing-auto at 100%: complete the site when the required production-build checks pass and the verified local preview is delivered. I explicitly request a persistent goal for this work.
```

In Claude Code, `/define-goal` drafts the condition; it does not activate persistence.
The user must send the returned `/goal <condition>` as the first line of its own message.
That message activates the harness; then invoke `/build-landing-auto 100%`.
Confirm supported runtime activation before claiming persistence.
Neither the builder nor a hands-free request activates a goal.

## Portfolio batches

When the project declares a portfolio context, read its brief, claims policy, template contract, ledger, and lessons.
Check existing topic ownership before assigning topics to new sites.
Use the context's collision rules; ask when a conflict has no supported resolution.
Keep each site's identity, artifacts, and evidence distinct.
Use supported configured roles and required isolated writer ownership.
Never turn one portfolio's brand, language, keyword, article count, framework, host, or model into a universal default.
