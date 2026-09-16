# Security Policy

## Reporting a vulnerability

Use GitHub's **private vulnerability reporting**:
<https://github.com/Estamora-Soroban-Layers/estamora-docs/security/advisories/new>

If you cannot use that form, email <danielwinningtalkerloba@gmail.com> with `[SECURITY]` in
the subject. The address on the
[organization profile](https://github.com/Estamora-Soroban-Layers) is the same one, and is
the authority if this file and it ever disagree.

**Do not open a public issue for a vulnerability.**

Please include the page or file, what the impact is, and the smallest reproduction you can
produce.

## What is in scope here

This repository builds and serves a documentation site. The in-scope classes are narrow, and
saying so is more useful than a broad policy nobody can act on:

- **Script injection through rendered content.** A path by which content from one of the
  assembled source repositories, or from a URL a page links to, can execute in a reader's
  browser on `estamora-docs.vercel.app`.
- **A leaked credential.** The deployment uses a Vercel token held as a GitHub Actions secret
  and the project IDs `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID`. Anything that exposes one of
  those, or that lets an unreviewed contribution obtain one.
- **A dependency in the documentation toolchain** with a known vulnerability that this build
  exposes.
- **Substitution of what is published.** Anything that lets content reach
  `estamora-docs.vercel.app` without passing through the `deploy-vercel.yml` workflow and its
  CI-built artefact.

## A documentation error is not a vulnerability here

If a page misstates a requirement, report it as an ordinary issue. If the misstatement is in
a pinned document, the report belongs in the repository that owns it — the **edit** link on
the page names it.

If a **normative** document is wrong — a profile contradicting another requirement, or a schema
that does not constrain what the documentation says it does — that is a security-relevant
defect in `estamora-conformance-spec`, and it is in scope *there*. A conformance claim that
misleads is worse than a page that reads badly.

## Estamora's conformance limits apply to anything quoted from this site

A `CONFORMANT` verdict means a contract behaved as a **named profile version** requires over a
**named corpus**. It is not an audit, and it is not evidence that a contract is safe. Profiles
are written by people, and a profile that does not state a failure mode does not detect it.

Nothing on this site replaces formal verification, a security audit, penetration testing or
economic analysis. If a page here is read as claiming otherwise, that is a documentation
defect worth reporting.

## Supported versions

The published site reflects the pinned revisions recorded in `.github/workflows/ci.yml`.
Security fixes are applied to `main` and deployed. Older deployed artefacts are not kept
addressable, which is deliberate: a stale rendering of the documentation is a misleading one.

## Response targets

| Stage | Target |
| --- | --- |
| Acknowledgement | 3 working days |
| Initial assessment | 10 working days |
| Fix, or a written explanation | 90 days from acknowledgement |

We will credit you unless you ask us not to.
