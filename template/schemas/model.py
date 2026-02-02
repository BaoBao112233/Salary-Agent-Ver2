from pydantic import BaseModel, Field
from typing import Optional, Any


class ChatRequest(BaseModel):
    session_id: int
    user_id: int
    message: str
    user_image: Optional[str] = None
\
class ChatResponse(BaseModel):
    response: str
    error_status: str = "success"

# Request models
class ChatRequestAPI(BaseModel):
    session_id: int = Field(..., description="Unique identifier for the user session")
    user_id: int = Field(..., description="Unique identifier for the user id")
    message: str = Field(..., description="User message to process")
    user_image: Optional[str] = Field("", description="User imagem to process")

# Response models
class APIResponse(BaseModel):
    success: bool = True
    data: Any = None
    error: Optional[str] = None