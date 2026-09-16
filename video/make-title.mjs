import { chromium } from 'playwright'

const W = 1920
const H = 1080
const OUT = '/tmp/video/shots'

const shell = (inner) => `<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
html,body{margin:0;width:${W}px;height:${H}px;background:radial-gradient(1200px 700px at 22% 12%, #16203a 0%, #0b0f16 58%);overflow:hidden}
body{font-family:'DejaVu Sans',system-ui,sans-serif;color:#e9ebf2;display:flex;flex-direction:column;justify-content:center;padding:0 120px}
.mark{font-size:56px;color:#8fa8ff;margin-bottom:18px}
h1{font-size:104px;margin:0;letter-spacing:-2.5px;font-weight:700}
.tag{font-size:38px;color:#aab3c6;margin-top:22px;max-width:1400px;line-height:1.35}
.rule{height:3px;width:220px;background:#8fa8ff;margin:40px 0}
.row{display:flex;gap:14px;flex-wrap:wrap;margin-top:44px}
.pill{font-family:'DejaVu Sans Mono',monospace;font-size:22px;color:#c9d1e0;background:#141a25;border:1px solid #262e3d;border-radius:999px;padding:12px 24px}
.small{font-size:24px;color:#7a8496;margin-top:30px}
.stat{display:flex;gap:64px;margin-top:52px}
.stat div{font-size:22px;color:#8b93a7}
.stat b{display:block;font-size:46px;color:#e9ebf2;font-weight:700;letter-spacing:-1px;margin-bottom:4px}
</style></head><body>${inner}</body></html>`

const TITLE = shell(`
  <div class="mark">◆</div>
  <h1>Estamora</h1>
  <div class="rule"></div>
  <div class="tag">Behavioural conformance for Soroban smart contracts — the specification, the runner that measures against it, and the evidence.</div>
  <div class="row">
    <span class="pill">estamora-conformance-spec</span>
    <span class="pill">estamora-conformance-runner</span>
    <span class="pill">estamora-docs</span>
    <span class="pill">estamora-app</span>
  </div>`)

const OUTRO = shell(`
  <div class="mark">◆</div>
  <h1>Conformance is not security.</h1>
  <div class="rule"></div>
  <div class="tag">A conformant verdict means a contract behaved as a named profile version requires over a named corpus — and nothing more. It is not an audit.</div>
  <div class="stat">
    <div><b>63</b>checks reported</div>
    <div><b>7</b>behavioural dimensions</div>
    <div><b>4</b>repositories, one contract</div>
  </div>
  <div class="small">estamora-docs.vercel.app &nbsp;·&nbsp; estamora-app.vercel.app &nbsp;·&nbsp; github.com/Estamora-Soroban-Layers</div>`)

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 })
for (const [name, html] of [
  ['title', TITLE],
  ['outro', OUTRO],
]) {
  await page.setContent(html, { waitUntil: 'load' })
  await page.waitForTimeout(400)
  await page.screenshot({ path: `${OUT}/${name}.png`, type: 'png' })
  console.log('ok  ', name)
}
await browser.close()
