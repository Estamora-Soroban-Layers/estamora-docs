# Contributing to Estamora Docs

Thank you for contributing to `estamora-docs`! This repository contains the source documentation for the Estamora protocol on Stellar.

## Local Development

```bash
git clone https://github.com/Estamora-Soroban-Layers/estamora-docs.git
cd estamora-docs

# Install MkDocs with Material theme
pip install mkdocs mkdocs-material

# Run local development server
mkdocs serve

# Verify build
mkdocs build --strict
```

## Guidelines

1. **Accuracy**: Code examples and contract addresses must match the deployed smart contracts on Stellar Testnet.
2. **Clear Architecture**: Emphasize how the smart contracts, TypeScript SDK, and web application integrate seamlessly.
