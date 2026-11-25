#!/usr/bin/env python3
"""Build the chief of staff queue page and the record's CURRENT STATE.

Every fact comes from the items file, so a second run with the same file
writes the same page and record. The run stops, writing nothing, when the
new text holds a string listed in the banned-strings file. That file lives
in the chief of staff's local folder, never in this repo: it is a list of
private names.

Items file (JSON): date, report, stamp, shown, counts[], notes[], log,
state_before[], state_after[] (a line that starts with two spaces is kept
as written, for sub-bullets), machine{name, budget, note},
areas[{name, state, text}],
items[{area, item, why, rec, mins, asks, record, links[{text, url}]}].
Text fields take `code`, **bold** and [text](url).
"""
import argparse
import html
import json
import os
import re
import sys

HEAD = '''<title>Chief of Staff Queue</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: one narrow column. The queue is an ordered list, top of the page; areas and machine sit under it as quiet reference rows. */
:root {
  --bg: #f2f6f7;
  --surface: #ffffff;
  --fg: #13212a;
  --muted: #586a75;
  --line: #d3dde2;
  --accent: #0b6877;
  --accent-soft: #dcecef;
  --hold: #8a5300;
  --hold-soft: #f6e9d2;
  --stop: #a3261f;
  --font-text: "Instrument Sans", "Helvetica Neue", Arial, sans-serif;
  --font-data: "JetBrains Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0e1518; --surface: #151f24; --fg: #e2ebee; --muted: #8fa2ac; --line: #25343b;
    --accent: #62c4d2; --accent-soft: #173238; --hold: #e2a64f; --hold-soft: #33280f; --stop: #f08a80;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #0e1518; --surface: #151f24; --fg: #e2ebee; --muted: #8fa2ac; --line: #25343b;
  --accent: #62c4d2; --accent-soft: #173238; --hold: #e2a64f; --hold-soft: #33280f; --stop: #f08a80;
  color-scheme: dark;
}
body {
  background: var(--bg); color: var(--fg);
  font-family: var(--font-text); font-size: 16px; line-height: 1.5;
  padding-block: 28px 56px;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
}
.page { max-width: 760px; margin: 0 auto; display: flex; flex-direction: column; gap: 36px; }
header { display: flex; flex-direction: column; gap: 10px; }
h1 { font-size: 30px; line-height: 1.15; font-weight: 700; letter-spacing: -0.01em; margin: 0; text-wrap: balance; }
h2 { font-size: 13px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin: 0; }
.stamp { font-family: var(--font-data); font-size: 13px; color: var(--muted); }
.counts { display: flex; flex-wrap: wrap; gap: 8px 24px; font-size: 15px; }
.counts b { font-family: var(--font-data); font-weight: 500; font-variant-numeric: tabular-nums; }
section { display: flex; flex-direction: column; gap: 14px; }
ol.queue { list-style: none; margin: 0; padding: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; }
ol.queue li { display: grid; grid-template-columns: 28px minmax(0, 1fr); gap: 4px 10px; padding: 16px; border-top: 1px solid var(--line); }
ol.queue li:first-child { border-top: 0; }
.n { font-family: var(--font-data); font-size: 14px; color: var(--muted); padding-top: 2px; font-variant-numeric: tabular-nums; }
.body { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.top { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 10px; }
.area { font-family: var(--font-data); font-size: 12px; padding: 1px 7px; border-radius: 3px; background: var(--accent-soft); color: var(--accent); white-space: nowrap; }
.item { font-weight: 600; min-width: 0; }
.why { color: var(--muted); font-size: 15px; max-width: 65ch; }
.rec { font-size: 15px; max-width: 65ch; }
.rec code { font-family: var(--font-data); font-size: 13.5px; background: var(--accent-soft); color: var(--fg); padding: 1px 6px; border-radius: 3px; overflow-wrap: anywhere; }
.meta { display: flex; flex-wrap: wrap; gap: 4px 16px; font-family: var(--font-data); font-size: 13px; color: var(--muted); }
a { color: var(--accent); text-underline-offset: 3px; }
a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }
dl.rows { margin: 0; display: flex; flex-direction: column; border-top: 1px solid var(--line); }
dl.rows > div { display: grid; grid-template-columns: 170px minmax(0, 1fr); gap: 4px 16px; padding: 12px 0; border-bottom: 1px solid var(--line); }
dl.rows dt { font-family: var(--font-data); font-size: 13.5px; display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px; }
dl.rows dd { margin: 0; font-size: 15px; min-width: 0; }
.state { font-size: 12px; padding: 0 6px; border-radius: 3px; border: 1px solid var(--line); color: var(--muted); }
.state.hold { background: var(--hold-soft); color: var(--hold); border-color: transparent; }
.budget { font-family: var(--font-data); font-size: 13px; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px; overflow-x: auto; white-space: nowrap; }
.zero { color: var(--stop); font-weight: 500; }
.note { color: var(--muted); font-size: 14px; max-width: 65ch; margin: 0; }
@media (max-width: 520px) {
  h1 { font-size: 25px; }
  dl.rows > div { grid-template-columns: minmax(0, 1fr); }
}
</style>
'''


def die(msg):
    sys.exit(f"refuse: {msg}")


def inline(text):
    """Escape plain text, then turn `code`, **bold** and [text](url) into markup."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', out)


def load_banned(path):
    if not os.path.isfile(path):
        die(f"no banned-strings file at {path}")
    lines = [l.rstrip("\n") for l in open(path, encoding="utf-8")]
    banned = [l for l in lines if l.strip() and not l.startswith("# ")]
    if not banned:
        die(f"the banned-strings file at {path} is empty")
    return banned


def li(n, it):
    links = "".join(f'<a href="{html.escape(l["url"])}">{html.escape(l["text"])}</a>' for l in it.get("links", []))
    return f"""      <li>
        <span class="n">{n}</span>
        <div class="body">
          <div class="top"><span class="area">{html.escape(it["area"])}</span><span class="item">{inline(it["item"])}</span></div>
          <div class="why">{inline(it["why"])}</div>
          <div class="rec">{inline(it["rec"])}</div>
          <div class="meta"><span>{it["mins"]} min</span>{links}</div>
        </div>
      </li>"""


def build_page(d):
    items, shown = d["items"], d.get("shown", 8)
    counts = [f'<span><b>{len(items)}</b> waiting on you, {min(shown, len(items))} shown</span>']
    counts += [f"<span>{inline(c)}</span>" for c in d.get("counts", [])]
    counts.append(f'<span>about <b>{sum(i["mins"] for i in items)} min</b> to clear</span>')
    areas = "\n".join(
        f"""      <div>
        <dt>{html.escape(a["name"])} <span class="state{' hold' if a["state"] == 'hold' else ''}">{html.escape(a["state"])}</span></dt>
        <dd>{inline(a["text"])}</dd>
      </div>""" for a in d["areas"])
    m = d["machine"]
    nl = "\n"
    return HEAD + f"""
<div class="page">
  <header>
    <h1>Chief of Staff Queue</h1>
    <div class="stamp">{html.escape(d["report"])} · {html.escape(d["stamp"])} · rebuilt at every report</div>
    <div class="counts">
      {(nl + "      ").join(counts)}
    </div>
  </header>

  <section aria-labelledby="q">
    <h2 id="q">Needs you, in order</h2>
    <ol class="queue">
{nl.join(li(n + 1, it) for n, it in enumerate(items[:shown]))}
    </ol>
{nl.join(f'    <p class="note">{inline(n)}</p>' for n in d.get("notes", []))}
  </section>

  <section aria-labelledby="a">
    <h2 id="a">Areas</h2>
    <dl class="rows">
{areas}
    </dl>
  </section>

  <section aria-labelledby="m">
    <h2 id="m">Machine {html.escape(m["name"])}</h2>
    <div class="budget">{html.escape(m["budget"])}</div>
    <p class="note">{inline(m["note"])}</p>
  </section>
</div>
"""


def bullet(text):
    """A state line is a bullet; one that starts with two spaces is kept as a sub-bullet."""
    return text if text.startswith("  ") else f"- {text}"


def build_state(d):
    items, shown = d["items"], d.get("shown", 8)
    lines = ["## CURRENT STATE", "", f'As of the {d["report"][0].lower() + d["report"][1:]}, {d["stamp"]}.', ""]
    lines += [bullet(b) for b in d.get("state_before", [])]
    lines.append(f"- Open owner asks ({len(items)}), in queue order; the page shows the first {min(shown, len(items))}:")
    lines += [f'  {n + 1}. {it["area"]}: {it["record"]}' for n, it in enumerate(items)]
    lines += [bullet(b) for b in d.get("state_after", [])]
    return "\n".join(lines) + "\n\n"


def build_record(d, old):
    """Keep the old header and Log, replace CURRENT STATE, add the log line once."""
    log = f'- {d["log"]}'
    header = d.get("header", f'# Chief of staff record, {d["date"]}\n\nCommitted at each report and at handoff, not at every tick.\n')
    tail = []
    if old:
        if "## CURRENT STATE" not in old or "## Log" not in old:
            die("the record has no CURRENT STATE or no Log heading")
        header = old[:old.index("## CURRENT STATE")].rstrip("\n") + "\n"
        tail = [l for l in old[old.index("## Log"):].splitlines()[1:] if l.strip() and l != log]
    return header.rstrip("\n") + "\n\n" + build_state(d) + "## Log\n\n" + "\n".join(tail + [log]) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--items", required=True, help="items file (JSON)")
    ap.add_argument("--record", required=True, help="the day's record file, rewritten in place")
    ap.add_argument("--page", required=True, help="where to write the queue page")
    ap.add_argument("--banned", required=True, help="file of strings that stop the run, one per line")
    ap.add_argument("--dry", action="store_true", help="build and scan, write nothing")
    a = ap.parse_args()

    d = json.load(open(a.items, encoding="utf-8"))
    missing = [k for k in ("date", "report", "stamp", "log", "items", "areas", "machine") if k not in d]
    if missing:
        die(f"the items file lacks {missing}")
    banned = load_banned(a.banned)
    old = open(a.record, encoding="utf-8").read() if os.path.exists(a.record) else ""
    page, record = build_page(d), build_record(d, old)
    new_text = build_state(d) + d["log"]
    for name, text in (("page", page), ("record", new_text)):
        hits = [b for b in banned if b in text]
        if hits:
            die(f"banned strings in the {name}: {hits}")

    items = d["items"]
    print(f'{"dry" if a.dry else "wrote"}: items={len(items)} minutes={sum(i["mins"] for i in items)} '
          f'one_by_one={sum(i.get("asks", 1) for i in items)} page_bytes={len(page.encode())}')
    if a.dry:
        return
    open(a.page, "w", encoding="utf-8").write(page)
    open(a.record, "w", encoding="utf-8").write(record)


if __name__ == "__main__":
    main()
