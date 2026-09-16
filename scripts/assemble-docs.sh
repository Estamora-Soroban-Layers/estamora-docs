#!/usr/bin/env bash
#
# Assemble the documentation site's `docs_dir`.
#
#   ./scripts/assemble-docs.sh build/docs          # assemble
#   ESTAMORA_DOCS_DIR=build/docs mkdocs build      # then render
#
# Or simply `./scripts/build-site.sh`, which does both.
#
# # Why this exists rather than a copy of the documents in this repository
#
# The runner already ships ten documents and the specification ships nineteen. Copying them
# here would create a second copy of every one of them, and two copies of a document that
# describe the same behaviour will diverge. Divergence is the specific defect the
# specification repository already spends a validation job preventing between its *own*
# profiles and schemas; introducing it between a document and its published rendering would be
# a regression in a project whose whole claim is that it is careful about drift.
#
# So nothing is copied into this repository. The site is assembled at build time from the
# exact revisions named below, which makes a page in the published site traceable to a commit
# in the repository that owns it. A weekly canary reports when a newer tag exists, so drift
# is discovered deliberately rather than as a surprise.
#
# # What is curated here, and what is not
#
# Seven pages are written in this repository: the landing page, getting started, the layer
# map, and three reference pages (exit codes, error classes, report format) that no repository
# currently publishes as a document. Everything else is assembled.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

OUT="${1:-build/docs}"

# The revisions the published site is assembled from. Pinned, and pinned to tags rather
# than branches, for the same reason the runner's CI pins the specification: a doc that can
# change under a published URL without a commit here is a doc nobody can cite.
RUNNER_TAG="${ESTAMORA_RUNNER_TAG:-v0.1.3}"
SPEC_TAG="${ESTAMORA_SPEC_TAG:-v0.1.1}"

RUNNER_REPO="https://github.com/Estamora-Soroban-Layers/estamora-conformance-runner"
SPEC_REPO="https://github.com/Estamora-Soroban-Layers/estamora-conformance-spec"
SPEC_SITE="https://estamora-soroban-layers.github.io/estamora-conformance-spec"

say() { printf '%s\n' "$*" >&2; }
die() { say "assemble-docs: $*"; exit 1; }

# A checkout is used when one was named or found beside this repository, and cloned at the
# pinned tag otherwise. A contributor developing two repositories side by side gets their
# working tree; CI gets the pin.
locate() {
    local name="$1" env="$2" tag="$3" url="$4"
    local named="${!env:-}"

    if [ -n "$named" ]; then
        [ -d "$named" ] || die "$env names $named and it is not a directory"
        printf '%s' "$named"
        return
    fi

    if [ -d "$ROOT/../$name/.git" ]; then
        printf '%s' "$ROOT/../$name"
        return
    fi

    local vendor="$ROOT/.vendor/$name"
    if [ ! -d "$vendor/.git" ]; then
        say "assemble-docs: cloning $name at $tag"
        mkdir -p "$ROOT/.vendor"
        git clone --quiet --depth 1 --branch "$tag" "$url" "$vendor" \
            || die "$name could not be cloned at $tag"
    fi
    printf '%s' "$vendor"
}

# A document in `docs/` links to files at its repository root as `../NAME.md` and to the
# normative trees as `../schema/...`. Those links are correct in a checkout and on GitHub.
# They cannot resolve in a site that renders only the documents, so each one is rewritten to
# the absolute URL that *does* serve it -- the specification site for the specification's
# normative trees, and the pinned revision on GitHub for the runner's files. Rewriting rather
# than dropping the links keeps `strict: true` link validation meaningful: with the links
# broken on purpose, MkDocs would have to be told to ignore broken links, and it would then
# also ignore a genuinely broken one.
rewrite_links() {
    local file="$1" target="$2"
    python3 - "$file" "$target" <<'PY'
import re, sys
path, target = sys.argv[1], sys.argv[2]
text = open(path, encoding="utf-8").read()
# Only markdown link destinations, so a `../` inside a fenced code block is left alone.
fixed = re.sub(r"\]\(\.\./", "](" + target + "/", text)
if fixed != text:
    open(path, "w", encoding="utf-8").write(fixed)
PY
}

RUNNER_DIR="$(locate estamora-conformance-runner ESTAMORA_RUNNER_REPO "$RUNNER_TAG" "$RUNNER_REPO")"
SPEC_DIR="$(locate estamora-conformance-spec ESTAMORA_SPEC_REPO "$SPEC_TAG" "$SPEC_REPO")"

say "assemble-docs: runner documents from $RUNNER_DIR"
say "assemble-docs: specification documents from $SPEC_DIR"

# The curated pages, which are the part of the site this repository owns.
rm -rf "$OUT"
mkdir -p "$OUT"
cp -R "$ROOT/docs/." "$OUT/"

# The runner's documents, under `runner/`. Each is copied at the pinned revision, so a page
# in the site names the commit it came from.
mkdir -p "$OUT/runner"
count_runner=0
for document in "$RUNNER_DIR"/docs/*.md; do
    [ -e "$document" ] || die "the runner checkout has no docs/ directory at $RUNNER_TAG"
    name="$(basename "$document")"
    cp "$document" "$OUT/runner/$name"
    rewrite_links "$OUT/runner/$name" "$RUNNER_REPO/blob/$RUNNER_TAG"
    count_runner=$((count_runner + 1))
done

# The specification's documents, under `spec/`. Its relative links point at its own
# published site, which is where the normative trees and the root documents are served
# beside the rendered pages -- so a reader who follows one arrives at the document that
# claims the identity, not at a 404.
mkdir -p "$OUT/spec"
cp -R "$SPEC_DIR/docs/." "$OUT/spec/"
mapfile -t spec_docs < <(find "$OUT/spec" -name '*.md' -print)
for document in "${spec_docs[@]}"; do
    rewrite_links "$document" "$SPEC_SITE"
done

# Assert the assembly happened, rather than trusting each `cp` to have been correct. A site
# that builds successfully with the curated pages present and the canonical documents absent
# is the failure this script exists to prevent: it would look finished and would be a link
# list.
[ "$count_runner" -gt 0 ] || die "no runner documents were assembled"
[ "${#spec_docs[@]}" -gt 0 ] || die "no specification documents were assembled"

say "assemble-docs: $(find "$OUT" -name '*.md' | wc -l | tr -d ' ') document(s) in $OUT"
say "assemble-docs:   curated   $(find "$OUT" -maxdepth 2 -name '*.md' -not -path "$OUT/runner/*" -not -path "$OUT/spec/*" | wc -l | tr -d ' ')"
say "assemble-docs:   runner    $count_runner"
say "assemble-docs:   spec      ${#spec_docs[@]}"
