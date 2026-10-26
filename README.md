# 🚀 Advanced DeFi Staking Protocol

A professional, production-ready DeFi Staking Smart Contract built with **Solidity** and tested using **Python (Web3.py)**. 

This repository provides a complete, secure, and highly customizable staking solution for Web3 projects. It allows users to stake their ERC-20 tokens and earn continuous rewards based on time.

## ✨ Key Features (Why choose this?)

- **🔒 Security First:** Implements a custom `nonReentrant` modifier to prevent reentrancy attacks, ensuring user funds are always safe.
- **👑 Owner Controls:** Includes an `onlyOwner` modifier allowing the contract deployer to safely adjust the `rewardRate` without compromising the system.
- **🛡️ Emergency Withdraw:** Users can safely withdraw their principal tokens at any time without claiming rewards in case of emergencies.
- **📊 Real-time Earnings:** Includes a view function `earned(address)` to check current pending rewards before withdrawal.
- **⚙️ Automated Deployment:** Comes with a Python script (`staking_v2.py`) to automatically compile, deploy, and simulate the entire staking lifecycle.

## 🛠 Tech Stack
- **Smart Contracts:** Solidity `^0.8.0`
- **Blockchain Interaction:** Python, `web3.py`
- **Compiler:** `py-solc-x`

## 📦 What's Included in this Package?
When you purchase this package, you get:
1. `staking_v2.py`: The complete Python script containing the Solidity code, compiler, deployer, and testing simulation.
2. `README.md`: Full documentation (this file).

## 🚀 How to Run and Test Locally

Follow these simple steps to test the smart contract on your local machine:

### 1. Prerequisites
- Python 3.8+ installed.
- [Ganache](https://trufflesuite.com/ganache/) installed and running on `http://localhost:7545`.

### 2. Install Dependencies
Open your terminal and run:
```bash
pip install web3 py-solc-x