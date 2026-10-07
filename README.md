# Estamora Documentation Hub

[![Live Docs](https://img.shields.io/badge/Vercel-Live_Documentation-4ade80.svg)](https://estamora-docs.vercel.app)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Guides, smart contract architecture, SDK references, and testnet verification for the Estamora Payment Protocol on Stellar.**

**Live Documentation**: **[https://estamora-docs.vercel.app](https://estamora-docs.vercel.app)**  
**Live DApp**: **[https://estamora-app.vercel.app](https://estamora-app.vercel.app)**

---

## The Estamora Protocol Stack

| Component | Repository | Role | Technology |
| :--- | :--- | :--- | :--- |
| **Smart Contracts** | [**`estamora-contracts`**](https://github.com/Estamora-Soroban-Layers/estamora-contracts) | Milestone escrow, timeout auto-refunds, and delegated spend caps | Rust, Soroban SDK v27.0.6 |
| **Client SDK** | [**`estamora-sdk`**](https://github.com/Estamora-Soroban-Layers/estamora-sdk) | Zero-broadcast pre-flight simulation, error decoding, and TypeScript client | TypeScript, `@stellar/stellar-sdk` |
| **DApp Console** | [**`estamora-app`**](https://github.com/Estamora-Soroban-Layers/estamora-app) | Merchant dashboard, interactive checkout demo, and Freighter wallet operator console | React 19, Vite, `@stellar/freighter-api` |
| **Documentation** | [**`estamora-docs`**](https://github.com/Estamora-Soroban-Layers/estamora-docs) | Guides, API reference, and specification hub (this repository) | Documentation & Architecture |

---

## Key Protocols & Primitives

1. **Milestone Escrow**: Dual-party programmable custody where buyer funds remain locked in the contract until the seller satisfies deliverables, with an automated fallback refund if the timeout expires.
2. **Autonomous Agent Spend Caps**: On-chain guardrails allowing secondary accounts (AI agents, microservices) to spend funds up to a strict per-transaction and rolling 24-hour ceiling.
3. **Pre-Flight Simulation Engine**: Zero-gas evaluation querying Soroban Testnet RPC to calculate exact CPU instructions and stroop resource fees prior to wallet signing.

---

## Community & Drips Wave Sprints

- 💬 **Telegram**: [Estamora Community](https://t.me/estamora_stellar)
- 👾 **Discord**: [Estamora Developers](https://discord.gg/estamora-dev)
- 👤 **Maintainer**: [@winningtalker-commits](https://github.com/winningtalker-commits)

---

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
