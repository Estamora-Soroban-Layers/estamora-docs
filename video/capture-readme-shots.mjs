/**
 * Capture the screenshots the READMEs embed.
 *
 * Every shot here is of the deployed site, not of a local dev server, because the thing a
 * README promises is what a reader will see when they click the link. A screenshot taken
 * against `localhost` can show a page that has never been deployed.
 *
 * Each capture waits for the page to have actually produced content -- the app fetches a
 * report over the network and reads a contract over RPC before it has anything to show, so
 * "load" is not the same as "ready". Shooting too early is how a README ends up illustrating
 * a spinner.
 *
 * Animations are suppressed with `reducedMotion: 'reduce'`, and that is a correctness fix rather
 * than a preference. Without it the capture was not reproducible: the app animates a small status
 * element, so the same unchanged page produced different bytes on consecutive runs -- `app-overview`
 * differed in a 10x4 CSS px region between two captures taken seconds apart, which is a diff nobody
 * can explain and therefore one that gets committed anyway. Settling the animation changed nothing
 * about what the shot shows; it only made it repeatable.
 *
 * What was measured after the change, so that a later diff can be read rather than guessed at:
 *
 *   app-conformance-report, docs-landing, spec-profiles   byte-identical across runs
 *   app-overview                                          at most a 2x2 CSS px region (9 pixels in
 *                                                         a 2880x2000 image), and only sometimes
 *   app-live-contract                                     not reproducible, see below
 *
 * `app-live-contract` states the ledger it read, and the ledger advances: three consecutive reads
 * reported 4,710,322, 4,710,323, 4,710,323. That shot is a real measurement rather than a rendering
 * of one, so its last digits move and always will. When re-capturing it, expect a small diff there
 * and check that it is confined to that figure -- a diff anywhere else is a change to the page.
 */

import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

const OUT = process.argv[2];
if (!OUT) throw new Error('usage: node capture-readme-shots.mjs <output-dir>');

const SHOTS = [
  {
    name: 'app-overview',
    url: 'https://estamora-app.vercel.app/#/overview',
    // The overview states the report's status once the committed report has loaded.
    ready: 'text=CONFORMANT',
    height: 1000,
  },
  {
    name: 'app-conformance-report',
    url: 'https://estamora-app.vercel.app/#/report',
    ready: 'text=checks',
    height: 1200,
  },
  {
    name: 'app-live-contract',
    url: 'https://estamora-app.vercel.app/#/inspect',
    // The contract identifier is prefilled from `EXAMPLE_CONTRACT`, but nothing has been
    // read until the button is pressed. A screenshot of the form before the call would
    // show an empty result panel, which is not what the README is describing.
    click: 'button:has-text("Read interface")',
    // This view has read a real testnet contract once the symbol is on screen.
    ready: 'text=Measurable Token',
    height: 900,
  },
  {
    name: 'docs-landing',
    url: 'https://estamora-docs.vercel.app/',
    ready: 'text=Estamora',
    height: 1000,
  },
  {
    name: 'spec-profiles',
    url: 'https://estamora-soroban-layers.github.io/estamora-conformance-spec/',
    ready: 'body',
    height: 900,
  },
];

await mkdir(OUT, { recursive: true });

const browser = await chromium.launch();
let failed = 0;

for (const shot of SHOTS) {
  const page = await browser.newPage({
    viewport: { width: 1440, height: shot.height },
    deviceScaleFactor: 2,
    colorScheme: 'light',
    // See the header: without this the same unchanged page does not produce the same bytes.
    reducedMotion: 'reduce',
  });
  try {
    await page.goto(shot.url, { waitUntil: 'load', timeout: 60_000 });
    if (shot.click) {
      await page.click(shot.click, { timeout: 20_000 });
    }
    await page.waitForSelector(shot.ready, { timeout: 45_000 });
    // Let webfonts settle so the capture is not of a fallback face.
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(1200);
    await page.screenshot({ path: `${OUT}/${shot.name}.png`, fullPage: false });
    const text = (await page.locator('body').innerText()).length;
    console.log(`ok   ${shot.name.padEnd(26)} ${text} chars of body text`);
  } catch (error) {
    failed += 1;
    console.log(`FAIL ${shot.name.padEnd(26)} ${error.message.split('\n')[0]}`);
  } finally {
    await page.close();
  }
}

await browser.close();
console.log(failed === 0 ? '\nall shots captured' : `\n${failed} shot(s) failed`);
process.exit(failed === 0 ? 0 : 1);
