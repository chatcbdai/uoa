---
title: inserting-data-dml
date: 2025-07-11 18:38:42
path: /Users/chrisryviss/undetectable_toolkit/scraped_content/inserting-data-dml.markdown
---

# Table Creation Overview

SXT Chain is a permissionless L1 blockchain that acts as a decentralized database and enables developers to define, own, and maintain tamperproof tables using standard SQL DDL. These tables form the foundation of Space and Time’s verifiable data model, allowing structured data to be inserted, queried, and cryptographically proven at scale.

Creating a table on SXT Chain is similar to defining a schema in any relational database, but with added guarantees of verifiability and decentralized consensus. Developers submit to SXT Chain an EDDSA or ED25519-signed Substrate transaction containing CREATE TABLE SQL syntax to define table structure, including column types, constraints, and optional permissions metadata.

Once defined, the table is:

- Assigned a unique table ID
- Associated with an initial table owner (the signer of the DDL transaction)
- Registered in the SXT Chain onchain registry
- Bound to a cryptographic commitment representing the table’s state (initially empty)

All inserts, updates, and deletions from that point forward are tracked by cryptographic commitments stored onchain, allowing for ZK-proven query execution and verifiable data integrity.

When creating a SXT Chain table, there are several permission types depending on access model and usage pattern:

- **Public Write Tables**: Any user can submit data (e.g., public content feeds or game leaderboards).
- **Owner-Permissioned Tables**: Only the table owner (or a whitelisted set of public keys) can insert data. Useful for oracle publishers or protocol-owned datasets.
- **User-Verified Tables**: Require that each row is signed by a user (ECDSA / ED25519), and optionally verified with zkTLS or indexer consensus.

Ownership is defined at table creation via the wallet signature that initiates the DDL transaction, and can later be delegated, transferred, or extended using authorization keys, aka Biscuit tokens, allowing for granular access.

---

# Table Lifecycle

The full life-cycle of a table:

1. **Create Table (DDL)**: Developer submits a signed CREATE TABLE statement via RPC, REST API, or onchain extrinsic.
2. **Validators Verify and Commit**: The table schema is validated, registered onchain, and a cryptographic commitment is initialized.
3. **Inserts Begin**: Insert transactions are routed, verified, and committed via threshold consensus. The table's commitment is updated on each state change.
4. **Queries Executed**: Prover nodes read from the offchain table storage and use the latest commitment to generate ZK proofs for query results.

---

# Securing Tables with Cryptographic Commitments

Every table on Space and Time is secured by a cryptographic commitment —a lightweight, tamper-evident fingerprint of its current state.

**Space and Time table commitments are:**

- **Maintained by Validators**: Each time data is inserted or modified, the validator set verifies the transaction and collaboratively updates the table’s commitment using a threshold signature scheme.
- **Updated Onchain**: The latest commitment hash for each table is posted in a block on SXT Chain, ensuring tamperproof recordkeeping.
- **Homomorphic**: New rows can be appended and a new commitment generated without needing access to the full table contents.
- **Used in ZK Queries**: When a ZK query is executed against a table, the Prover uses the commitment to prove the data hasn’t been modified or forged.

These commitments are the core crypto-economic responsibility of Space and Time validators: they attest to the correctness of every update and publish commitment roots that the rest of the system uses for verification.

---

# Table Storage

While the commitments are stored onchain, the full row-level table data is stored offchain—but redundantly pinned across a decentralized validator set:

- Validators opt-in to storing table data to support query execution and ZK proof generation.
- Table data is stored in columnar or row-based formats (depending on Prover compatibility) and structured for high-throughput analytics.
- Prover nodes query this offchain data when generating ZK proofs of SQL queries.
- Anyone can opt to store table data for public or private queries, enabling horizontal scale.

This separation of storage (offchain) and verification (onchain) ensures high availability and performance without sacrificing the tamperproof guarantees of the network.

Updated 2 months ago

---

Did this page help you?

Yes

No