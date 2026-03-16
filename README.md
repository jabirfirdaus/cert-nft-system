# Certificate NFT System (CertNFT)

![Solidity](https://img.shields.io/badge/Solidity-e6e6e6?style=for-the-badge&logo=solidity&logoColor=black)
![Foundry](https://img.shields.io/badge/Foundry-white?style=for-the-badge)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

A professional-grade, decentralized certificate issuance system leveraging the Ethereum blockchain. This project utilizes ERC-721 Non-Fungible Tokens (NFTs) to provide immutable, publicly verifiable, and secure digital credentials for graduates, event attendees, or achievement earners.

## Architecture & Core Features

- **Immutable Credentials:** Once minted, the certificate data is permanently secured on the blockchain, eliminating the risk of forgery.
- **OpenZeppelin Integration:** Built upon battle-tested OpenZeppelin ERC-721 contracts to ensure maximum security and industry-standard compliance.
- **On-Chain Verification:** Anyone can verify the authenticity and ownership of a certificate without relying on a centralized database.
- **Gas Optimized:** Smart contract logic is streamlined to ensure minimal gas consumption during the batch-minting or individual issuance processes.

## Live Deployment

The smart contract has been successfully deployed and verified on the blockchain.

- **Network:** [Sepolia Testnet]
- **Contract Address:** `[0xd1eD6112A65492a761C8Fe68666a1f8cd32e49A0]`
- **Block Explorer:** [https://sepolia.etherscan.io/address/0xd1eD6112A65492a761C8Fe68666a1f8cd32e49A0]

## Getting Started

### Prerequisites

- [Foundry](https://getfoundry.sh/) installed on your local machine.

### Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/jabirfirdaus/cert-nft-system.git](https://github.com/jabirfirdaus/cert-nft-system.git)
   cd cert-nft-system
   ```

2. **Install dependencies:**

   ```bash
   forge install
   ```

3. **Build the smart contract:**

   ```bash
   forge build
   ```

4. **Deploy the smart contract:**

   ```bash
   forge script script/DeployCertNFT.s.sol:DeployCertNFTScript --rpc-url <your_rpc_url> --private-key <your_private_key>
   ```

5. **Verify the smart contract:**

   ```bash
   forge verify 0xd1eD6112A65492a761C8Fe68666a1f8cd32e49A0 --rpc-url <your_rpc_url> --constructor-args script/DeployCertNFT.s.sol:DeployCertNFTScript --chain-id <your_chain_id>
   ```

6. **Interact with the smart contract:**
   ```bash
   forge script script/InteractCertNFT.s.sol:InteractCertNFTScript --rpc-url <your_rpc_url> --private-key <your_private_key>
   ```
