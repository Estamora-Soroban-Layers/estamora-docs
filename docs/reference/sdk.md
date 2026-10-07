# TypeScript SDK Reference

The `@estamora/sdk` package provides complete TypeScript abstractions for interacting with Estamora smart contracts.

- **Package**: `@estamora/sdk`
- **Repository**: [`estamora-sdk`](https://github.com/Estamora-Soroban-Layers/estamora-sdk)

---

## Installation

```bash
npm install @estamora/sdk @stellar/stellar-sdk
```

---

## Classes & Methods

### `EstamoraClient`

#### `new EstamoraClient(config?: Partial<EstamoraClientConfig>)`
Creates a client instance. If config is omitted, defaults to Stellar Testnet and contract `CADQOBYHA4DQOBYHA4DQOBYHA4DQOBYHA4DQP5KR`.

#### `simulateCreateEscrow(params: CreateEscrowParams): Promise<PreflightSimulation>`
Simulates the creation of an escrow off-chain. Validates:
- Positive amounts and milestone breakdowns.
- Expiration timestamps in the future.
- Valid Stellar public keys (RFC 4648 base32 / StrKey format).
- Estimated gas and CPU instructions.

#### `simulateDelegatedPayment(params: DelegatedPaymentParams): Promise<PreflightSimulation>`
Simulates a delegated payment against the agent's rolling 24-hour spend allowance.

---

## Error Decoding

The SDK decodes raw Soroban contract errors into typed error classes:

```typescript
import { decodeContractError, ContractErrorCode } from '@estamora/sdk';

try {
  // transaction call
} catch (err) {
  const decoded = decodeContractError(err);
  console.error(`Error Code: ${decoded.code} - ${decoded.message}`);
}
```

### Supported Contract Error Codes:
1. `INVALID_AMOUNT` (Code 1) - Amount must be positive.
2. `INVALID_TIMEOUT` (Code 2) - Timeout ledger must be in the future.
3. `UNAUTHORIZED` (Code 3) - Caller failed cryptographic authorization.
4. `ESCROW_NOT_FOUND` (Code 4) - Escrow ID does not exist.
5. `ESCROW_EXPIRED` (Code 5) - Timeout ledger has already passed.
6. `ESCROW_NOT_EXPIRED` (Code 6) - Cannot refund before timeout ledger.
7. `ESCROW_ALREADY_SETTLED` (Code 7) - All milestones have been released.
8. `ESCROW_IN_DISPUTE` (Code 8) - Action blocked while dispute is pending.
9. `ESCROW_NOT_IN_DISPUTE` (Code 9) - Dispute resolution called on active escrow.
10. `INVALID_PAYOUT_SUM` (Code 10) - Payer + merchant payout sum does not match balance.
11. `EXCEEDS_PER_TX_CAP` (Code 11) - Delegated amount exceeds single transaction limit.
12. `EXCEEDS_DAILY_CAP` (Code 12) - Cumulative 24h spend exceeds daily cap.
13. `INVALID_MILESTONE_INDEX` (Code 13) - Milestone index out of range.
14. `MILESTONE_ALREADY_RELEASED` (Code 14) - Milestone has already been paid out.
