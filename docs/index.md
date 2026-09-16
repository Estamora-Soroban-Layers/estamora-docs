# Estamora documentation

**This is the reader's documentation for Estamora: what it is for, how to run it against a
contract, and how to tell what a verdict means.** Start at
[Installation](getting-started/installation.md), then
[Your first measurement](getting-started/first-measurement.md).

<a href="https://github.com/Estamora-Soroban-Layers/estamora-docs/releases/download/pitch-v1/estamora-pitch.mp4">
  <img src="assets/pitch-thumbnail.png" alt="Watch the five-minute Estamora product pitch" width="100%">
</a>

**▶ [Watch the five-minute product pitch](https://github.com/Estamora-Soroban-Layers/estamora-docs/releases/download/pitch-v1/estamora-pitch.mp4)**
— every frame of it is a live deployment or real program output, and the pipeline that made it
is in [`video/`](https://github.com/Estamora-Soroban-Layers/estamora-docs/tree/main/video).

<div class="grid cards" markdown>

- **Get running**

    ---

    Install the runner, point it at a specification checkout, and measure a contract.

    [Installation :material-arrow-right:](getting-started/installation.md)

- **Put it in a pipeline**

    ---

    Use the exit-code contract and the JUnit rendering as a gate, without turning a
    network outage into a failed release.

    [CI integration :material-arrow-right:](runner/ci-integration.md)

- **Understand a verdict**

    ---

    What `CONFORMANT`, `NON_CONFORMANT`, `INCONCLUSIVE`, `PROFILE_ERROR` and
    `EXECUTION_ERROR` each commit you to.

    [Exit codes :material-arrow-right:](reference/exit-codes.md)

- **Read the standard**

    ---

    The normative specification: profiles, schemas and vectors, where every schema
    `$id` resolves.

    [Specification :material-arrow-right:](https://estamora-soroban-layers.github.io/estamora-conformance-spec/)

</div>

## The question Estamora answers

> Does this Soroban contract actually behave according to the standard or interface
> profile it claims to implement?

Not *does it compile*, and not *does it expose the expected methods*. Interface
compatibility is a **shape** claim. Behavioural conformance is a claim about **what
happens**: which principal must authorize which call and over which arguments, which events
must be emitted and what they must correspond to in state, what a failed call must leave
behind, and which properties must survive every call.

A contract that verifies *a* signature is present, without verifying *whose*, passes every
test that only asks whether the unauthorized call failed. It does fail — for the wrong
reason. See [The layers, and who owns what](concepts/the-layers.md).

## What is where

| Repository | Role |
| --- | --- |
| [`estamora-conformance-spec`](https://github.com/Estamora-Soroban-Layers/estamora-conformance-spec) | **Defines** conformance. The normative layer. |
| [`estamora-conformance-runner`](https://github.com/Estamora-Soroban-Layers/estamora-conformance-runner) | **Measures** conformance. The `estamora` binary. |
| [`estamora-docs`](https://github.com/Estamora-Soroban-Layers/estamora-docs) | **Explains** it. This site. |
| [`estamora-app`](https://github.com/Estamora-Soroban-Layers/estamora-app) | **Shows** it. The web application. |

## Conformance is not security

A `CONFORMANT` verdict means the contract behaved as a **named profile version** requires
over a **named corpus** of vectors. Profiles are written by people; a profile that does not
state a failure mode does not detect it.

Estamora does not replace formal verification, a security audit, penetration testing or
economic analysis, and a conformant contract can still be exploitable. Read the
[specification's security page](spec/security.md) and the
[runner's](runner/security.md) before quoting a verdict to anyone.
