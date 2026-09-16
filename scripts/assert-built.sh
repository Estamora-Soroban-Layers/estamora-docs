#!/usr/bin/env bash
#
# Vercel's build step for this project.
#
# The site is not built on Vercel. It is built by GitHub Actions, which has a pinned Python
# and the MkDocs toolchain, and whose output is reproducible and inspectable as a CI artefact
# before anything is published. Vercel's job is to serve what CI produced.
#
# That makes this step a check rather than a build: it asserts the site exists, so a
# misconfigured workflow fails here with a clear message instead of publishing an empty
# directory over a working deployment. Publishing nothing is worse than publishing nothing
# updated, because the site is where the documentation is read.

set -euo pipefail

if [ ! -f site/index.html ]; then
    printf '%s\n' "vercel-build: site/index.html is absent." >&2
    printf '%s\n' "vercel-build: run ./scripts/build-site.sh before deploying; the site is assembled from pinned revisions of two repositories and must not be deployed unbuilt." >&2
    exit 1
fi

pages="$(find site -name '*.html' | wc -l | tr -d ' ')"
if [ "$pages" -lt 30 ]; then
    printf '%s\n' "vercel-build: only $pages page(s) in site/; expected more than 30." >&2
    exit 1
fi

printf '%s\n' "vercel-build: $pages page(s) present; packaging the artefact GitHub Actions built."
