from typing import Optional, List
import hashlib
from stacks_transactions import (
    make_contract_call, TransactionOptions,
    chain_id, network
)
import secrets
import asyncio
from dataclasses import dataclass
from datetime import datetime
import jwt
from redis import Redis
from typing import Dict

@dataclass
class IdentityMetadata:
    address: str
    reputation: int
    trust_score: int
    achievements: List[int]
    last_login: datetime
    validator_count: int

class EnhancedIdentityManager:
    def __init__(
        self, 
        stacks_api_url: str, 
        contract_address: str, 
        contract_name: str,
        redis_url: str,
        jwt_secret: str
    ):
        self.stacks_api_url = stacks_api_url
        self.contract_address = contract_address
        self.contract_name = contract_name
        self.network = network.mainnet
        self.redis = Redis.from_url(redis_url)
        self.jwt_secret = jwt_secret
        
    async def generate_session_token(self, user_address: str) -> str:
        """Generate a JWT session token for authenticated users."""
        identity = await self.get_identity(user_address)
        
        payload = {
            "sub": user_address,
            "reputation": identity.reputation,
            "trust_score": identity.trust_score,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    async def validate_session_token(self, token: str) -> Dict:
        """Validate a session token and return the decoded payload."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            # Check if user is still active
            identity = await self.get_identity(payload["sub"])
            if not identity:
                raise ValueError("Identity no longer exists")
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    async def get_identity(self, user_address: str) -> Optional[IdentityMetadata]:
        """Fetch identity information from blockchain."""
        try:
            # First check cache
            cached_data = self.redis.get(f"identity:{user_address}")
            if cached_data:
                return IdentityMetadata(**json.loads(cached_data))
            
            tx_options = TransactionOptions(chain_id=chain_id.mainnet)
            response = await make_contract_call(
                contract_address=self.contract_address,
                contract_name=self.contract_name,
                function_name="get-identity",
                function_args=[user_address],
                sender_address=user_address,
                tx_options=tx_options
            )
            
            if response.success:
                identity = IdentityMetadata(
                    address=user_address,
                    reputation=response.result["reputation-score"],
                    trust_score=response.result["trust-score"],
                    achievements=response.result["achievements"],
                    last_login=datetime.fromtimestamp(response.result["last-login"]),
                    validator_count=response.result["validator-count"]
                )
                
                # Cache the result
                self.redis.setex(
                    f"identity:{user_address}",
                    300,  # 5 minutes cache
                    json.dumps(identity.__dict__)
                )
                return identity
            return None
            
        except Exception as e:
            print(f"Error fetching identity: {e}")
            return None
    
    async def register_new_identity(
        self, 
        user_address: str, 
        game_data: Optional[str] = None,
        recovery_address: Optional[str] = None
    ) -> dict:
        """Register a new digital identity with enhanced features."""
        try:
            tx_options = TransactionOptions(chain_id=chain_id.mainnet)
            function_args = []
            if game_data:
                function_args.append(game_data)
            if recovery_address:
                function_args.append(recovery_address)
                
            tx = await make_contract_call(
                contract_address=self.contract_address,
                contract_name=self.contract_name,
                function_name="register-identity",
                function_args=function_args,
                sender_address=user_address,
                tx_options=tx_options
            )
            
            return {
                "status": "success",
                "transaction_id": tx.txid,
                "user_address": user_address,
                "session_token": await self.generate_session_token(user_address)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def add_achievement(
        self,
        user_address: str,
        achievement_id: int
    ) -> dict:
        """Add an achievement to a user's identity."""
        try:
            tx_options = TransactionOptions(chain_id=chain_id.mainnet)
            
            tx = await make_contract_call(
                contract_address=self.contract_address,
                contract_name=self.contract_name,
                function_name="add-achievement",
                function_args=[user_address, achievement_id],
                sender_address=self.admin_address,
                tx_options=tx_options
            )
            
            # Invalidate cache
            self.redis.delete(f"identity:{user_address}")
            
            return {
                "status": "success",
                "transaction_id": tx.txid,
                "achievement_id": achievement_id
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }