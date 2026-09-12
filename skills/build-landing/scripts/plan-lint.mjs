// Guards the lesson: "The plan carried the same floor violation three times."
// Also: "Built HTML is one line." Fix the plan, not the implementations.
import { readFileSync } from 'node:fs';

const usage = `Usage:
  plan-lint.mjs plan.md --body 17 --min 12 [--astro]

  --body N   body text size; px values below it are reported for confirmation
  --min N    hard floor; px values below it fail
  --astro    also flag compound selectors that a component's element will not match

FAIL exits 1. CONFIRM lines are for a human to rule on and exit 0.`;

const argv = process.argv.slice(2);
if (argv.length === 0 || argv.includes('--help')) { console.log(usage); process.exit(argv.length === 0 ? 1 : 0); }

let body = 17, min = 12, astro = false, path = null;
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--body') body = Number(argv[++i]);
  else if (argv[i] === '--min') min = Number(argv[++i]);
  else if (argv[i] === '--astro') astro = true;
  else path = argv[i];
}
if (!path) { console.error('no plan file given'); process.exit(1); }

const lines = readFileSync(path, 'utf8').split('\n');
const findings = [];
const add = (line, level, message) => findings.push({ line: line + 1, level, message });

// A font size is `font-size: <value>` or a type-scale custom property. clamp() reports its lower bound.
const sizeSource = /(?:font-size\s*:|--[\w-]*(?:h[1-6]|text|lede|eyebrow|btn|font|size|title|display)[\w-]*\s*:)\s*([^;}]*)/g;
const firstPx = value => {
  const clamp = value.match(/clamp\(([^)]*)/);
  const match = (clamp ? clamp[1] : value).match(/(\d+(?:\.\d+)?)px/);
  return match ? Number(match[1]) : null;
};

let inStyle = false; // true only inside a scoped <style> block
lines.forEach((text, index) => {
  for (const match of text.matchAll(sizeSource)) {
    const px = firstPx(match[1]);
    if (px === null) continue;
    if (px < min) add(index, 'FAIL', `${px}px font size is below the ${min}px floor`);
    else if (px < body) add(index, 'CONFIRM', `${px}px font size is under body ${body}px: confirm this is an eyebrow/label, not body text`);
  }

  if (/grep -c/.test(text) && /dist\/|\.html/.test(text))
    add(index, 'FAIL', 'grep -c on built HTML: built HTML is one line, use grep -o ... | wc -l');

  if (/dispatch|subagent|codex exec/i.test(text) && !lines.slice(index + 1, index + 16).some(l => /report/i.test(l)))
    add(index, 'CONFIRM', 'dispatch without a report file in the next 15 lines');

  if (/<style/.test(text)) inStyle = !/is:global/.test(text); // is:global styles are not scoped
  if (astro && inStyle && text.includes('{')) {
    for (const selector of text.slice(0, text.indexOf('{')).split(',')) {
      const parts = selector.trim().split(/\s+|>|\+|~/).filter(Boolean);
      if (selector.includes(':global(') || selector.trim().startsWith('@') || parts.length < 2) continue;
      if (parts.at(-1).startsWith('.'))
        add(index, 'CONFIRM', `heuristic: "${selector.trim()}" ends in a class; a component-rendered element carries no scope id and needs :global()`);
    }
  }
  if (/<\/style/.test(text)) inStyle = false;
});

for (const finding of findings.sort((a, b) => a.line - b.line))
  console.log(`${path}:${finding.line}  ${finding.level}  ${finding.message}`);
console.log(`\n${findings.filter(f => f.level === 'FAIL').length} FAIL, ${findings.filter(f => f.level === 'CONFIRM').length} CONFIRM`);
if (findings.some(f => f.level === 'FAIL')) process.exit(1);
