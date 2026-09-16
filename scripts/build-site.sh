#!/usr/bin/env bash
#
# Build the documentation site.
#
#   ./scripts/build-site.sh              # into ./site
#   ./scripts/build-site.sh /tmp/out     # somewhere else
#
# One entry point for CI and for a contributor, because the two must not build different
# sites. It assembles the curated pages together with the canonical document sets at their
# pinned revisions, then renders the result.
#
# `strict: true` is set in `mkdocs.yml`, so a broken internal link or a page missing from the
# navigation fails the build rather than being published. The relative links in the assembled
# documents were rewritten to absolute URLs by the assembly step, precisely so that this
# check can stay on instead of being relaxed to accommodate them.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

OUT="${1:-site}"
ASSEMBLED="build/docs"

say() { printf '%s\n' "$*" >&2; }
die() { say "build-site: $*"; exit 1; }

python3 -c "import mkdocs" 2>/dev/null \
    || die "mkdocs is not installed; run: pip install -r requirements-docs.txt"

./scripts/assemble-docs.sh "$ASSEMBLED"

# The pitch video is fetched, not committed, and it has to be beside the pages before MkDocs
# renders: MkDocs copies the non-Markdown files in `docs_dir` into the site, so fetching it
# afterwards would leave it out of the published artefact. `fetch-pitch-video.sh` explains why
# the site serves its own copy rather than linking the release asset.
./scripts/fetch-pitch-video.sh "$ASSEMBLED/assets"

say "build-site: rendering into $OUT"
ESTAMORA_DOCS_DIR="$ASSEMBLED" mkdocs build --site-dir "$OUT"

pages="$(find "$OUT" -name '*.html' | wc -l | tr -d ' ')"
# Asserted, because the failure this script exists to prevent is a site that builds
# successfully while missing its content.
[ "$pages" -gt 30 ] || die "expected more than 30 pages, found $pages"

# The video is the one asset whose absence would not fail the build: the site renders fine
# with a player pointing at nothing. Asserted here because the page is the first thing on the
# landing page, and a broken player is worse than no player.
if [ ! -s "$OUT/assets/estamora-pitch.mp4" ]; then
    die "the site has no pitch video at $OUT/assets/estamora-pitch.mp4"
fi

if [ -n "${GITHUB_SHA:-}" ]; then
    printf '%s\n' "$GITHUB_SHA" > "$OUT/REVISION"
fi

say "build-site: $pages page(s) in $OUT"
