# Error classes

Every failure `estamora` can report has two independent properties: a **class**, which says
what went wrong, and a **blame**, which says who is answerable for it. The registry is closed:
a new failure mode is a new variant, reviewed alongside the report it will appear in, rather
than a free-form string that each call site invents.

Blame is *derived* from the class rather than passed in at the call site, because a call site
that can choose the blame is a call site that can blame the wrong party.

## The ten classes

| Class | What it means | Blame | Exit |
| --- | --- | --- | --- |
| `PROFILE_ERROR` | A profile bundle is malformed, self-inconsistent, or names something that does not exist. The requirements were never usable, so **no verdict about any contract was reached**. | Specification | `3` |
| `VECTOR_ERROR` | A vector is malformed, or disagrees with the profile it is declared against. As with a profile, no verdict was reached. | Specification | `3` |
| `CONTRACT_RESOLUTION_ERROR` | The target contract could not be resolved: an unknown network, an identifier that does not exist there, or a fixture that could not be built. | Environment | `4` |
| `NETWORK_ERROR` | A refused connection, a timeout, or a node that returned an error rather than a result. | Environment | `4` |
| `EXECUTION_ERROR` | The environment reached the contract but could not produce an observation the runner could evaluate. | Environment | `4` |
| `ASSERTION_FAILURE` | The contract ran, was observed, and violated a requirement. **The only class that describes the contract.** | Contract | — |
| `REPORT_ERROR` | A result could not be rendered: bad configuration, an unwritable path, or a serialization failure. | Runner | `5` |
| `CERTIFICATION_ERROR` | A receipt could not be produced or verified. | Runner | `5` |
| `USAGE_ERROR` | The command line was wrong: an unknown flag, a missing argument, a combination that cannot be satisfied. | Invocation | `64` |
| `INTERNAL_ERROR` | The runner failed in a way that indicates a defect in the runner itself. Reported rather than panicking, so a CI job gets a usable message and a stable exit code. | Runner | `5` |

## The four blames

| Blame | Meaning |
| --- | --- |
| `contract` | The contract's behaviour. **The only blame that supports a non-conformant verdict.** |
| `specification` | The profile or vector corpus supplied for the run. |
| `environment` | The network, the RPC endpoint, the toolchain or the fixture build. |
| `runner` | Estamora itself. |
| `invocation` | The command that was run. |

## `ASSERTION_FAILURE` is special

It is the only class whose blame is the contract, and it is the **only** way a `1` is
produced. Note that it has no exit code of its own in the table above: by the time a run
finishes, every assertion failure has been reduced to a per-vector result and folded into the
run's status. An `ASSERTION_FAILURE` that reaches the process boundary *unreduced* is a
runner defect, and exits `5` rather than blaming the contract.

This is why [Exit codes](exit-codes.md) and this page describe the same taxonomy from two
directions: the exit code is a total function of the class, and the class is what makes
"the contract is at fault" a claim the tool has to earn.

## Where a class appears

- In the **report**: the run's `status` is one of the six conformance statuses, and each
  vector's `status` is `passed`, `failed`, `error` or `skipped`. Vector-level `diagnostics[]`
  entries carry a short machine-readable `code` and a `message` — for example
  `seeding-unavailable`, which is what a vector reports when it needs seeded state a read-only
  measurement of a deployed contract cannot arrange.
- On **standard error**: one line, as `CLASS: message`. Diagnostics never go to standard
  output, because a machine-readable document on standard output is how a pipeline consumes a
  run and a log line printed beside it is how that pipeline breaks in a way nobody notices
  until the day it matters.

## The specification's own exit codes

The specification repository's validation tooling uses a deliberately smaller scale, and it is
a tested contract rather than a convention:

| Exit code | Meaning |
| --- | --- |
| `0` | Every checked artifact is valid |
| `1` | At least one defect was found |
| `2` | The tooling itself failed, or the command line was wrong |

`2` **never** means "a contract is non-conformant". CI and the runner depend on that
distinction, which is why the specification tests it.
