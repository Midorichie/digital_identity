from typing import Optional
import hashlib
from stacks_transactions import (
    make_contract_call, TransactionOptions,
    chain_id, network
)
import secrets

class DigitalIdentityManager:
    def __init__(self, stacks_api_url: str, contract_address: str, contract_name: str):
        self.stacks_api_url = stacks_api_url
        self.contract_address = contract_address
        self.contract_name = contract_name
        self.network = network.mainnet
        
    def generate_challenge(self, user_address: str) -> str:
        """Generate a random challenge for user verification."""
        random_bytes = secrets.token_bytes(32)
        challenge = hashlib.sha256(random_bytes + user_address.encode()).hexdigest()
        return challenge
    
    async def register_new_identity(
        self, 
        user_address: str, 
        game_data: Optional[str] = None
    ) -> dict:
        """Register a new digital identity on the blockchain."""
        try:
            tx_options = TransactionOptions(chain_id=chain_id.mainnet)
            function_args = []
            if game_data:
                function_args.append(game_data)
                
            tx = make_contract_call(
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
                "user_address": user_address
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def verify_identity(self, user_address: str) -> dict:
        """Verify a user's digital identity."""
        try:
            tx_options = TransactionOptions(chain_id=chain_id.mainnet)
            
            # First check if registered
            tx = make_contract_call(
                contract_address=self.contract_address,
                contract_name=self.contract_name,
                function_name="is-registered",
                function_args=[user_address],
                sender_address=user_address,
                tx_options=tx_options
            )
            
            # Update login timestamp
            update_tx = make_contract_call(
                contract_address=self.contract_address,
                contract_name=self.contract_name,
                function_name="update-login",
                function_args=[],
                sender_address=user_address,
                tx_options=tx_options
            )
            
            return {
                "status": "success",
                "is_verified": True,
                "last_login_tx": update_tx.txid
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }