---
title: running-a-validator-node
date: 2025-07-11 18:38:54
path: /Users/chrisryviss/undetectable_toolkit/scraped_content/running-a-validator-node.markdown
---

Running a Validator node on Space and Time is a critical way to contribute to the protocol’s decentralization, security, and data integrity. Validators are responsible for securing the network’s tamperproof tables, processing data insertion commitments, and participating in zero-knowledge query verification checkpoints - they are the backbone of the Space and Time network and are rewarded for it.

For more details on mainnet validator ops: <https://github.com/spaceandtimefdn/sxt-node-docs/blob/main/mainnet.md>

Participating as a validator means:

- **Earning Block Rewards**: Validators receive fees from:
  - Insert-data gas payments (e.g., from clients or indexers)
  - Query verification fees (ZK-proven or optimistic)
  - Foundation staking subsidies (during bootstrap phase)
- **Participating in a Secure Data Economy**: You help maintain tamperproof commitments for indexed data tables and ensure accurate data verification, which enables smart contracts to query complex, verifiable analytics.
- **Receiving Delegated Stake**: Validators can attract delegated stakers who earn a share of validator rewards, boosting validator influence and earning potential.
- **Scaling the Future of Web3**: By running a validator, you're part of a decentralized backend for thousands of dapps, smart contracts, and cross-chain apps that rely on secure data and ZK proofs.

---

# What Validators Do

Validator nodes are the backbone of the Space and Time network, by providing:

### Sign Table Commitments

After new rows are inserted into a table (e.g., via Indexer or client), validators compute a new table root (using Dory, HyperKZG, etc.) and threshold-sign it.

### Verify Insert Transactions

Insertions may be client-submitted with zkTLS proofs, ECDSA user signatures, or proposed by Indexers. Validators check validity before updating table state.

### Participate in BFT Consensus

Validators vote on block proposals and participate in finality for data insertions, fee distributions, and contract execution.

### Support Query Verification

Verifier contracts rely on validator-published table commitments to verify ZK query proofs against the correct table state.

---

# Economic Incentives and Rewards

Validators of SXT Chain earn from multiple streams:

| Source | Description |
| --- | --- |
| Insert Data Fees | Collected when clients pay to insert data into tamperproof tables. 100% of this gas is routed into block rewards for validators. |
| Query Job Fees | ZK-proven and optimistic queries carry compute credit payments from clients. 50% of these go to validators; the other 50% goes to table owners. |
| Foundation Subsidies | Temporary incentives to bootstrap validator activity in the early network phase. |
| Delegated Staking Yield | Validators receive SXT delegations from community members. A portion of validator rewards are automatically shared with those delegators. |

Validators who perform poorly (e.g., go offline or sign incorrect commitments) may be slashed, losing a portion of their SXT stake and delegated stake.

---

# Node Hardware Requirements

> ## 🖥️
>
> To run a validator node, check out the setup guide here: [Validator Node Setup Guide](https://github.com/spaceandtimelabs/sxt-node-docs)

Minimum Hardware Requirements:

| Component | Requirement |
| --- | --- |
| CPU Cores | 16 |
| CPU Architecture | amd64, with virtualization support |
| Memory (GiB) | 64 |
| Storage (GiB) | 512 |
| Storage Type | SSD |
| OS | Linux |
| Network Speed | 500Mbps up/down |
| Network Addressing | Static IP |
| Deployment | Docker & Docker Compose installed |
| Staking | SXT tokens |

On Azure cloud, this is equivalent to SKU Standard\_D8as\_v5 with storage SKU of PremiumV2\_SSD.

Once configured, your validator will:

- Sync with the SXT Chain network
- Start signing commitments
- Receive real-time insert and query jobs
- Begin earning block rewards and delegation incentives

Updated about 1 month ago

---

Did this page help you?

Yes

No