# Contributing

This repository holds the Estamora documentation site. Two rules shape almost every decision
here, and both exist because the alternative has a specific failure mode.

## Rule 1 — a document lives in the repository that owns it

The site is assembled at build time from `estamora-conformance-runner@v0.1.3` and
`estamora-conformance-spec@v0.1.1`. Nothing is copied in.

So if you want to change what the runner's troubleshooting page says, **change it in the
runner**. A change here cannot do it, and a copy here would be a second version of the same
document. Two versions of one document will disagree, and the one a reader finds will be
whichever search engine preferred.

The edit links on every page point at the repository that owns it. Follow them.

## Rule 2 — a normative statement is never restated

The profiles, the JSON Schemas and the vectors are normative. The
[specification site](https://estamora-soroban-layers.github.io/estamora-conformance-spec/) is
where they are served, and where every schema `$id` resolves.

Pages in this repository **describe and link**; they do not restate a requirement. If a page
here and a schema disagree, the schema governs and this page is the defect.

## Building and checking

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-docs.txt

./scripts/build-site.sh
```

`mkdocs.yml` sets `strict: true`, so a broken internal link or a page missing from the
navigation fails the build rather than being published. If your change adds a page, add it to
`nav` in `mkdocs.yml` — the pin fixes the page set, and the navigation is what names it.

Check the links you write before opening a pull request:

```bash
python3 scripts/check-external-links.py
```

## What a pull request should say

- **What a reader could not do before**, and can now.
- **Which repository owns the fact you changed**, if you changed a fact rather than a
  description. If a fact is wrong, this is the wrong repository for the change.
- **What you verified.** "Built the site" is verification. "Ran the link check" is
  verification. "It reads well" is not.

## Style

- Second person, present tense: "run the command", not "the user should run the command".
- Prefer the concrete over the general. A command that can be pasted beats a description of
  what the command does.
- State the limit of a thing at the point where a reader might over-trust it. Nearly every
  page here has a sentence saying what a result does *not* mean, and those sentences are the
  point rather than a disclaimer.

## Proposing a change to the pin

Moving `ESTAMORA_RUNNER_TAG` or `ESTAMORA_SPEC_TAG` is a content change, not a maintenance
chore: it changes what every reader is told. Open an issue first, say what moved and why the
site should follow, and update `mkdocs.yml`'s `nav` in the same pull request if the page set
changed.

## Conduct

[`CODE_OF_CONDUCT.md`](https://github.com/Estamora-Soroban-Layers/estamora-conformance-spec/blob/main/CODE_OF_CONDUCT.md)
applies across the organization.

## Security

See [`SECURITY.md`](SECURITY.md). Do not open a public issue for a vulnerability.
