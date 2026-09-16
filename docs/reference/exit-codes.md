# Exit codes

A CI system reads one thing from `estamora`: the number it exits with. This page is the
contract for that number. It is implemented in `estamora-core` as an enum rather than a set
of `return` statements, it is derived from the failure's *class* rather than chosen at each
call site, and every branch is covered by a test.

| Code | Status | Meaning | Who is at fault |
| --- | --- | --- | --- |
| `0` | `CONFORMANT` | The contract satisfied every required vector | Nobody |
| `1` | `NON_CONFORMANT`, `PARTIALLY_CONFORMANT` | The contract violated a requirement | **The contract** |
| `2` | `INCONCLUSIVE` | Part of the corpus could not be decided | The run |
| `3` | `PROFILE_ERROR` | The requirements were unusable | The specification |
| `4` | `EXECUTION_ERROR` | The environment failed | The environment |
| `5` | — | The runner itself failed | The runner |
| `64` | — | The command line was wrong | The invocation |

`64` is `sysexits.h`'s usage status, so a wrapper script can recognise a command-line mistake
without knowing this program.

## The rule the table encodes

**A failure never produces `0`, `1` or `2` unless it names the contract.** That is a test, not
a convention:

```text
for every ErrorClass:
    assert exit_code(class) != 0        # nothing fails silently
    assert exit_code(class) != 1        # a failure never blames the contract
```

The second assertion is the important one. An assertion failure that somehow reached the
process boundary without first being reduced to a vector result is a **defect in the runner**,
so it exits `5`. Reporting the contract as non-conformant at that point would be a guess, and
a guess that fails somebody's release.

## Why `1` and `4` are separated

This is the single most consequential distinction in the tool.

A runner that reports an unreachable node, an unbuilt fixture or a refused connection as a
contract failure:

- blocks a release for a network outage;
- and teaches its users to distrust **every** `1` it produces, including the real ones.

So the three environment classes — `CONTRACT_RESOLUTION_ERROR`, `NETWORK_ERROR` and
`EXECUTION_ERROR` — all map to `4`, and only a violated requirement maps to `1`.

A pipeline should therefore **fail on `1`** and **retry on `4`**. See
[Conformance in CI](https://github.com/Estamora-Soroban-Layers/estamora-conformance-runner/blob/main/docs/ci-integration.md).

## `2` is not a pass

`INCONCLUSIVE` means part of the corpus could not be decided. The committed worked example is
exactly this case: **63 checks across all seven dimensions, 0 failed**, and still
`INCONCLUSIVE` rather than `CONFORMANT`, because 19 of the 20 vectors need seeded state that
a read-only measurement of a deployed contract cannot arrange.

19 vectors contributing nothing to a verdict is a real limitation, and the report says so
rather than presenting a partial run as a conformant one. Treat `2` as *"this measurement did
not settle the question"*.

## `--no-fail`

`run` and `report` accept `--no-fail`, which exits `0` whatever the verdict while still
recording it. It exists for a scheduled measurement that should publish the report of a
non-conformant contract without failing the job that produced it.

It is precisely the opt-out from a release gate. Do not use it for one.

## Mapping from an error class

Every failure the runner can report carries an `ErrorClass`, and the exit code is a total
function of that class:

| `ErrorClass` | Exit | Blame |
| --- | --- | --- |
| `PROFILE_ERROR` | `3` | The specification |
| `VECTOR_ERROR` | `3` | The specification |
| `CONTRACT_RESOLUTION_ERROR` | `4` | The environment |
| `NETWORK_ERROR` | `4` | The environment |
| `EXECUTION_ERROR` | `4` | The environment |
| `ASSERTION_FAILURE` | `5` | The runner — never the contract at this boundary |
| `REPORT_ERROR` | `5` | The runner |
| `CERTIFICATION_ERROR` | `5` | The runner |
| `INTERNAL_ERROR` | `5` | The runner |
| `USAGE_ERROR` | `64` | The invocation |

See [Error classes](error-classes.md) for what each one means and when it is raised.
