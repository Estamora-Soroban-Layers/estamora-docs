# The pitch video, and how it is made

**Watch it: <https://estamora-docs.vercel.app/assets/estamora-pitch.mp4>** (or the
[archived release copy](https://github.com/Estamora-Soroban-Layers/estamora-docs/releases/download/pitch-v1/estamora-pitch.mp4),
which downloads rather than plays — release assets are served as
`application/octet-stream` with `content-disposition: attachment`).
— 5:14, 1920×1080.

The pipeline that produces it is committed here, which is the point. A pitch video is
normally a binary artefact that exists in one place and can never be corrected when a figure
in it goes stale. This one can be regenerated, and `verify.mjs` -- run by the `video` job on
every push -- is what decides whether it still is.

**That check answers two different questions, and the second is the one nothing else asks.**
Does the published file actually play in a browser, as opposed to being served? And is every
figure the narration states still true? A video is a recording of a project at a moment, and
nothing breaks when the project moves on: the file still plays, every link still resolves, and
the voice calmly states a number that is now wrong. So the check reads the numbers out of the
artefacts that own them -- the committed conformance report for the 63 checks, the seven
dimensions and the 19 undecided vectors, the organization's repository list for the four
project repositories -- and compares them with what the video says.

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

And, at any time, without rendering anything:

```bash
npm install --prefix video      # one dependency, pinned
node video/verify.mjs           # does it play, and is what it says still true?
```

| File | Does |
| --- | --- |
| `scenes.json` | The script: one entry per scene, with its shot, its caption and its narration |
| `capture.mjs` | Playwright capture. Live pages, plus terminal and code slides rendered from real output |
| `make-title.mjs` | The title and outro cards |
| `tts.py` | Neural narration via piper, one file per scene, offline |
| `compose.py` | ffmpeg: captions, fades, encode, and assertions on the result |
| `verify.mjs` | The published file plays in a browser, and every figure the narration states still matches the artefact that owns it |
| `capture-readme-shots.mjs` | The stills the four READMEs embed, captured from the deployed sites |

## Three decisions worth knowing

**The narration is synthesised locally, not by a hosted service.** No API key, no per-character
cost, and the voice is a file. It also means the video can be rebuilt by anybody who checks
out this repository, which is the difference between a committed artefact and a committed
pipeline.

**The Playwright version is pinned to the one that can decode this file.** Playwright ships a
different Chromium build per release, and `1.48`'s cannot decode H.264: the element never reaches
`HAVE_METADATA` and the check reports a broken player for a reason that has nothing to do with the
video. `1.63.0` was verified to decode it. That is worth knowing before upgrading, because the
symptom of getting it wrong looks exactly like the defect the check exists to find.

**The stills are captured without animations, and one of them cannot be reproducible.** The app
animates a small status element, so the same unchanged page produced different bytes on consecutive
captures — `app-overview` differed in a 10x4 CSS px region between two runs taken seconds apart. A
README image that cannot be repeated cannot be regenerated without a diff nobody can explain, and a
diff nobody can explain is one that gets committed anyway, so the capture now asks for reduced
motion. That changed nothing about what the shots show, which is the point: it makes them
repeatable. The exception is `app-live-contract`, which states the ledger it read and the ledger
advances — three consecutive reads reported `4,710,322`, `4,710,323`, `4,710,323`. Expect a small
diff there when re-capturing it, and check that it is confined to that figure: a diff anywhere else
is a change to the page.

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
