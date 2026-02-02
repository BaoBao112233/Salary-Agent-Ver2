from fastapi import APIRouter, Depends
from cachetools import TTLCache
from xsol.agent.agent import XSolAgent
from xsol.schemas.model import ChatRequest, ChatResponse


Router = APIRouter(
    prefix="/ai", tags=["Trading"]
)

cache = TTLCache(maxsize=500, ttl=300)
@Router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, agent: XSolAgent = Depends()) -> ChatResponse:
    response = agent.chat(request)
    return response