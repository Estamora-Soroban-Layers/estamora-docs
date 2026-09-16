# Installation

Estamora is one binary, `estamora`, plus a checkout of the specification it measures
against.

## It needs a specification checkout

This is the part that surprises people, so it comes first. **A profile is not compiled into
the binary.** `--profile sep-41@1.0` resolves inside a checkout of
[`estamora-conformance-spec`](https://github.com/Estamora-Soroban-Layers/estamora-conformance-spec),
because *which revision of which profile a verdict was produced against* is part of what the
verdict means. A bundled copy would let the requirements and the measurement drift apart
silently, and the drift would be invisible in the report.

```bash
git clone https://github.com/Estamora-Soroban-Layers/estamora-conformance-spec
```

The checkout is found in this order:

1. `--spec <PATH>`, the global flag;
2. `ESTAMORA_SPEC_REPO`;
3. the sibling directory `../estamora-conformance-spec`.

A binary installed from a release archive is a sibling of nothing, so without one of the
first two it stops with a message naming the variable, the directory it tried, and the
command that clones it. It never falls back to a different checkout: measuring against
requirements you did not name would attribute a result to a document nobody read.

## Three routes to the binary

Pick by what you need to be able to say afterwards about which revision produced a verdict.

=== "A released binary"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/Estamora-Soroban-Layers/estamora-conformance-runner/v0.1.3/scripts/install-binary.sh | sh
    ```

    The script detects the platform, downloads the matching archive from the release,
    checks it against the release's `SHA256SUMS`, and installs to `~/.cargo/bin` or
    `~/.local/bin`.

    It **refuses to install anything it cannot verify.** No checksum file, no entry for the
    archive, or a mismatch all stop the install rather than printing a warning and
    continuing. That is not ceremony: an installer that fetches a binary and runs it
    unchecked is trusting the network, a DNS answer and a TLS certificate for the integrity
    of the tool whose whole job is to be trustworthy about somebody else's contract.

    | Platform | Archive |
    | --- | --- |
    | Linux, x86-64 | `estamora-x86_64-unknown-linux-gnu.tar.gz` |
    | Linux, arm64 | `estamora-aarch64-unknown-linux-gnu.tar.gz` |
    | macOS, Apple silicon | `estamora-aarch64-apple-darwin.tar.gz` |
    | Windows, x86-64 | `estamora-x86_64-pc-windows-msvc.tar.gz` |

    `--version v0.1.3` pins a release instead of taking the latest, `--target` overrides the
    detected platform, and `--dir` chooses where it lands.

=== "From a tagged revision"

    ```bash
    cargo install --locked --git https://github.com/Estamora-Soroban-Layers/estamora-conformance-runner \
      --tag v0.1.3 estamora-cli
    ```

    Compiles from source, so it needs a Rust toolchain and several minutes, and in exchange
    the binary is built from a revision you can read.

    !!! note "It does not use the pinned toolchain"

        `cargo install` compiles the checkout in a temporary directory, and rustup selects a
        toolchain from the working directory rather than from the source tree. The released
        binaries are built with the pinned toolchain, and are the ones whose identity matches
        what a report records.

=== "From a checkout"

    ```bash
    ./scripts/install.sh
    ```

    Installs the working tree you are standing in. This is what a contributor wants, and the
    wrong answer for anybody who has to ask which revision produced a verdict.

## It is not on crates.io

`cargo install estamora-cli` is not a fourth route, and it is not one to wait for.

The seven library crates are publishable; `estamora-cli` is not one of them and will not
become one. It links `estamora-fixture-token`, the contract that `--contract fixture:<name>`
deploys so the runner can exercise its own execution path without a deployed contract, and
that fixture is deliberately `publish = false`. Packaging rewrites a path dependency into a
registry requirement of the same version, so the requirement the command would carry names a
version no registry will hold.

Publication is a human command against a token rather than a workflow step, because a
version on crates.io cannot be withdrawn. Until that command is run, a released binary or a
checkout is how `estamora` is obtained.

## Building from source

The toolchain is pinned in `rust-toolchain.toml` and is part of the runner's identity: a
result is only meaningful if the tooling that produced it is identified. The minimum
supported Rust version is **1.98**, on the 2024 edition.

```bash
git clone https://github.com/Estamora-Soroban-Layers/estamora-conformance-runner
cd estamora-conformance-runner

cargo build --workspace
cargo test --workspace
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
```

Building a contract fixture additionally needs the `wasm32v1-none` target:

```bash
rustup target add wasm32v1-none
```

## Verify the install

```bash
estamora --version
estamora --help
```

Six commands, each answering a different question:

| Command | Question |
| --- | --- |
| `run` | Does this contract behave as this profile requires? |
| `inspect` | What does this contract expose? |
| `profile` | What does this profile require? |
| `validate` | Are these requirements usable at all? |
| `report` | Render a result someone can read. |
| `certify` | Commit to a result, and check a commitment. |

Next: [Your first measurement](first-measurement.md).
