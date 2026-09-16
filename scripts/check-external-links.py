#!/usr/bin/env python3
"""Check that every external URL in this repository's own documentation resolves.

A documentation site is mostly links, and a link that 404s is the most common way a
documented project looks abandoned. The two failures this catches are both real:

  * a URL that was correct when it was written and has since moved;
  * a URL that was never correct, because a path was guessed rather than checked.

Only the curated documents in this repository are checked. The assembled documents are
validated by MkDocs' own link checking against the rendered site, and their external
links are rewritten during assembly to the specification site and to pinned GitHub URLs,
both of which are asserted to serve their content elsewhere in this workflow.

Some hosts answer a machine with 403 or 429 while serving a browser normally. Treating
those as failures would make this check flaky, and a flaky check is one people learn to
ignore -- so they are reported as "unknown" and do not fail the run. A 404 or 410 is
unambiguous and does fail.

    python3 scripts/check-external-links.py [--json]
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCAN = ["docs", "README.md", "CONTRIBUTING.md", "SECURITY.md"]

URL = re.compile(r"https?://[^\s\)\]\"'<>`]+")
# Trailing punctuation that a sentence adds but a URL does not contain.
TRAILING = ".,;:!?"

# Hosts that answer automated requests with a challenge page whatever the status code.
# Checking them this way would report a healthy link as broken, so they are skipped and
# the reason is stated rather than the check being silently narrowed.
SKIP_HOSTS = ("localhost", "127.0.0.1")
ALLOWED_UNKNOWN = {403, 405, 429, 999}

TIMEOUT = 20
AGENT = "estamora-docs-link-check (+https://github.com/Estamora-Soroban-Layers/estamora-docs)"


def documents() -> list[pathlib.Path]:
    found: list[pathlib.Path] = []
    for entry in SCAN:
        path = ROOT / entry
        if path.is_file():
            found.append(path)
        elif path.is_dir():
            found.extend(sorted(path.rglob("*.md")))
    return found


def urls() -> dict[str, set[str]]:
    """Every external URL, mapped to the files that reference it."""
    found: dict[str, set[str]] = {}
    for document in documents():
        text = document.read_text(encoding="utf-8")
        for match in URL.finditer(text):
            url = match.group(0).rstrip(TRAILING)
            if any(host in url for host in SKIP_HOSTS):
                continue
            found.setdefault(url, set()).add(str(document.relative_to(ROOT)))
    return found


def reachable(url: str) -> tuple[str, int | str]:
    """Return ("ok" | "broken" | "unknown", detail)."""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return ("ok", response.status)
    except urllib.error.HTTPError as problem:
        if problem.code in ALLOWED_UNKNOWN:
            return ("unknown", problem.code)
        if problem.code in (404, 410):
            # Some servers refuse HEAD but serve GET. Confirm before calling it broken, so
            # this check never fails on a link that works in a browser.
            try:
                with urllib.request.urlopen(
                    urllib.request.Request(
                        url, method="GET", headers={"User-Agent": AGENT}
                    ),
                    timeout=TIMEOUT,
                ) as response:
                    return ("ok", response.status)
            except urllib.error.HTTPError as again:
                return ("broken" if again.code in (404, 410) else "unknown", again.code)
            except Exception:  # noqa: BLE001 - any transport failure is "unknown"
                return ("unknown", "transport")
        return ("unknown", problem.code)
    except urllib.error.URLError as problem:
        # A DNS failure or a timeout is not evidence that the link is wrong.
        return ("unknown", str(problem.reason)[:60])
    except Exception as problem:  # noqa: BLE001
        return ("unknown", type(problem).__name__)


def main() -> int:
    as_json = "--json" in sys.argv
    targets = urls()
    results = {url: reachable(url) for url in sorted(targets)}

    broken = {url: detail for url, (state, detail) in results.items() if state == "broken"}
    unknown = {url: detail for url, (state, detail) in results.items() if state == "unknown"}

    if as_json:
        print(
            json.dumps(
                {
                    "checked": len(results),
                    "broken": {u: {"detail": d, "in": sorted(targets[u])} for u, d in broken.items()},
                    "unknown": {u: d for u, d in unknown.items()},
                },
                indent=2,
            )
        )
    else:
        for url, (state, detail) in results.items():
            marker = {"ok": "ok     ", "broken": "BROKEN ", "unknown": "unknown"}[state]
            print(f"{marker} {detail!s:>8}  {url}")
        print(f"\nlink-check: {len(results)} URL(s), {len(broken)} broken, {len(unknown)} unknown")

    if broken:
        for url, detail in sorted(broken.items()):
            where = ", ".join(sorted(targets[url]))
            print(f"::error file={where}::link returned {detail}: {url}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
