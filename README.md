# 🚀 Smart Contract & Web3 Portfolio

Welcome to my Web3 development portfolio. I am a Smart Contract developer specializing in Solidity, Web3.py, and Ethereum blockchain solutions. 

## 🛠 Tech Stack
- **Languages:** Solidity, Python
- **Frameworks/Libraries:** Web3.py, py-solc-x
- **Blockchain:** Ethereum (Local Ganache & Testnets)

## 📁 Projects

### 1. Advanced ERC-20 Token (HajiCoin)
A fully functional ERC-20 token built from scratch using Solidity. It includes advanced tokenomics features such as:
- **Minting:** Owner can create new tokens.
- **Burning:** Users can burn their tokens to reduce total supply.
- **Standard Transfers & Balances:** Fully compliant with the ERC-20 standard.
- **Deployment:** Automated deployment and interaction scripts written in Python using Web3.py.

### 2. Decentralized Voting System
A secure and transparent voting smart contract. 
- Prevents double-voting using address mapping.
- Only the contract owner can add new candidates.
- Fully tested on simulated EVM.

### 3. Simple Storage (Python Integration)
A foundational smart contract demonstrating the integration of Python with Ethereum. It stores a number on the blockchain and updates it via Python scripts.

### 4. ERC-721 NFT Collection (Haji Art)
A complete implementation of the ERC-721 standard for creating Non-Fungible Tokens (NFTs).
- **Minting:** Allows creating unique NFTs with a specific Token ID.
- **Metadata (TokenURI):** Attaches a unique URI (like an IPFS link) to each NFT, which points to its image and properties.
- **Transfer:** Enables the secure transfer of NFTs between wallets, ensuring the ownership and metadata remain intact.

- ### 5. DeFi Staking Protocol
A complete Decentralized Finance (DeFi) staking smart contract. This project demonstrates how users can lock their tokens to earn rewards over time.
- **Time-Based Rewards:** Calculates user rewards automatically based on the exact time their tokens are staked using `block.timestamp`.
- **Secure Approvals:** Uses the `Approve` and `transferFrom` patterns to safely handle user deposits without compromising wallet security.
- **Automated Withdrawal:** Users can withdraw their principal (staked tokens) and earned rewards seamlessly in a single transaction.
- **Testing:** Simulated time-travel testing using Python and Ganache to verify accurate reward calculation and smart contract logic.

## 🐍 How to Run Locally
1. Clone this repository.
2. Install dependencies: `pip install web3 py-solc-x`
3. Start a local blockchain (e.g., Ganache).
4. Run the Python deployment scripts: `python <script_name>.py`
