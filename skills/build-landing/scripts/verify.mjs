// Guards the lesson: "Headless Chrome cannot produce a 390px capture on macOS."
// Also: "For a landing page the browser harness is the test suite." Read the evidence, not the verdict.
import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { execSync } from 'node:child_process';

const usage = `Usage:
  verify.mjs --url http://127.0.0.1:4403 --out evidence/ [options]

  --viewports 1440x900,390x844   viewports to check (default 1440x900,390x844)
  --header <css selector>        header element; checks it stays pinned or hides deliberately
  --anchor <id>                  in-page anchor id, without the '#'
  --outbound <host>              every link to this host must carry utm_source
  --article </path/>             second page to load for console errors

Writes checks.json and screenshots to --out. Exits 1 if any check fails.
reducedMotion sees CSS and Web Animations only; a requestAnimationFrame loop needs a site-specific check.
Playwright: a local install is used when present, else the global one (npm root -g); Chrome must be installed.`;

const argv = process.argv.slice(2);
if (argv.length === 0 || argv.includes('--help')) { console.log(usage); process.exit(argv.length === 0 ? 1 : 0); }
const flag = name => { const i = argv.indexOf(name); return i === -1 ? null : argv[i + 1]; };
const url = flag('--url');
const out = flag('--out');
if (!url || !out) { console.error('--url and --out are required'); process.exit(1); }
const viewports = (flag('--viewports') ?? '1440x900,390x844').split(',').map(v => {
  const [width, height] = v.split('x').map(Number);
  return { width, height };
});
const headerSelector = flag('--header');
const anchor = flag('--anchor');
const outbound = flag('--outbound');
const article = flag('--article');
mkdirSync(out, { recursive: true });

const localRequire = createRequire(resolve(process.cwd(), 'package.json'));
const { chromium } = (() => {
  try { return localRequire('playwright'); } catch {}
  const globalRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
  return createRequire(resolve(globalRoot, '@playwright/test/package.json'))('playwright');
})();

const checks = {};
const screenshots = [];
const record = (name, pass, value) => { checks[name] = { pass: Boolean(pass), value }; };
const pause = page => page.waitForTimeout(650);
const settle = async page => { await page.evaluate(() => document.fonts.ready).catch(() => {}); await pause(page); };
const scroll = async (page, y) => { await page.evaluate(y => scrollTo(0, y), y); await pause(page); };
const overflow = page => page.evaluate(() => ({ scrollWidth: document.scrollingElement.scrollWidth, innerWidth, scrollY }));
const box = async (page, selector) => {
  const el = page.locator(selector).first();
  if (await el.count() === 0) return { missing: selector, top: NaN, bottom: NaN, height: NaN, position: 'none' };
  return el.evaluate(el => {
    const r = el.getBoundingClientRect();
    return { top: r.top, bottom: r.bottom, height: r.height, position: getComputedStyle(el).position };
  });
};
const shoot = async (page, name, fullPage = false) => {
  const path = resolve(out, name);
  await page.screenshot({ path, fullPage });
  screenshots.push(path);
};

const browser = await chromium.launch({ channel: 'chrome' });
try {
  for (const { width, height } of viewports) {
    const tag = String(width);
    const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 2 });
    const page = await context.newPage();
    const errors = [];
    let route = '/';
    page.on('console', msg => { if (msg.type() === 'error') errors.push({ route, type: 'console', text: msg.text() }); });
    page.on('pageerror', error => errors.push({ route, type: 'pageerror', text: error.message }));

    await page.goto(url);
    await settle(page);
    const overflowTop = await overflow(page);
    await shoot(page, `top-${tag}.png`);

    // Tab first: setting the hash or scrolling moves the sequential focus start point.
    await page.keyboard.press('Tab');
    const focus = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body) return null;
      const style = getComputedStyle(el);
      return { tag: el.tagName, className: el.className, outlineStyle: style.outlineStyle, outlineWidth: style.outlineWidth, boxShadow: style.boxShadow };
    });
    record(`keyboardFocusVisible:${tag}`, focus && (focus.outlineStyle !== 'none' || (focus.boxShadow && focus.boxShadow !== 'none')), focus);

    const details = await page.evaluate(() => {
      const found = [...document.querySelectorAll('details')].findIndex(d => d.querySelector('summary')?.checkVisibility());
      return { count: document.querySelectorAll('details').length, index: found };
    });
    if (details.count === 0) record(`detailsKeyboard:${tag}`, true, 'no details on the page');
    else if (details.index === -1) record(`detailsKeyboard:${tag}`, false, { ...details, note: 'every summary is hidden at this viewport' });
    else {
      const summary = page.locator('details').nth(details.index).locator('summary').first();
      const identity = await summary.evaluate(el => ({ text: el.innerText.trim(), parentClass: el.parentElement.className }));
      await summary.focus();
      await page.keyboard.press('Enter'); await pause(page);
      const opened = await page.locator('details').nth(details.index).evaluate(el => el.open);
      await page.keyboard.press('Enter'); await pause(page);
      const closed = !(await page.locator('details').nth(details.index).evaluate(el => el.open));
      record(`detailsKeyboard:${tag}`, opened && closed, { ...identity, opened, closed });
    }

    if (headerSelector) {
      await scroll(page, 800);
      const header = await box(page, headerSelector);
      const pinned = Math.abs(header.top) <= 1;
      const hidden = header.bottom <= 0 && ['sticky', 'fixed'].includes(header.position);
      record(`stickyHeader:${tag}`, pinned || hidden, { mode: header.missing ? 'selector not found' : pinned ? 'pinned' : hidden ? 'hides on scroll' : 'scrolled away', ...header });
    }

    if (anchor) {
      await scroll(page, 0);
      await page.evaluate(id => { location.hash = `#${id}`; }, anchor);
      await pause(page); await pause(page);
      const target = await box(page, `#${anchor}`);
      const header = headerSelector ? await box(page, headerSelector) : { bottom: 0 };
      const floor = Math.max(0, header.bottom || 0);
      record(`anchorOffset:${tag}`, !target.missing && target.top >= floor - 1, { targetTop: target.top, headerBottom: header.bottom, floor, missing: target.missing ?? null });
    }

    if (outbound) {
      const links = await page.locator('a[href]').evaluateAll((all, host) => all
        .map(a => a.href)
        .filter(href => { try { const h = new URL(href).hostname; return h === host || h.endsWith(`.${host}`); } catch { return false; } })
        .map(href => ({ href, hasUtmSource: new URL(href).searchParams.has('utm_source') })), outbound);
      record(`outboundAttribution:${tag}`, links.length > 0 && links.every(l => l.hasUtmSource), links);
    }

    await page.evaluate(() => scrollTo(0, document.scrollingElement.scrollHeight));
    await pause(page);
    const overflowBottom = await overflow(page);
    record(`noOverflow:${tag}`, [overflowTop, overflowBottom].every(v => v.scrollWidth <= v.innerWidth), { top: overflowTop, bottom: overflowBottom });
    await shoot(page, `full-${tag}.png`, true);

    if (article) { route = article; await page.goto(new URL(article, url).href); await settle(page); }
    record(`consoleClean:${tag}`, errors.length === 0, errors);
    await context.close();
  }

  const first = viewports[0];
  const reduced = await browser.newContext({ viewport: first, deviceScaleFactor: 2, reducedMotion: 'reduce' });
  const reducedPage = await reduced.newPage();
  await reducedPage.goto(url); await settle(reducedPage);
  const motion = await reducedPage.evaluate(() => ({
    running: document.getAnimations().filter(a => a.playState === 'running').map(a => a.animationName ?? a.constructor.name),
    textLength: document.body.innerText.length,
  }));
  record('reducedMotion', motion.running.length === 0 && motion.textLength > 200, motion);
  await reduced.close();

  const noJs = await browser.newContext({ viewport: first, deviceScaleFactor: 2, javaScriptEnabled: false });
  const noJsPage = await noJs.newPage();
  await noJsPage.goto(url); await noJsPage.waitForTimeout(650);
  const stateWithoutJs = {
    textLength: (await noJsPage.locator('body').innerText()).length,
    h1Visible: await noJsPage.locator('h1').first().evaluate(el => el.checkVisibility()),
  };
  record('noJs', stateWithoutJs.textLength > 200 && stateWithoutJs.h1Visible, stateWithoutJs);
  await noJs.close();
} catch (error) {
  record('executionComplete', false, { error: error.stack });
} finally {
  await browser.close();
  const report = { url, checks, screenshots };
  writeFileSync(resolve(out, 'checks.json'), `${JSON.stringify(report, null, 2)}\n`);
  console.log(JSON.stringify(report, null, 2));
  if (Object.values(checks).some(check => !check.pass)) process.exitCode = 1;
}
