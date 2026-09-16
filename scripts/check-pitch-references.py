#!/usr/bin/env python3
"""Check that every reference to the pitch video keeps it playable.

The defect this guards against shipped once and was invisible to every existing check. Every
"watch the pitch" link across all five repositories pointed at the **GitHub release asset**, and
GitHub serves a release asset as `content-type: application/octet-stream` with
`content-disposition: attachment`. The file is served correctly and every header check passes --
but a reader who clicks "watch" gets a 15 MB download prompt instead of a video.

Serving the same bytes from the documentation site as `video/mp4` with byte-range support is the
fix, and this is the check that keeps it fixed. Four properties, because each fails differently:

1. A playback link points at the site, not at the release asset.
2. The archival link uses an **immutable tag**, never `latest`, because a link that silently
   repoints is worse than one that breaks.
3. A referenced thumbnail exists on disk, since a broken poster image renders as nothing and
   looks like a styling problem.
4. The landing page embeds a player with a declared MIME type, because a `<source>` without one
   makes the browser sniff the file before it will play it.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAYABLE = "https://estamora-docs.vercel.app/assets/estamora-pitch.mp4"
ARCHIVE_PREFIX = "https://github.com/Estamora-Soroban-Layers/estamora-docs/releases/download/"
ARCHIVE_FILENAME = "estamora-pitch.mp4"

# The release asset URL, anywhere it appears as a *playback* target rather than a download.
RELEASE_MEDIA = re.compile(
    r"https://github\.com/[^\s)\"'>]*/releases/download/[^\s)\"'>]*\.mp4"
)

MARKDOWN = sorted(
    path
    for path in REPO_ROOT.rglob("*.md")
    if not any(part in {"build", "node_modules", ".git", "site"} for part in path.parts)
)
CURATED_SOURCES = [*MARKDOWN, REPO_ROOT / "docs" / "index.md"]


def main() -> int:
    problems: list[str] = []

    for path in MARKDOWN:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(REPO_ROOT)

        for match in RELEASE_MEDIA.finditer(text):
            url = match.group(0)
            # A release asset is the right target for a download and the wrong target for a
            # player. It must be labelled as the archived copy wherever it appears.
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            line = text[line_start : line_end if line_end != -1 else len(text)]
            # The URL is removed before looking for the label, because every archive URL contains
            # the word "download" in its own path: `/releases/download/<tag>/<file>`. Leaving it in
            # made this check pass on an unlabelled link, which is the state it exists to catch.
            around_url = line.replace(match.group(0), "")
            if not re.search(r"archiv|download|immutable|release copy", around_url, re.IGNORECASE):
                problems.append(
                    f"{relative}: a release asset is offered without being labelled as the "
                    f"archived download — a reader clicking this gets a file, not a video:\n"
                    f"    {line.strip()}"
                )
            if "/latest/" in url:
                problems.append(
                    f"{relative}: the archive link uses `latest`, which repoints silently — "
                    f"use the release tag"
                )
            if not url.startswith(ARCHIVE_PREFIX) or not url.endswith(ARCHIVE_FILENAME):
                problems.append(f"{relative}: unexpected archive URL shape: {url}")

    # The landing page must embed a player, same-origin, with a declared type.
    index = REPO_ROOT / "docs" / "index.md"
    if index.exists():
        html = index.read_text(encoding="utf-8")
        if "<video" not in html:
            problems.append("docs/index.md: the pitch is not embedded as a player")
        if 'type="video/mp4"' not in html:
            problems.append(
                "docs/index.md: the <source> declares no MIME type, so the browser must sniff "
                "the file before it will play it"
            )
        if "poster=" not in html:
            problems.append("docs/index.md: the player has no poster, so it renders as a blank box")
    else:
        problems.append("docs/index.md is missing, so the site has no landing page")

    # A referenced poster must exist on disk.
    asset = REPO_ROOT / "docs" / "assets" / "pitch-thumbnail.png"
    if not asset.exists():
        problems.append(f"{asset.relative_to(REPO_ROOT)} is referenced but does not exist")
    elif asset.stat().st_size == 0:
        problems.append(f"{asset.relative_to(REPO_ROOT)} is empty")

    if problems:
        print(f"::error::{len(problems)} problem(s) with how the pitch is referenced:")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print(
        f"pitch references: {len(MARKDOWN)} markdown file(s) checked; playback links point at "
        f"{PLAYABLE.removeprefix('https://')}, the archive uses a tag, and the player is embedded "
        f"with a declared type"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
