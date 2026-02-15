"""
LiveKit Token Generation API
Provides access tokens for frontend to connect to LiveKit rooms
"""
from livekit import api
import os

def generate_token(room_name: str, participant_name: str) -> str:
    """Generate LiveKit access token for a participant"""
    token = api.AccessToken(
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
    )
    
    token.with_identity(participant_name).with_name(participant_name).with_grants(
        api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        )
    )
    
    return token.to_jwt()
