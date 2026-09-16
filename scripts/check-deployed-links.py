#!/usr/bin/env python3
"""Check that the deployed site actually serves everything its own pages reference.

Run after a deployment, with the built site on disk:

    python3 scripts/check-deployed-links.py --site site

# Why this runs after the deploy, and why it reads the HTML

Every other link check in this project looks *outward*: the specification site, GitHub, the
shields.io badges. Those are other people's hosts, and a job that cannot see the deployment can
check them any time.

A URL on this site's own host is different. It names an artefact this repository publishes, so
checking it before the deployment exists checks it against whatever was live a moment ago.
That is not hypothetical: the first version of this check ran in CI, found the pitch video's URL
in the README before the deployment carrying the video had published, and reported a 404 for a
file that was served correctly seconds later. The fix is not a retry in CI. It is to check these
URLs here, where the thing they name exists.

# Why the relative references and not a list of URLs

A list of URLs decays into a list of URLs that were correct when it was written, and the failure
that matters most is the one nobody would think to list: a page whose player, poster or stylesheet
resolves to a path that does not exist. MkDocs validates *internal page links* at build time, and
`strict: true` fails the build on a broken one -- but a relative reference in raw HTML, which is
how the landing page embeds its video, is not a Markdown link and is not validated.

So this resolves what a browser would resolve. It takes every relative `src` and `href` in every
built page, resolves it against that page's own deployed URL, and asserts the result is served.
The URL list is derived, so it cannot go stale, and it cannot be empty without this check failing.

# What it does not do

It does not check whether a page looks right, and it does not follow JavaScript: a URL that only
exists after a script runs is invisible here. It answers one question -- would a browser's
request for every relative thing this page names be answered?
"""

from __future__ import annotations

import argparse
import html
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

# The attribute syntax a browser's parser accepts for an embedded reference.
REFERENCE = re.compile(r"""(?:src|href)\s*=\s*["']([^"']+)["']""")

# Schemes and fragment-only references that are not requests to this host.
NOT_A_REFERENCE = ("http://", "https://", "//", "#", "mailto:", "data:", "javascript:", "tel:")

# The markdown this repository owns, scanned for absolute self-references. The assembled
# documents are not scanned: their links are rewritten to the repositories that own them, which
# are checked by the CI link job.
CURATED_MARKDOWN = ("README.md", "CONTRIBUTING.md", "SECURITY.md", "docs", "video")

TIMEOUT = 60
AGENT = "estamora-deploy-check (+https://github.com/Estamora-Soroban-Layers/estamora-docs)"


def references(site: pathlib.Path, base: str) -> dict[str, str]:
    """Every URL this site references on its own host, mapped to where it is referenced."""
    found: dict[str, str] = {}

    def add(url: str, where: str) -> None:
        url, _ = urllib.parse.urldefrag(url)
        if url and url not in found:
            found[url] = where

    # Relative references in the built pages, resolved the way a browser resolves them.
    for page in sorted(site.rglob("*.html")):
        relative = page.relative_to(site).as_posix()
        page_url = f"{base}/{relative}"
        for value in REFERENCE.findall(page.read_text(encoding="utf-8")):
            value = html.unescape(value).strip()
            if not value or value.startswith(NOT_A_REFERENCE):
                continue
            add(urllib.parse.urljoin(page_url, value), relative)

    # Absolute self-references in this repository's own markdown, which the pages above are
    # rendered from but which are not themselves published.
    root = site.resolve().parent
    for entry in CURATED_MARKDOWN:
        path = root / entry
        for document in [path] if path.is_file() else sorted(path.rglob("*.md")):
            for value in re.findall(r"https?://[^\s)\"'<>`]+", document.read_text(encoding="utf-8")):
                value = value.rstrip(".,;:!?")
                if value.startswith(base):
                    add(value, str(document.relative_to(root)))

    return found


def served(url: str) -> tuple[bool, str]:
    """Return (ok, detail). Follows redirects: a directory without its trailing slash is not a 404."""
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status == 200, str(response.status)
    except urllib.error.HTTPError as problem:
        return False, str(problem.code)
    except Exception as problem:  # noqa: BLE001 - a transport failure is a failure here
        return False, type(problem).__name__


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default="site", help="the built site directory")
    parser.add_argument("--base", default="https://estamora-docs.vercel.app")
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()

    site = pathlib.Path(arguments.site)
    if not site.is_dir():
        print(f"::error::{site} is not a directory; run this after building the site")
        return 1

    base = arguments.base.rstrip("/")
    targets = references(site, base)

    # A derived URL list can be derived wrongly. An empty one means this check is broken, not
    # that the site is perfect, so it is a failure rather than a vacuous pass.
    if len(targets) < 5:
        print(f"::error::only {len(targets)} self-referential URL(s) were derived; the derivation is broken")
        return 1

    broken: dict[str, str] = {}
    for url in sorted(targets):
        ok, detail = served(url)
        marker = "ok   " if ok else "FAIL "
        print(f"{marker} {detail:>4}  {url}  ({targets[url]})")
        if not ok:
            broken[url] = detail

    print(f"\ndeployed-link-check: {len(targets)} URL(s), {len(broken)} not served")
    if broken:
        for url, detail in sorted(broken.items()):
            print(f"::error file={targets[url]}::the deployed site returned {detail} for {url}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
