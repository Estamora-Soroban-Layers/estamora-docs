# Quickstart Guide

Get up and running with the Estamora protocol on Stellar Testnet in less than 5 minutes.

---

## 1. Install the SDK

Install the `@estamora/sdk` package in your Node.js or web project:

```bash
npm install @estamora/sdk @stellar/stellar-sdk
```

---

## 2. Initialize the Client

```typescript
import { EstamoraClient, TESTNET_CONFIG } from '@estamora/sdk';

// Initialize with default Stellar Testnet settings
const client = new EstamoraClient({
  networkPassphrase: TESTNET_CONFIG.networkPassphrase,
  rpcUrl: TESTNET_CONFIG.rpcUrl,
  contractId: 'CADQOBYHA4DQOBYHA4DQOBYHA4DQOBYHA4DQOBYHA4DQP5KR',
});
```

---

## 3. Run Pre-Flight Escrow Simulation

Before prompting the user's Freighter wallet or broadcasting a transaction to the network, run an off-chain pre-flight simulation:

```typescript
const simulation = await client.simulateCreateEscrow({
  payer: 'GA2C5RFPE6GCKMY3US5PAB6UZLKIGAHWKXX2G6EXO2Z6Q',
  merchant: 'GBEXAMPLEMERCHANT2G6EXO2Z6Q5PAB6UZLKIGAHWKXX',
  amount: 5000000000n, // 500 XLM in stroops
  timeoutSeconds: 86400, // 24 hours
  milestones: [
    { title: 'Initial deposit & design approval', amount: 2000000000n },
    { title: 'Final delivery & sign-off', amount: 3000000000n },
  ],
});

if (simulation.success) {
  console.log('Pre-flight simulation passed! Viability score: 100%');
  console.log(`Estimated CPU instructions: ${simulation.estimatedCpuInstructions}`);
} else {
  console.error('Simulation rejected:', simulation.errorMessage);
}
```

---

## 4. Testnet Contract Details

- **Network**: Stellar Testnet
- **Contract ID**: `CADQOBYHA4DQOBYHA4DQOBYHA4DQOBYHA4DQOBYHA4DQP5KR`
- **RPC URL**: `https://soroban-testnet.stellar.org`
- **Horizon URL**: `https://horizon-testnet.stellar.org`
- **Web Console**: [`https://estamora-app.vercel.app`](https://estamora-app.vercel.app)
