# Estamora Documentation

**Estamora** is a policy-guarded payments and milestone escrow protocol built on **Stellar (Soroban)**.

It provides trust-minimized multi-party escrow, autonomous agent spend limits, and pre-flight transaction simulation to protect merchants, buyers, and automated workflows from failures, fraud, and budget overruns.

---

<div class="grid cards" markdown>

- **Core Smart Contracts**

    ---

    Explore the Rust Soroban smart contract architecture, milestone releases, timeout refunds, and dispute mediation.

    [Smart Contracts Reference :material-arrow-right:](reference/contracts.md)

- **TypeScript SDK**

    ---

    Integrate `@estamora/sdk`, pre-flight simulation, and error decoding into your web application or backend service.

    [SDK Reference :material-arrow-right:](reference/sdk.md)

- **Merchant & Buyer DApp**

    ---

    Use the interactive web console deployed live at [estamora-app.vercel.app](https://estamora-app.vercel.app) to manage escrows and spend caps.

    [Application Console :material-arrow-right:](reference/app.md)

- **Protocol Architecture**

    ---

    Understand the 3-tier system design, state invariants, and delegated spend cap security models.

    [The 3-Tier Architecture :material-arrow-right:](concepts/the-layers.md)

</div>

---

## The Problems Estamora Solves

1. **Unprotected Commerce & High-Risk Agreements**  
   Traditional transfers on Stellar finalize irreversibly in 3–5 seconds. If a merchant fails to fulfill goods or services, the buyer has zero on-chain recourse. Estamora provides progressive milestone release, automated timeout refunds, and mediator arbitration.

2. **Unbounded Agent Spends & Rogue Workflows**  
   Autonomous AI agents and automated services need delegated allowances, but granting full private key access risks catastrophic fund loss. Estamora introduces on-chain 24-hour rolling spend caps and per-call limits.

3. **Silent Failures & Blind Submissions**  
   Transactions submitted with insufficient allowances, expired timeouts, or invalid state waste fees and fail silently. The `@estamora/sdk` engine simulates every call before wallet signing, scoring risk and explaining exact contract error codes.

---

## Ecosystem Repositories

| Repository | Role | Technology |
| :--- | :--- | :--- |
| [`estamora-contracts`](https://github.com/Estamora-Soroban-Layers/estamora-contracts) | Smart contract engine | Rust, Soroban SDK v22.0.8, WebAssembly |
| [`estamora-sdk`](https://github.com/Estamora-Soroban-Layers/estamora-sdk) | Client SDK & Pre-flight engine | TypeScript, `@stellar/stellar-sdk` |
| [`estamora-app`](https://github.com/Estamora-Soroban-Layers/estamora-app) | Merchant & Buyer Web Console | React 19, Vite, Freighter Wallet |
| [`estamora-docs`](https://github.com/Estamora-Soroban-Layers/estamora-docs) | Protocol Documentation | MkDocs Material |
