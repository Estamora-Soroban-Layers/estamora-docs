# Report format

The normative report document is defined by
[`schema/report.schema.json`](https://estamora-soroban-layers.github.io/estamora-conformance-spec/schema/report.schema.json),
whose `$id` resolves on the published specification site. This page describes the shape a
reader needs to interpret one. Where this page and the schema disagree, **the schema
governs** and this page is a defect.

Every report declares the schema it claims to satisfy in `$schema`, so a consumer does not
have to be told which revision of the format it is holding.

## Top-level members

| Member | What it is |
| --- | --- |
| `$schema` | The URL of the report schema this document claims to satisfy. |
| `estamora_spec_version` | The specification format version the report is written in. |
| `runner` | `{ name, version }` — **which tool** produced the verdict. Part of the report's identity, not decoration. |
| `generated_at` | An RFC 3339 UTC instant. |
| `target` | `{ contract, network, wasm_hash, metadata }` — what was measured. |
| `profile` | `{ id, version, digest }` — the requirements it was measured against. |
| `vectors` | `{ digest, count }` — the corpus that was executed. |
| `configuration` | `{ contract, network, profile_root, seeding, tags, vectors_root }` — how the run was configured. |
| `results` | One entry per vector. |
| `summary` | Per-dimension tallies. |
| `status` | One of the six conformance statuses. |
| `exit_code` | The integer the process exited with. |

## Why the digests are in the report

`profile.digest` and `vectors.digest` are the reason a verdict is reproducible rather than
merely repeatable.

A report that named only `sep-41@1.0` would be incomplete: a later revision of that profile
can require something the earlier one did not, and the same contract could then produce a
different verdict under the same name. The digest pins **the exact bytes of the requirements
that were read**, so a reviewer can fetch the same revision and check that the same verdict
follows.

Both digests are computed over canonical JSON, so they are identical on any machine
regardless of where the checkout lives, what it is called, or which operating system read it.
That property is tested, and it is not free: an earlier implementation folded the absolute
path of each vector into the corpus digest, which made a published digest reproducible only by
reproducing the operator's filesystem layout.

## `target.wasm_hash`

For a deployed contract, `target.wasm_hash` is the hash declared by the contract's instance
ledger entry, and the runner verifies the fetched artifact against it. A report that records a
hash the deployment does not declare would be evidence of nothing.

## Per-vector results

Each entry in `results` has five members:

| Member | Meaning |
| --- | --- |
| `vector_id` | The identity of the vector, which is the requirement it exercises. |
| `category` | Its category — `boundary`, and so on. |
| `status` | `passed`, `failed`, `error` or `skipped`. |
| `assertions` | Every assertion that was evaluated, with its outcome and category. |
| `diagnostics` | A list of `{ code, message }` — why a vector could not be decided, when it could not. |

A **skipped** vector is not a silent omission. It is reported with a diagnostic that names the
reason, and it contributes nothing to the verdict. The distinction between *"this held"* and
*"this was not exercised"* is the difference between a verdict and an assumption.

## The seven dimensions

`summary` is keyed by dimension, each with `{ passed, failed, total }`:

```text
interface, authorization, events, behavior, state, invariants, failure
```

The worked example in the runner repository reports **49 + 4 + 6 + 2 + 1 + 1 + 0 = 63 checks,
0 failed** — and is still `INCONCLUSIVE`, because `failure` records `0/0`. A dimension with no
checks is a dimension the corpus did not exercise, and the report shows that as a zero rather
than omitting the key.

!!! note "Dimension naming"

    The assertion vocabulary in the schema enumerates the same dimensions in the singular
    (`event`, `invariant`) while `summary` is keyed in the plural (`events`, `invariants`).
    Both appear in a report; when consuming one, read the keys as they are written rather
    than normalising them.

## The six conformance statuses

| Status | Exit | Meaning |
| --- | --- | --- |
| `CONFORMANT` | `0` | Every required vector that was executed passed. |
| `PARTIALLY_CONFORMANT` | `1` | Some requirement held and some did not. |
| `NON_CONFORMANT` | `1` | A required vector failed. |
| `INCONCLUSIVE` | `2` | Part of the corpus could not be decided. |
| `EXECUTION_ERROR` | `4` | The environment failed; no verdict about the contract was reached. |
| `PROFILE_ERROR` | `3` | The requirements were unusable. |

These six are collapsed into a single boolean nowhere. In particular, `INCONCLUSIVE` is not
`CONFORMANT` with caveats, and `EXECUTION_ERROR` is not a contract defect — see
[Exit codes](exit-codes.md).

## Renderings

The JSON document is the artefact of record. Three renderings exist for readers:

| `--format` | Intended for |
| --- | --- |
| `json` | The normative document, for another tool. |
| `markdown` | A reviewer reading a pull request. |
| `junit` | An existing CI gate. |
| `text` | A terminal. |

`run` defaults to `text`; `report` defaults to `markdown`. Use `--report <PATH>` to write the
normative JSON alongside a rendering, since a pipeline usually wants both from one run.
