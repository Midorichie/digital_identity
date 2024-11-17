from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from enhanced_identity_manager import EnhancedIdentityManager
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json

app = FastAPI()
security = HTTPBearer()
identity_manager = EnhancedIdentityManager(
    stacks_api_url="https://stacks-node-api.mainnet.stacks.co",
    contract_address="ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM",
    contract_name="digital-identity",
    redis_url="redis://localhost:6379/0",
    jwt_secret="your-secret-key"
)

class GameProfile(BaseModel):
    username: str
    game_specific_data: Optional[str]
    recovery_address: Optional[str]

class Achievement(BaseModel):
    id: int
    name: str
    description: str

ACHIEVEMENTS = {
    1: Achievement(id=1, name="First Victory", description="Win your first game"),
    2: Achievement(id=2, name="Social Butterfly", description="Play with 10 different players"),
    3: Achievement(id=3, name="Veteran", description="Reach 100 games played")
}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = await identity_manager.validate_session_token(credentials.credentials)
        return payload["sub"]
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/register")
async def register_game_profile(profile: GameProfile):
    """Register a new player with digital identity."""
    result = await identity_manager.register_new_identity(
        user_address=profile.username,
        game_data=profile.game_specific_data,
        recovery_address=profile.recovery_address
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.get("/profile")
async def get_profile(current_user: str = Depends(get_current_user)):
    """Get the current player's profile and achievements."""
    identity = await identity_manager.get_identity(current_user)
    
    if not identity:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    achievements = [
        ACHIEVEMENTS[ach_id] for ach_id in identity.achievements
        if ach_id in ACHIEVEMENTS
    ]
    
    return {
        "address": identity.address,
        "reputation": identity.reputation,
        "trust_score": identity.trust_score,
        "achievements": achievements,
        "last_login": identity.last_login,
        "validator_count": identity.validator_count
    }

@app.post("/achievements/{achievement_id}")
async def award_achievement(
    achievement_id: int,
    current_user: str = Depends(get_current_user)
):
    """Award an achievement to the current player."""
    if achievement_id not in ACHIEVEMENTS:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    result = await identity_manager.add_achievement(
        user_address=current_user,
        achievement_id=achievement_id
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {
        "message": f"Achievement '{ACHIEVEMENTS[achievement_id].name}' awarded",
        "transaction_id": result["transaction_id"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)