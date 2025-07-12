---
title: zk-sql-via-smart-contracts
date: 2025-07-11 18:39:05
path: /Users/chrisryviss/undetectable_toolkit/scraped_content/zk-sql-via-smart-contracts.markdown
---

Space and Time is the first trustless database for the EVM, enabling smart contracts to interact with historical, cross-chain, or offchain data as if it were natively accessible onchain.

## ZK-SQL Execution from your Smart Contract

Execution of ZK-proven query from your smart contract is as simple as sending your request along with a small payment to the ZKpay query relayer contract.

In your smart contract, you simply:

- Import ZKPay and the Proof of SQL onchain verifier
- Set the contract addresses for the chain you're on (see below)
- Authorize a small amount of USDC or SXT to cover all payments, such as query execution, return of the final data set back onchain, onchain verification, etc.
- Convert your SQL Statement into a hex query plan - check out the [Proof of SQL SDK](https://github.com/spaceandtimefdn/sxt-proof-of-sql-sdk) for details
- Send the request to ZKpay query relayer contract
- Make sure to implement the `zkPayCallback` function, which will be called back by ZKpay once the data is complete and verified.

**To see this in action, check out this [working solidity contract](/recipes/run-a-zk-proven-query-from-a-smart-contract):**

---

# Contract Addresses

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

![](https://files.readme.io/f4b39d3a3a93ae6b0929a024f6fa8ecbbbf4006930d99e7facee9b07fc45587c-diagram05.png)


---

# How to Run and Verify Queries on a Local Device

You can also run zk-proven queries and verify results, on your local device.

The [Space and Time Proof of SQL SDK](https://github.com/spaceandtimefdn/sxt-proof-of-sql-sdk) is a Rust crate designed to simplify the process of running SQL queries against Space and Time (SXT Chain) and verifying the results using cryptographic proofs. It leverages the Proof of SQL framework to ensure the integrity and correctness of query results.

To get started with this Rust crate SDK, follow the instructions on this repo:  
<https://github.com/spaceandtimefdn/sxt-proof-of-sql-sdk>

For more information on the Proof of SQL product holistically, check out:  
<https://github.com/spaceandtimefdn/sxt-proof-of-sql>

Updated about 1 month ago

---

Did this page help you?

Yes

No