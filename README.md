# Decentralized Digital Identity Verification System

A blockchain-based digital identity system built on Stacks for gaming and general identity verification. This system provides secure, decentralized identity management with features like reputation scoring, achievements, and identity recovery.

## 🌟 Features

### Core Identity Management
- Decentralized identity registration and verification
- Secure cryptographic challenge-response system
- Reputation and trust scoring
- Activity tracking and login management
- Game-specific data storage

### Enhanced Security
- Multi-validator identity verification
- Identity recovery mechanism
- JWT-based session management
- Cached identity lookups
- Secure cryptographic utilities

### Gaming Integration
- NFT-based achievement system
- Player reputation management
- Game-specific profile data
- REST API for game integration
- Session-based authentication

## 🛠 Technology Stack

- **Smart Contracts**: Clarity on Stacks blockchain
- **Backend**: Python (FastAPI)
- **Cryptography**: Rust
- **Caching**: Redis
- **Authentication**: JWT

## 📋 Prerequisites

- Python 3.8+
- Rust toolchain
- Redis server
- Stacks node access
- Node.js and npm (for contract deployment)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/digital-identity-system
cd digital-identity-system
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Rust dependencies
cd crypto-utils
cargo build --release

# Install Clarity contract dependencies
npm install @stacks/transactions
```

### 3. Configure Environment

Create a `.env` file:

```env
STACKS_API_URL=https://stacks-node-api.mainnet.stacks.co
CONTRACT_ADDRESS=your_contract_address
CONTRACT_NAME=digital-identity
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your_jwt_secret
```

### 4. Deploy Smart Contract

```bash
# Deploy using Clarinet
clarinet deploy contracts/digital-identity.clar
```

### 5. Start the Backend

```bash
# Start Redis
redis-server

# Start the FastAPI server
uvicorn app.main:app --reload
```

## 📚 API Documentation

### Authentication

All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

### Endpoints

#### Register New Identity
```http
POST /register
Content-Type: application/json

{
    "username": "string",
    "game_specific_data": "string",
    "recovery_address": "string"
}
```

#### Get Profile
```http
GET /profile
Authorization: Bearer <token>
```

#### Award Achievement
```http
POST /achievements/{achievement_id}
Authorization: Bearer <token>
```

## 🔒 Security Features

### Identity Recovery
The system implements a secure identity recovery mechanism:
1. Users can designate a recovery address during registration
2. Recovery requires cryptographic proof of ownership
3. Recovery process maintains all user data and achievements

### Validation System
- Multi-validator approach for enhanced security
- Trust score calculation based on validator consensus
- Reputation scoring with achievement impact

## 🎮 Game Integration Guide

### 1. Initialize Identity Manager
```python
from enhanced_identity_manager import EnhancedIdentityManager

identity_manager = EnhancedIdentityManager(
    stacks_api_url="your_api_url",
    contract_address="your_contract_address",
    contract_name="digital-identity",
    redis_url="your_redis_url",
    jwt_secret="your_secret"
)
```

### 2. Register Player
```python
result = await identity_manager.register_new_identity(
    user_address="player_address",
    game_data="optional_game_data",
    recovery_address="optional_recovery_address"
)
```

### 3. Award Achievements
```python
result = await identity_manager.add_achievement(
    user_address="player_address",
    achievement_id=1
)
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🙏 Acknowledgments

- Stacks Foundation for blockchain infrastructure
- FastAPI team for the excellent web framework
- OpenZeppelin for smart contract patterns