# Merchant & Buyer Console Reference

The Estamora Web Console is a live DApp allowing buyers and merchants to interact with the Stellar Soroban contracts.

- **Live URL**: [`https://estamora-app.vercel.app`](https://estamora-app.vercel.app)
- **Repository**: [`estamora-app`](https://github.com/Estamora-Soroban-Layers/estamora-app)

---

## Capabilities

### 1. Milestone Escrow Builder
- Configure merchant address, milestone breakdown, and timeout expiration window.
- View real-time pre-flight simulation before broadcasting.
- Support for multi-milestone progressive settlement.

### 2. Pre-Flight Simulation Scorecard
- Validates parameters before prompt in Freighter wallet.
- Displays CPU instruction budget, fee estimation, and parameter viability check.

### 3. Agent Spend Limit Firewall
- Configure autonomous delegated spenders.
- Enforce rolling 24-hour spend limits and single-transaction maximums.
- Inspect active allowance consumption and remaining quotas.

### 4. Dispute Resolution & Arbitration
- Escrow locking upon dispute notice.
- Mediator arbitration portal for percentage/custom payout splits between parties.
