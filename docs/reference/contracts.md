# Smart Contracts Reference

The core Estamora contract is implemented in Rust using Soroban SDK v22.0.8.

- **Contract ID (Testnet)**: `CADQOBYHA4DQOBYHA4DQOBYHA4DQOBYHA4DQOBYHA4DQP5KR`
- **Wasm Binary Size**: 26,247 Bytes (26.2 KB)
- **Repository**: [`estamora-contracts`](https://github.com/Estamora-Soroban-Layers/estamora-contracts)

---

## Functions

### 1. `create_escrow`
Creates a new milestone escrow agreement and deposits the initial principal into contract storage.

```rust
pub fn create_escrow(
    env: Env,
    payer: Address,
    merchant: Address,
    mediator: Option<Address>,
    amount: i128,
    timeout_ledger: u32,
    milestone_count: u32,
) -> u64
```
- **Returns**: `u64` - Unique escrow ID.
- **Requirements**: `payer.require_auth()`, `amount > 0`, `timeout_ledger > current_ledger`.

---

### 2. `release_milestone`
Releases the payout for a specific completed milestone to the merchant.

```rust
pub fn release_milestone(
    env: Env,
    escrow_id: u64,
    caller: Address,
    milestone_index: u32,
) -> bool
```
- **Requirements**: `caller.require_auth()`, caller must be payer or approved mediator.

---

### 3. `refund_escrow`
Refunds all remaining escrow balance back to the payer if the timeout ledger has passed without milestone fulfillment.

```rust
pub fn refund_escrow(
    env: Env,
    escrow_id: u64,
    caller: Address,
) -> bool
```
- **Requirements**: `caller.require_auth()`, current ledger > timeout ledger, no active dispute lock.

---

### 4. `open_dispute`
Halts all automated payouts and locks the escrow into dispute arbitration mode.

```rust
pub fn open_dispute(
    env: Env,
    escrow_id: u64,
    caller: Address,
) -> bool
```
- **Requirements**: `caller.require_auth()`, caller must be payer or merchant.

---

### 5. `resolve_dispute`
Arbitrates a disputed escrow, splitting remaining funds between payer and merchant.

```rust
pub fn resolve_dispute(
    env: Env,
    escrow_id: u64,
    mediator: Address,
    merchant_payout: i128,
    payer_payout: i128,
) -> bool
```
- **Requirements**: `mediator.require_auth()`, caller must match assigned mediator, `merchant_payout + payer_payout == remaining_balance`.

---

### 6. `set_spend_cap`
Configures a rolling 24-hour spend cap for an authorized agent or delegate.

```rust
pub fn set_spend_cap(
    env: Env,
    owner: Address,
    agent: Address,
    daily_cap: i128,
    per_tx_cap: i128,
) -> bool
```
- **Requirements**: `owner.require_auth()`.

---

### 7. `execute_delegated_payment`
Executes an automated payment on behalf of an owner while enforcing daily rolling window limits.

```rust
pub fn execute_delegated_payment(
    env: Env,
    owner: Address,
    agent: Address,
    recipient: Address,
    amount: i128,
) -> bool
```
- **Requirements**: `agent.require_auth()`, `amount <= per_tx_cap`, cumulative 24h spend <= daily_cap.
