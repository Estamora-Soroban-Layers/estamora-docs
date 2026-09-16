# Changelog

All notable changes to the Estamora documentation site are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versioning is
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## How versioning works for this site

This repository renders documents it does not own. The runner's ten engineering documents and the
specification's twenty-one are **assembled at build time from pinned tags**, and its pitch video is
fetched from a release — nothing is copied in. A version here identifies a **published rendering**
of those revisions, which makes one rule worth stating explicitly:

**A pin is part of what a published URL means.** Moving `ESTAMORA_RUNNER_TAG` changes the content
behind links that other people have already cited, without changing any URL. That is a breaking
change even when the site builds perfectly and every page is better, so the pins are listed below
per version and a move is recorded as one.

## Pinned revisions

| What | Pin | Where it comes from |
| --- | --- | --- |
| Runner documents | `v0.1.3` | `estamora-conformance-runner` → `docs/`, rendered under `/runner/` |
| Specification documents | `v0.1.1` | `estamora-conformance-spec` → `docs/`, rendered under `/spec/` |
| Pitch video | `pitch-v1` | this repository's release assets, fetched into `/assets/` |

The pins are declared once in `mkdocs.yml`'s companion scripts, repeated in the CI and deploy
workflows' `env`, and checked upstream by CI's `pins` job — a tag deleted upstream would otherwise
surface as a confusing clone failure.

## [Unreleased]

Nothing yet.

## [0.1.0] - 2026-09-16

First release: the site, the assembly pipeline and the deployment.

### Added

- **Seven curated pages**, written in this repository: the landing page, install and first
  measurement, the layer map, and the three reference pages no other repository publishes as
  documents — exit codes, error classes and report format.
- **`scripts/assemble-docs.sh`**, which assembles the `docs_dir` from the pinned revisions rather
  than copying the documents in. Two copies of a document that describes the same behaviour will
  diverge, which is the defect the specification repository already spends a validation job
  preventing between its own profiles and schemas. It also rewrites the assembled documents'
  relative links to absolute URLs, which is what allows `strict: true` to stay on: with the links
  broken on purpose, MkDocs would have to be told to ignore broken links, and it would then also
  ignore a genuine one.
- **`scripts/build-site.sh`**, the single entry point CI and a contributor both use, so the two
  cannot build different sites. It asserts the page count and the presence of the video, because
  the failure worth preventing is a site that builds cleanly while missing its content.
- **The pitch, played rather than linked.** The landing page embeds an HTML5 player whose source
  is served by this site: `video/mp4`, with `accept-ranges: bytes` and a `206` on a range request,
  which is what lets a browser start before the file has finished arriving and seek once it has.
- **`scripts/check-deployed-links.py`**, which derives the set of URLs this site must serve from
  its own built pages — every relative `src` and `href`, resolved the way a browser resolves it —
  and asserts each one is served after a deployment.
- **Vercel deployment from what CI built**, not from a rebuild. The site is assembled at pinned
  revisions and fetches its video from a release, so publishing a build nobody validated would
  publish a build nobody can cite. Vercel's build step asserts the artefact exists instead of
  producing it, and the workflow asserts the served pages, the pitch's content type and ranges,
  and every derived URL.

### Fixed

- **Every "watch the pitch" link downloaded the video instead of playing it.** A GitHub release
  asset is served as `content-type: application/octet-stream` with `content-disposition: attachment`.
  The same bytes are now served by this site as playable media, and the release asset is kept and
  named as the archival download. Every README in the organisation that linked it was repointed.
- **The CI link check raced the deploy over this site's own URLs.** Adding a link to the pitch made
  CI report a `404` for a URL the deployment published moments later: the link job cannot see the
  deployment, so it checked the site against whatever was live at that instant. The own host is now
  excluded from the CI check and reported as `own` rather than skipped silently, and those URLs are
  asserted after the deploy, where the thing they name exists.
- **The post-deploy assertion failed on two correct deployments, for two different reasons.** It
  first read the production alias before the edge had switched and saw the previous deployment's
  not-found page; it then asserted the immutable deployment URL, which turned out to be behind
  Vercel Authentication and answers an unauthenticated request with `302` to an SSO prompt carrying
  `content-type: text/plain`. The alias is the only URL a reader can reach, so the alias is what is
  asserted, with a bounded wait, and the failure message distinguishes "the edge has not switched"
  from "the response is not media" instead of blaming the video for either.

[Unreleased]: https://github.com/Estamora-Soroban-Layers/estamora-docs/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Estamora-Soroban-Layers/estamora-docs/releases/tag/v0.1.0
