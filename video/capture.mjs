/**
 * Capture every frame of the pitch video from the real things.
 *
 * Nothing here invents a screenshot. Each shot is either a live deployment read over HTTP, or
 * a rendering of text a program actually produced -- the release binary's own `--help`, and a
 * real run against a fixture that is wrong in exactly one way. A pitch video full of mock-ups
 * is a claim; footage of the actual output is evidence.
 */

import { chromium } from 'playwright'
import { mkdir, readFile, writeFile } from 'node:fs/promises'

const WIDTH = 1920
const HEIGHT = 1080
const OUT = '/tmp/video/shots'
const CAPTURES = '/tmp/video/captures'
const RUNNER = '/workspaces/estamora-conformance-runner'

const APP = 'https://estamora-app.vercel.app'
const DOCS = 'https://estamora-docs.vercel.app'
const ORG = 'https://github.com/Estamora-Soroban-Layers'

const results = []
function note(name, message) {
  results.push(`${message ? 'FAIL' : 'ok  '} ${name}${message ? ` — ${message}` : ''}`)
}

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, (character) => {
    switch (character) {
      case '&':
        return '&amp;'
      case '<':
        return '&lt;'
      case '>':
        return '&gt;'
      case '"':
        return '&quot;'
      default:
        return '&#39;'
    }
  })
}

/** Colour a captured CLI transcript the way the terminal would, without altering a character. */
function transcript(lines) {
  return lines
    .map((line) => {
      const text = escapeHtml(line)
      if (line.startsWith('✓')) return `<span class="pass">${text}</span>`
      if (line.startsWith('✗')) return `<span class="fail">${text}</span>`
      if (line.startsWith('·') || line.startsWith('    ·'))
        return `<span class="dim">${text}</span>`
      if (line.trimStart().startsWith('status')) return `<span class="status">${text}</span>`
      if (/^[─═]/.test(line)) return `<span class="rule">${text}</span>`
      if (/^\s+[a-z]+\s+\d+ passed/.test(line)) return `<span class="summary">${text}</span>`
      return `<span>${text}</span>`
    })
    .join('\n')
}

function terminalSlide({ command, lines, caption }) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{box-sizing:border-box}
  html,body{margin:0;width:${WIDTH}px;height:${HEIGHT}px;background:#0b0f16;overflow:hidden}
  body{font-family:'DejaVu Sans',system-ui,sans-serif;color:#e9ebf2;padding:54px 64px}
  .head{display:flex;align-items:baseline;gap:18px;margin-bottom:8px}
  .title{font-size:40px;font-weight:700;letter-spacing:-.5px}
  .caption{font-size:22px;color:#8b93a7;margin-bottom:26px;max-width:1500px;line-height:1.45}
  .win{background:#11161f;border:1px solid #232a37;border-radius:14px;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,.5)}
  .bar{display:flex;align-items:center;gap:10px;padding:14px 18px;background:#161c27;border-bottom:1px solid #232a37}
  .dot{width:13px;height:13px;border-radius:50%}
  .cmd{margin-left:10px;font-family:'DejaVu Sans Mono',monospace;font-size:19px;color:#9dbaff}
  pre{margin:0;padding:22px 26px;font-family:'DejaVu Sans Mono',monospace;font-size:${lines.length > 60 ? 15 : 18}px;line-height:1.42;white-space:pre;overflow:hidden;color:#c9d1e0}
  .pass{color:#6fd3a3}.fail{color:#f08c85}.dim{color:#7a8496}.rule{color:#39414f}
  .status{color:#ffd479;font-weight:700}.summary{color:#c9d1e0}
  </style></head><body>
  <div class="head"><div class="title">${escapeHtml(caption.title)}</div></div>
  <div class="caption">${escapeHtml(caption.body)}</div>
  <div class="win">
    <div class="bar">
      <span class="dot" style="background:#ff5f57"></span>
      <span class="dot" style="background:#febc2e"></span>
      <span class="dot" style="background:#28c840"></span>
      <span class="cmd">${escapeHtml(command)}</span>
    </div>
    <pre>${transcript(lines)}</pre>
  </div>
  </body></html>`
}

function codeSlide({ code, caption, highlight = [] }) {
  const body = code
    .map((line, index) => {
      const marked = highlight.includes(index + 1)
      const text = escapeHtml(line)
      return `<span class="${marked ? 'hit' : ''}">${text}</span>`
    })
    .join('\n')
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{box-sizing:border-box}
  html,body{margin:0;width:${WIDTH}px;height:${HEIGHT}px;background:#0b0f16;overflow:hidden}
  body{font-family:'DejaVu Sans',system-ui,sans-serif;color:#e9ebf2;padding:54px 64px}
  .title{font-size:40px;font-weight:700;letter-spacing:-.5px;margin-bottom:8px}
  .caption{font-size:22px;color:#8b93a7;margin-bottom:26px;max-width:1560px;line-height:1.45}
  .win{background:#11161f;border:1px solid #232a37;border-radius:14px;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,.5)}
  .bar{display:flex;align-items:center;gap:10px;padding:14px 18px;background:#161c27;border-bottom:1px solid #232a37}
  .dot{width:13px;height:13px;border-radius:50%}
  .cmd{margin-left:10px;font-family:'DejaVu Sans Mono',monospace;font-size:19px;color:#9dbaff}
  pre{margin:0;padding:22px 26px;font-family:'DejaVu Sans Mono',monospace;font-size:${code.length > 34 ? 17 : 21}px;line-height:1.5;white-space:pre;overflow:hidden;color:#aeb8cc}
  .hit{background:rgba(240,140,133,.14);color:#ffd0cb;display:block}
  </style></head><body>
  <div class="title">${escapeHtml(caption.title)}</div>
  <div class="caption">${escapeHtml(caption.body)}</div>
  <div class="win">
    <div class="bar">
      <span class="dot" style="background:#ff5f57"></span>
      <span class="dot" style="background:#febc2e"></span>
      <span class="dot" style="background:#28c840"></span>
      <span class="cmd">${escapeHtml(caption.file)}</span>
    </div>
    <pre>${body}</pre>
  </div>
  </body></html>`
}

function diagramSlide({ caption, svg }) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{box-sizing:border-box}
  html,body{margin:0;width:${WIDTH}px;height:${HEIGHT}px;background:#0b0f16;overflow:hidden}
  body{font-family:'DejaVu Sans',system-ui,sans-serif;color:#e9ebf2;padding:54px 64px}
  .title{font-size:40px;font-weight:700;letter-spacing:-.5px;margin-bottom:8px}
  .caption{font-size:22px;color:#8b93a7;margin-bottom:20px;max-width:1560px;line-height:1.45}
  </style></head><body>
  <div class="title">${escapeHtml(caption.title)}</div>
  <div class="caption">${escapeHtml(caption.body)}</div>
  ${svg}
  </body></html>`
}

async function shoot(page, name) {
  const path = `${OUT}/${name}.png`
  await page.screenshot({ path, type: 'png' })
  return path
}

async function main() {
  await mkdir(OUT, { recursive: true })
  const browser = await chromium.launch()
  const page = await browser.newPage({
    viewport: { width: WIDTH, height: HEIGHT },
    deviceScaleFactor: 1,
  })

  // ---------- live deployments ----------
  const live = [
    ['app-overview', `${APP}/#/overview`, 'h1'],
    ['app-docs', `${APP}/#/docs`, 'h1'],
    ['docs-home', `${DOCS}/`, 'h1'],
    ['docs-exit-codes', `${DOCS}/reference/exit-codes/`, 'h1'],
    ['docs-report-format', `${DOCS}/reference/report-format/`, 'h1'],
    ['docs-auth-model', `${DOCS}/spec/authorization-model/`, 'h1'],
    ['docs-runner-cli', `${DOCS}/runner/cli/`, 'h1'],
  ]
  for (const [name, url, selector] of live) {
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
      await page.waitForSelector(selector, { timeout: 30000 })
      await page.evaluate(() => window.scrollTo(0, 0))
      await page.waitForTimeout(600)
      await shoot(page, name)
      note(name)
    } catch (problem) {
      note(name, problem.message)
    }
  }

  // The report view fetches the report and the schema, then renders a verdict. Waiting for
  // the verdict is waiting for the application to have actually done the thing being filmed.
  try {
    await page.goto(`${APP}/#/report`, { waitUntil: 'networkidle', timeout: 60000 })
    await page.waitForSelector('.verdict-headline', { timeout: 60000 })
    await page.waitForTimeout(1200)
    await shoot(page, 'app-report')
    note('app-report')

    // And the audit findings, which are the reason the view exists.
    await page.evaluate(() => {
      const heading = [...document.querySelectorAll('h3')].find((h) =>
        h.textContent?.includes('own rules'),
      )
      heading?.scrollIntoView({ block: 'start' })
    })
    await page.waitForTimeout(700)
    await shoot(page, 'app-report-audit')
    note('app-report-audit')
  } catch (problem) {
    note('app-report', problem.message)
  }

  // The live contract read: press the button and wait for values that came off the network.
  try {
    await page.goto(`${APP}/#/inspect`, { waitUntil: 'networkidle', timeout: 60000 })
    await page.waitForSelector('#contract-id', { timeout: 30000 })
    await page.click('button:has-text("Read interface")')
    await page.waitForSelector('.reading', { timeout: 60000 })
    await page.waitForTimeout(800)
    await shoot(page, 'app-inspector')
    note('app-inspector')
  } catch (problem) {
    note('app-inspector', problem.message)
  }

  // ---------- terminal transcripts, from the real binary ----------
  try {
    const help = (await readFile(`${CAPTURES}/help.txt`, 'utf8')).split('\n')
    await page.setContent(
      terminalSlide({
        command: 'estamora --help',
        lines: help.slice(0, 30),
        caption: {
          title: 'Six commands, one question each',
          body: 'Only `run` reaches a verdict. `validate` and `profile` deploy nothing; `inspect` deploys and reads, and states that an interface is not evidence of behaviour.',
        },
      }),
      { waitUntil: 'load' },
    )
    await shoot(page, 'terminal-help')
    note('terminal-help')
  } catch (problem) {
    note('terminal-help', problem.message)
  }

  try {
    const run = (await readFile(`${CAPTURES}/run-bad.txt`, 'utf8')).split('\n')
    await page.setContent(
      terminalSlide({
        command: 'estamora run --profile sep-41@1.0 --contract fixture:skips-authorization',
        lines: run.slice(0, 26),
        caption: {
          title: 'A contract that is wrong in exactly one way',
          body: 'The fixture omits one `require_auth` call. The profile notices it in the authorization plan, the refusal, the events, the state and the failure category — five dimensions from one missing line.',
        },
      }),
      { waitUntil: 'load' },
    )
    await shoot(page, 'terminal-run')
    note('terminal-run')

    await page.setContent(
      terminalSlide({
        command: 'estamora run --profile sep-41@1.0 --contract fixture:skips-authorization',
        lines: run.slice(-26),
        caption: {
          title: 'The verdict, and the sentence that limits it',
          body: 'Exit code 1 — the only code that names the contract as at fault. Every other failure exits something else, on purpose.',
        },
      }),
      { waitUntil: 'load' },
    )
    await shoot(page, 'terminal-verdict')
    note('terminal-verdict')
  } catch (problem) {
    note('terminal-verdict', problem.message)
  }

  // ---------- the fix, from the real source ----------
  try {
    const source = await readFile(
      `${RUNNER}/fixtures/contracts/measurable-token/src/lib.rs`,
      'utf8',
    )
    const lines = source.split('\n')
    const guard = lines.findIndex((line) => line.includes('fn is_valid_amount'))
    const burn = lines.findIndex((line) => line.includes('pub fn burn('))
    const start = guard >= 0 ? Math.max(0, guard - 6) : Math.max(0, burn - 10)
    const window = lines.slice(start, start + 40)

    // Mark the guard and the calls that use it, wherever they fall in the window.
    const highlight = window
      .map((line, index) => (index + 1))
      .filter((_, index) => {
        const line = window[index] ?? ''
        return line.includes('is_valid_amount')
      })

    await page.setContent(
      codeSlide({
        code: window,
        highlight,
        caption: {
          title: 'The rule, stated once',
          body: 'The free-mint bug existed because one rule was written in three places and implemented in two. `burn` and `burn_from` guarded nothing, so a negative amount made the balance check vacuously false and the subtraction added to the balance.',
          file: 'fixtures/contracts/measurable-token/src/lib.rs',
        },
      }),
      { waitUntil: 'load' },
    )
    await shoot(page, 'code-guard')
    note('code-guard')
  } catch (problem) {
    note('code-guard', problem.message)
  }

  // ---------- the organization ----------
  for (const [name, url] of [
    ['org-profile', ORG],
    ['org-issues', `${ORG}/estamora-conformance-runner/issues`],
  ]) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 })
      await page.waitForTimeout(2500)
      await shoot(page, name)
      note(name)
    } catch (problem) {
      note(name, problem.message)
    }
  }

  await browser.close()

  await writeFile('/tmp/video/capture-report.txt', results.join('\n') + '\n')
  console.log(results.join('\n'))
  const failures = results.filter((line) => line.startsWith('FAIL'))
  console.log(`\n ${results.length - failures.length}/${results.length} shots captured`)
}

main().catch((problem) => {
  console.error('capture failed:', problem)
  process.exit(1)
})
