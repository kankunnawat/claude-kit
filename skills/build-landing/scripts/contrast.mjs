// Guards the lesson: "Contrast fails on state changes, not on the palette."
// Every state that changes ground gets a pair here, before the plan is written.
import { readFileSync } from 'node:fs';

const usage = `Usage:
  contrast.mjs '#fg' '#bg' ['#fg' '#bg' ...]   check pairs given on the command line
  contrast.mjs --file pairs.txt                 one pair per line: fg bg [label...]; # comments allowed
  contrast.mjs ... --min 3                      minimum ratio (default 4.5)

Prints one line per pair: ratio (2 decimals), PASS/FAIL, label.
Exits 1 if any pair is below the minimum.`;

const argv = process.argv.slice(2);
if (argv.length === 0 || argv.includes('--help')) { console.log(usage); process.exit(argv.length === 0 ? 1 : 0); }

let min = 4.5;
let file = null;
const rest = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--min') min = Number(argv[++i]);
  else if (argv[i] === '--file') file = argv[++i];
  else rest.push(argv[i]);
}
if (!Number.isFinite(min)) { console.error('--min needs a number'); process.exit(1); }

const channel = value => (value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
const expand = hex => { const t = hex.trim().replace(/^#/, ''); return t.length === 3 ? [...t].map(c => c + c).join('') : t; };
const isHex = hex => /^[0-9a-fA-F]{6}$/.test(expand(hex));
function luminance(hex) {
  const full = expand(hex);
  if (!isHex(hex)) throw new Error(`not a hex colour: ${hex}`);
  const [r, g, b] = [0, 2, 4].map(i => channel(parseInt(full.slice(i, i + 2), 16) / 255));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
const ratio = (fg, bg) => {
  const [a, b] = [luminance(fg), luminance(bg)].sort((x, y) => y - x);
  return (a + 0.05) / (b + 0.05);
};

const pairs = [];
if (file) {
  for (const line of readFileSync(file, 'utf8').split('\n')) {
    const [fg, bg, ...label] = line.trim().split(/\s+/);
    if (!fg || !bg || !isHex(fg)) continue; // blank line or # comment
    pairs.push([fg, bg, label.join(' ')]);
  }
}
for (let i = 0; i < rest.length; i += 2) {
  if (!rest[i + 1]) { console.error(`odd colour without a background: ${rest[i]}`); process.exit(1); }
  pairs.push([rest[i], rest[i + 1], '']);
}
if (pairs.length === 0) { console.error('no pairs to check'); process.exit(1); }

let failed = false;
for (const [fg, bg, label] of pairs) {
  const value = ratio(fg, bg);
  const pass = value >= min;
  if (!pass) failed = true;
  console.log(`${value.toFixed(2)}  ${pass ? 'PASS' : 'FAIL'}  ${fg} on ${bg}${label ? `  ${label}` : ''}`);
}
if (failed) process.exit(1);
