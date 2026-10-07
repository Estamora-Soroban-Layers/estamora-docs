# Protocol Security & Invariants

Estamora is designed with safety-critical guarantees for both human payers and autonomous delegated agents.

---

## Smart Contract Invariants

1. **Conservation of Balance**:  
   The contract never holds orphaned funds. Sum of released milestones + remaining balance + refunded amounts strictly equals total principal deposited at creation.

2. **Authorization Boundaries**:  
   - Only the designated payer or neutral mediator can authorize a milestone release.
   - Payer refunds are strictly locked until `current_ledger > timeout_ledger`.
   - When in active dispute, direct payouts and refunds are locked until the mediator submits `resolve_dispute`.

3. **Time-Bound Rolling Windows**:  
   Delegated agent spend caps reset on a strict 24-hour rolling ledger time window. Any payment exceeding either the single-transaction cap or the rolling daily quota is rejected at the host layer before any transfer occurs.

---

## Client Simulation Safety

The `@estamora/sdk` simulation engine performs local and RPC pre-flight dry runs:
- Eliminates transaction reverts due to expired timeouts or zero amounts.
- Validates Freighter account balances and stroop conversions before prompting wallet signing.
