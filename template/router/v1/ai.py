from fastapi import APIRouter, BackgroundTasks
from cachetools import TTLCache
from template.agent.agent import Agent
from template.schemas.model import ChatRequest, ChatResponse, ChatRequestAPI, APIResponse
import logging
from template.agent.agent import Agent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


RouterAI = APIRouter(
    prefix="/ai", tags=["AI Chat Default"]
)

cache = TTLCache(maxsize=500, ttl=300)


@RouterAI.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequestAPI, background_tasks: BackgroundTasks):
    """Process a chat message and return a response"""
    try:
        agent = Agent()
        # Convert to internal ChatRequest
        chat_request = ChatRequest(
            session_id=request.session_id,
            user_id=request.user_id,
            message=request.message,
            user_image=request.user_image,
        )

        print(f'session_id: {request.session_id} | user_id: {request.user_id} | message: {request.message}')

        # Process the request
        response = agent.chat(chat_request)
        
        return response
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        return ChatResponse(
            response=f"Error processing request: {str(e)}",
            error_status="error"
        )
