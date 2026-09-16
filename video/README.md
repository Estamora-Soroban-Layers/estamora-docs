# The pitch video, and how it is made

**Watch it: <https://github.com/Estamora-Soroban-Layers/estamora-docs/releases/download/pitch-v1/estamora-pitch.mp4>**
— 5:14, 1920×1080.

The pipeline that produces it is committed here, which is the point. A pitch video is
normally a binary artefact that exists in one place and can never be corrected when a figure
in it goes stale. This one can be regenerated, and `video/verify` in CI is what keeps the
figures in it honest.

## Nothing in it is a mock-up

Every frame is either a live deployment read over HTTP or output a program actually produced:

| Source | What it is |
| --- | --- |
| `estamora-app.vercel.app` | The deployed application: overview, report view, the audit findings, a live testnet read |
| `estamora-docs.vercel.app` | The deployed documentation: the authorization model, the exit-code contract, the report format |
| the release binary | Its own `--help`, and a real run against `fixture:skips-authorization` that exits 1 |
| the fixture source | The real `is_valid_amount` guard, read from the repository |
| the organization page | The profile and the issue list |

`capture.mjs` fails loudly rather than substituting a placeholder, so a video cannot be
produced from a deployment that is down.

## Regenerating it

Three tools, all installable, none of them a service you need an account for:

```bash
pip install -r <(echo mkdocs-material)   # not needed here; see the list below
apt-get install -y ffmpeg espeak-ng
npm install playwright && npx playwright install --with-deps chromium
python3 -m venv /tmp/ttsvenv && /tmp/ttsvenv/bin/pip install piper-tts
```

Then, from this directory:

```bash
node capture.mjs        # film the live deployments and the real program output
node make-title.mjs     # the title and outro cards
python3 tts.py          # synthesise the narration locally
python3 compose.py      # render estamora-pitch.mp4
```

| File | Does |
| --- | --- |
| `scenes.json` | The script: one entry per scene, with its shot, its caption and its narration |
| `capture.mjs` | Playwright capture. Live pages, plus terminal and code slides rendered from real output |
| `make-title.mjs` | The title and outro cards |
| `tts.py` | Neural narration via piper, one file per scene, offline |
| `compose.py` | ffmpeg: captions, fades, encode, and assertions on the result |

## Two decisions worth knowing

**The narration is synthesised locally, not by a hosted service.** No API key, no per-character
cost, and the voice is a file. It also means the video can be rebuilt by anybody who checks
out this repository, which is the difference between a committed artefact and a committed
pipeline.

**`compose.py` asserts what it produced.** It checks the finished file is 1920×1080, that its
duration matches the sum of the scene durations within a second and a half, and that a scene
is not missing from the concatenation. A video that silently drops a scene is worse than one
that fails to render, because nobody notices until a judge does.

Captions are passed to `drawtext` with `textfile=` rather than inline. That is not tidiness: a
colon or an apostrophe in an inline filter expression truncates the caption silently, and the
result looks deliberate.

## Editing the script

Change `scenes.json` and re-run `tts.py` then `compose.py`. The narration duration drives the
scene duration, so there is no timeline to keep in sync by hand — the cut follows the voice.

If you change a figure that is *also* asserted somewhere else — the 63 checks, the seven
dimensions, the four repositories — change it in the repository that owns it first. The video
is downstream of every other artefact here, never the source of one.
