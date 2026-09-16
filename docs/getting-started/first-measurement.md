# Your first measurement

This page runs an end-to-end measurement against a fixture that ships with the runner, so
you can see every part of a verdict before pointing it at a contract you care about.

## Measure the contract that is wrong in no way

The repository ships fixtures that are each wrong in exactly one way. The one named `none`
is wrong in no way at all: it is the conforming case.

```bash
estamora run --profile sep-41@1.0 --contract fixture:none
```

Expected: a conformant verdict, and exit code `0`.

```bash
echo "exit code: $?"
```

## Measure one that is wrong in exactly one way

```bash
estamora run --profile sep-41@1.0 --contract fixture:skips-authorization
```

`skips-authorization` never calls `require_auth` in `transfer`. One line is missing, and
four separate dimensions notice it.

```bash
echo "exit code: $?"   # 1 — the contract violated a requirement
```

That `1` is the only exit code that names the contract as at fault. Everything else — an
unreachable node, an unbuilt fixture, a malformed profile — is a different number, on
purpose. See [Exit codes](../reference/exit-codes.md).

## The fixtures, and what each one is for

| Fixture | Wrong in | Noticed by |
| --- | --- | --- |
| `none` | Nothing — the conforming case | `CONFORMANT`, exit `0` |
| `skips-authorization` | `transfer` never calls `require_auth` | the authorization plan, the refusal, the events and the state |
| `omits-event` | moves the value, publishes nothing | the event cardinality and value requirements |
| `wrong-credit-amount` | credits one unit less than it debits | the balance deltas and the conservation invariant |
| `double-emits` | two transfer events for one movement | the event cardinality requirement |
| `wrong-event-amount` | states an amount one unit larger | the event data requirement |
| `allows-overdraft` | permits a negative balance | the must-fail rule, the non-negative bound, and the state assertions |
| `missing-decimals` | the interface omits `decimals` | the interface dimension, on every vector |

Each fixture is a contract that is *plausible*. `wrong-credit-amount` is an off-by-one that
would pass a signature comparison, a balance smoke test and a happy-path transfer test. It is
the reason the suite asserts on deltas and conservation rather than on a final total.

## Get the normative document

The default rendering is for a terminal. The normative document — the report itself, as the
published schema defines it — is JSON:

```bash
estamora run --profile sep-41@1.0 --contract fixture:none \
  --format json --report report.json
```

`--report` is separate from `--out` because a human-readable rendering on a terminal and the
document another tool consumes are different artefacts, and a pipeline usually wants both
from one run:

```bash
estamora run --profile sep-41@1.0 --contract fixture:none \
  --format markdown --out verdict.md --report report.json
```

## See every check, not just the failures

By default the runner prints the checks that did **not** hold. `--verbose` prints every
check it made:

```bash
estamora run --profile sep-41@1.0 --contract fixture:none --verbose
```

This is what makes a verdict auditable rather than merely authoritative. A report that lists
only failures cannot be distinguished from a report that ran nothing.

## Ask what the profile requires, without running anything

`profile` and `validate` answer questions about the requirements rather than the contract,
and neither deploys or executes anything:

```bash
estamora profile --profile sep-41@1.0
estamora validate --profile sep-41@1.0
```

The split matters because a run that conflated them would have no way to say *the profile is
wrong* as distinct from *the contract is wrong*:

- `validate` failing means the requirements were never usable, so no verdict about any
  contract was reached — exit `3`, and the specification is at fault;
- `run` returning `NON_CONFORMANT` means the requirements were usable and the contract
  violated one — exit `1`, and the contract is at fault.

## Read a contract's interface without judging it

```bash
estamora inspect --contract fixture:none
```

`inspect` deploys and reads. It states plainly that an interface is not evidence of
behaviour: a contract can expose all ten methods of the token interface with the exact
expected signatures and still lose user funds.

## Where to go next

- [Testnet testing](../runner/testnet-testing.md) — the same run against a contract on
  testnet.
- [CI integration](../runner/ci-integration.md) — turning the exit code into a gate.
- [Report format](../reference/report-format.md) — why a digest is in the report and what it
  commits to.
- [Certification](../runner/certification.md) — committing to a result so it can be checked
  later.
