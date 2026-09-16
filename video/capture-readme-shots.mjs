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
