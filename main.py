import os
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Any
import logging
from template.configs.environments import env
from template.agent.agent import Agent, ChatRequest, ChatResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Initialize the FastAPI app
app = FastAPI(
    title="Template AI API",
    description="API for interacting with the Template Agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Request models
class ChatRequestAPI(BaseModel):
    session_id: int = Field(..., description="Unique identifier for the user session")
    user_id: int = Field(..., description="Unique identifier for the user id")
    message: str = Field(..., description="User message to process")
    user_image: Optional[str] = Field("", description="User imagem to process")
    tweet_id: Optional[str] = Field("", description="User Tweet ID")

# Response models
class APIResponse(BaseModel):
    success: bool = True
    data: Any = None
    error: Optional[str] = None


# Routes
@app.post("/ai/chat", response_model=ChatResponse)
async def chat(request: ChatRequestAPI, background_tasks: BackgroundTasks):
    """Process a chat message and return a response"""
    try:
        agent = Agent(api_key=env.OPENAI_API_KEY)
        # Convert to internal ChatRequest
        chat_request = ChatRequest(
            session_id=request.session_id,
            user_id=request.user_id,
            message=request.message,
            user_image=request.user_image,
            tweet_id=request.tweet_id
        )

        print(f'session_id: {request.session_id} | user_id: {request.user_id} | message: {request.message}')

        # Process the request
        response = agent.chat(chat_request)
        
        return response
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        return APIResponse(
            success=False,
            error=f"Error processing request"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5555, reload=True) 