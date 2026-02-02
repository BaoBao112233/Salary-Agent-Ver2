from typing import Optional
from pydantic import BaseModel 

class ChatRequest(BaseModel):
    session_id: int
    user_id: int
    message: str
    user_image: Optional[str] = None
    tweet_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    tweet_id: Optional[str] = None
    error_status: str = "success"