Vendored from https://github.com/petergyang/no-ai-slop (MIT).
Upstream path: skills/no-ai-slop/
Pinned commit: d30eddb9e04562234f2070b5ee63ca4649d9a05e
Fetched: 2026-08-12

Update: re-run the gh api fetches for SKILL.md and eval.md against a newer commit.

## Local deviation from upstream

`SKILL.md` frontmatter `description` is extended past upstream's wording so the
skill fires proactively on any writing deliverable, not only when the user
complains the text sounds like AI. Re-apply this
extension after any upstream sync.

Body additions (not upstream): later local commits added patterns (see `git log -- skills/no-ai-slop/SKILL.md`, e.g. ac4bbf7). The pstack `unslop` borrow (cursor/plugins@019a6a2, MIT, (c) 2026 Lauren Tan) adds more metaphor nouns, name-the-actor for passive voice, sentence-case headings and straight quotes. The em-dash rule stays Kan's own. Re-apply all of these after any upstream sync.
