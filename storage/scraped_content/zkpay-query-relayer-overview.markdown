---
title: zkpay-query-relayer-overview
date: 2025-07-11 18:38:48
path: /Users/chrisryviss/undetectable_toolkit/scraped_content/zkpay-query-relayer-overview.markdown
---

ZKpay is a cross-chain payment protocol we developed to enable smart contracts, agents, humans, or dapps to send flexible payments to onchain service providers, such as "data oracles" like Space and Time.

Github repo: <https://github.com/spaceandtimefdn/sxt-zkpay-contracts>

**The main functionalities that ZKpay provides are:**

- Send direct payment to service provider without any data returned to the client..
- Execute a ZK-proven proven query and handle payment along with callback for the query result.

![](https://files.readme.io/ea006b24ef5fe4ca59470af7df6d5d87f439821d56434f51e44364f5733face7-diagram01_1_1.png)

**Send Payment to Service Provider without Query**  
Users/dApps can send payment to target service provider by calling one of the following methods on ZKpay contract:

```
function send(address asset, uint248 amount, bytes32 onBehalfOf, address target, bytes calldata memo) external;

function sendNative(bytes32 onBehalfOf, address target, bytes calldata memo) external payable;

```

Payer should specify few parameters like asset and amount they are paying, payer address, target service provider and encoded blob of bytes that will be decoded and understood by the service provider.

![](https://files.readme.io/2b166f926b3e624cebb6c7a64e0a1ebfbf18fae20c607fbd5810fa944d97b159-diagram02.png)

**Send Payment to Service Provider and receive a Query Result**  
Smart contracts uses this method to query data or computations off-chain from a specific service provider by specifying service provider target custom logic contract, and including payment to cover both service provider's fees + gas callback transaction, if client over pays the remainder will be settled and sent back to client contract.

```
/// @notice Submit a query with a payment in ERC20 tokens.
/// @param asset The ERC20 token used for the payment.
/// @param amount The amount of tokens to deposit.
/// @param queryRequest The struct containing the query details.
/// @return queryHash The unique hash representing the query.
function query(address asset, uint248 amount, QueryLogic.QueryRequest calldata queryRequest)

```

The query request is a struct that includes: query blob, query parameters, timeout, callback gas limit, service provider's custom logic contract address, and callback data. Refer to [struct definition here](https://github.com/spaceandtimefdn/sxt-zkpay-contracts/blob/dfa2fcc3e2270c6d27b483afae407d57769a2a6c/src/libraries/QueryLogic.sol#L73-L97).

**Overview of an Onchain Query with ZKpay**  
Below outlines the process of running an onchain query from a smart contract using Space and Time.

-Request is initiated when a client smart contract makes a call to Space and Time's ZKpay relayer contract, including the SQL plan (hex encoded) to execute, any parameters, etc.

-The relayer contract signs the request and places it onchain for delivery as events emitted on Ethereum (which Space and Time listens for).

-A collection of special listeners called indexers in the Space and Time network will identify the request, verify the authenticity, then issue the query to the data network for processing.

-Largely in parallel with the query execution, the Proof of SQL engine will generate the associated ZK-proof. Note, this step is skipped for optimistic queries in MakeInfinite's Managed DB offering.

-Usage of compute is calculated and deducted from the account's ZKpay ledger, if applicable (specifically for pre-payments, rather than the normal use case of client contracts sending payment along with they're query for each request).

-The final query result, ZK-proof, signed cryptographic commitments from Space and Time, and the query fee report are all prepared and sent back onchain by prover.

-The onchain zk proof can be sent to an onchain verifier, which will verify the compute and data as untampered.

The query results, zk proof, verifier receipt and query are all returned back to the initiating contract for further processing.

![](https://files.readme.io/9a3a32e9faab6b67f383fc75048551f69b262bec09a09841f964a6f0971365e9-Screenshot_2025-05-08_at_4.34.35_AM.png)

Updated 2 months ago

---

Did this page help you?

Yes

No