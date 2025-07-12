---
title: docs
date: 2025-07-11 18:38:30
path: /Users/chrisryviss/undetectable_toolkit/scraped_content/docs.markdown
---

# The Blockchain for ZK-proven Data

Space and Time (SXT Chain) is an open source, decentralized layer 1 blockchain where validators verify and sign every piece of data that gets inserted. They don’t store the raw data—instead, they update cryptographic commitments (similar to digital fingerprints) for each table and collectively sign those commitments before recording them on-chain. This ensures that the structure and contents of every table are locked in and tamperproof. Alongside the validators, Prover nodes monitor query requests coming from EVM contracts. When a query is triggered, a Prover runs the SQL logic off-chain against the validated data—whether it's from SXT Chain tables or blockchain data indexed by redundant, crypto-secured servers. The Prover then generates a zero-knowledge proof that the query was executed correctly over untampered data, and ZK-oracles the results back onchain to your EVM contract via a callback.

To put it simply: validators seal the data with cryptographic proofs, and [prover nodes](https://github.com/spaceandtimefdn/sxt-proof-of-sql) do the computation and prove that data retrieval results (SQL queries) are honest—without anyone needing to re-run the work. The proof is tiny, fast to verify, and trustless.

For more information, [check out the Proof of SQL (ZK-prover) repo](https://github.com/spaceandtimefdn/sxt-proof-of-sql?tab=readme-ov-file#proof-of-sql).

---

![](https://files.readme.io/54286c5790cfe492be530ff91bef820165d5abbd395c4ba21bcc08bdc7c5906f-image.png)

# Developers use Space and Time to...

> ## 🤝
>
> Connect indexed onchain data and your signed offchain data
>
> Connect to comprehensive blockchain data we've indexed from major chains in real time as well as offchain data you've ingested from your app or source db. SXT indexes Ethereum, Bitcoin, ZKsync, Polygon, Sui, Avalanche, and we're continually adding support for more chains.

> ## 📊
>
> Query data from EVM smart contracts with SQL
>
> Leverage a familiar SQL interface to ask questions using the ZKpay query relayer contract. As a domain-specific ZK coprocessor and the first trustless SQL database for the EVM, it enables smart contracts to run fully verifiable SQL queries against both on-chain indexed data (e.g., decoded EVM events) and user-generated off-chain tables.

> ## 🔐
>
> ZK-prove your query results
>
> Send verifiable query results directly to your smart contract with Proof of SQL, SXT's sub-second ZK coprocessor. SXT enables your smart contract to process data at the scale required to power your application in the time it needs to transact.

> ## 👩‍💻
>
> Publish queries to smart contracts, APIs, apps, or dashboards
>
> Publish datasets and queries directly to APIs, build sophisticated onchain apps on top of SXT, and power the next generation of expressive, data-driven smart contracts with Proof of SQL.

  

Space and Time has deployed ZKpay query relayer contracts that act as onchain interfaces for receiving already-ZK-verified SQL results. Those contracts can be found here:

### ZKpay Query Relayer Contract Addresses:

- **Ethereum Mainnet**: [0x27d4d2af364c1ad2ebdb2a28d6cb7b99ede1d450](https://etherscan.io/address/0x27d4d2af364c1ad2ebdb2a28d6cb7b99ede1d450)
- **Ethereum Sepolia**: [0xA735143283a6E686723403A820841E5774951a63](https://sepolia.etherscan.io/address/0xA735143283a6E686723403A820841E5774951a63)
- **Base**: coming soon!
- **ZKSync**: coming soon!

### Onchain Verifier Contract Addresses:

- **Ethereum Mainnet**: [0x84d6795ff1fCc224De328C86C318fABC396826B0](https://etherscan.io/address/0x84d6795ff1fCc224De328C86C318fABC396826B0)
- **Ethereum Sepolia**: [0x99b3c29dDC225F75f9248c863379b195Ef9D82C2](https://sepolia.etherscan.io/address/0x99b3c29dDC225F75f9248c863379b195Ef9D82C2)
- **Base**: coming soon!
- **ZKSync**: coming soon!

---

# Sub-second Zero Knowledge Proofs

Space and Time (SXT Chain) is the first trustless database for the EVM, enabling smart contracts to interact with historical, cross-chain, or offchain data as if it were natively accessible onchain. **Space and Time (SXT Chain) is optimized for:**

- High-throughput data ingestion from blockchains, consumer apps, and enterprise sources
- Verifiable query execution over large datasets (millions of rows)
- Fast ZK proof generation and EVM-compatible proof verification with minimal gas

**Key Features of SXT Chain**

- The first cryptographically tamperproof decentralized database for EVM verification.
- Supports ZK-proven SQL queries against chain-secured tables.
- Flagship performance: GPU provers perform SQL computations sub-second on large datasets.
- Indexes verified data from chains like Ethereum, Bitcoin, Base, ZKsync, Sui, and many more.
- Cryptographically tamperproof database with zero knowledge proofs of query results that are verifiable with **150k gas on the EVM**.

---

Space and Time (SXT Chain) scales zero-knowledge (ZK) proofs on a decentralized data warehouse to deliver trustless data processing to smart contracts. You can use SXT to join comprehensive blockchain data we've indexed from major chains with your app's data or other offchain datasets. Proof of SQL is SXT's sub-second ZK coprocessor, which allows your smart contract to ask complicated questions about activity on its own chain or other chains and get back a ZK-proven answer next block. SXT enables a new generation of smart contracts that can transact in real time based on both onchain data (like txns, blocks, smart contract events, storage slot changes, etc.) and data from your app, ultimately delivering a more robust onchain economy and more sophisticated onchain applications.

> Jump over to [Discord](https://discord.com/invite/spaceandtimedb) to join the Space and Time community!

Updated 2 months ago

---

Did this page help you?

Yes

No