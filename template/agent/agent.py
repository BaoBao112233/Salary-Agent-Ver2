import os
import json
import logging
from datetime import datetime
from langchain_google_vertexai import ChatVertexAI
from langchain.tools import StructuredTool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain.agents import AgentExecutor
from template.configs.environments import get_environment_variables
from template.schemas.model import ChatRequest, ChatResponse
from template.agent.histories import RedisSupportChatHistory
from template.agent.prompts import SYSTEM_PROMPT
from template.agent.tools.caculator import add, subtract, multiply, divide, mod
from template.agent.tools.search import (
    google_search
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

env = get_environment_variables()

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env.GOOGLE_APPLICATION_CREDENTIALS

memories = {}

default_tools = [
    StructuredTool.from_function(
        func=google_search,
        name="google_search",
        description="Search Google for information. Input is required. Input should be a single string strictly in the following JSON format: {query: <query: string>}. Example: {\"query\": \"latest news on Bitcoin\"}. Input query is user require. Output is a string of search results.",
    ),
    StructuredTool.from_function(
        func=add,
        name="add",
        description="Add two numbers. Input should be a JSON object with 'a' and 'b' fields. Example: {\"a\": 5, \"b\": 10}. Output is the sum of a and b.",
    ),
    StructuredTool.from_function(
        func=subtract,
        name="subtract",
        description="Subtract two numbers. Input should be a JSON object with 'a' and 'b' fields. Example: {\"a\": 10, \"b\": 5}. Output is the difference of a and b.",
    ),
    StructuredTool.from_function(
        func=multiply,
        name="multiply",
        description="Multiply two numbers. Input should be a JSON object with 'a' and 'b' fields. Example: {\"a\": 5, \"b\": 10}. Output is the product of a and b.",
    ),
    StructuredTool.from_function(
        func=divide,
        name="divide",
        description="Divide two numbers. Input should be a JSON object with 'a' and 'b' fields. Example: {\"a\": 10, \"b\": 5}. Output is the quotient of a and b.",
    ),
    StructuredTool.from_function(
        func=mod,
        name="mod",
        description="Calculate the modulus of two numbers. Input should be a JSON object with 'a' and 'b' fields. Example: {\"a\": 10, \"b\": 5}. Output is the modulus of a and b.",
    ),
]

def _init_memories(session_id: int , user_id: int):
    try:

        memory = _get_memory(session_id, user_id)
        memory.clear()
        key = str(session_id) + "_" + str(user_id)

        os.makedirs("memories", exist_ok=True)
        file_path = f"memories/chat_history_{key}.json"
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted old file: {file_path}")

        with open(file_path, "w") as f:
            json.dump([{
                "type": "human",
                "data": {
                    "content": f"your user id is {user_id}",
                    "additional_kwargs": {},
                    "response_metadata": {},
                    "type": "human",
                    "name": None,
                    "id": None,
                    "example": False
                }
            }], f)
            logger.info(f"Created new file: {file_path}")


    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        import traceback
        traceback.print_exc()
        return f"Error processing file: {str(e)}"
    

def _get_memory(session_id: int, user_id: int) -> RedisSupportChatHistory:
    """Get or create memory for a session using unified Redis/File storage"""
    session_key = str(session_id) + "_" + str(user_id)
    if session_key not in memories:
        # Create directory if it doesn't exist (for file fallback)
        os.makedirs("memories", exist_ok=True)
        
        # Use Redis storage by default with file fallback
        memories[session_key] = RedisSupportChatHistory(
            session_id=str(session_id),
            user_id=str(user_id),
            storage="redis",  # Will auto-fallback to "file" if Redis unavailable
            ttl=env.TTL_SECONDS
        )
        
        # Initialize with user ID if it's a new session
        if not memories[session_key].exists_session():
            memories[session_key].add_ai_message(f"your user id is {user_id}")

    return memories[session_key]


class Agent:
    """
    XSol agent that handles multiple operations:
    - Create token on Jupiter or Pumpfun
    - Buy/sell/send tokens
    - General crypto questions
    """
    
    def __init__(self, 
                 api_key: str = None, 
                 model: str = None, 
                 prompt: str = SYSTEM_PROMPT, 
                 temperature: float = 0.2,
                 tools: list = default_tools):
        # Initialize LLM with Vertex AI (Gemini)
        self.llm = ChatVertexAI(
            model=model or env.MODEL_NAME,
            project=env.GOOGLE_CLOUD_PROJECT,
            location=env.GOOGLE_CLOUD_LOCATION,
            temperature=temperature
        )

        # Define tools
        self.tools = tools
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ('human',
             [
                {
                    "type": "text",
                    "text": "{input}"
                },
            ]),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        self.prompt_with_image = ChatPromptTemplate.from_messages([
            ("system", prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ('human',
             [
                {
                    "type": "text",
                    "text": "{input}"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "{image_url}"
                    }
                }
            ]),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Default session and memory
        self.default_session_id = 0

    def chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request and return a response"""
        try:
            # Get memory for this session
            temp_memory = _get_memory(
                session_id=request.session_id,
                user_id=request.user_id
            )
            
            # Add the user message to history with image if present
            if request.user_image:                # We'll handle this manually since we need to format it correctly
                temp_memory.add_user_message(request.message, request.user_image)
                prompt = self.prompt_with_image
            else:
                prompt = self.prompt

            # Create the agent
            self.agent = OpenAIFunctionsAgent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
            
            # Create the agent executor
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5
            )

            # Set up runnable with chat history
            agent_with_chat_history = RunnableWithMessageHistory(
                self.agent_executor,
                lambda session_id: temp_memory,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="output"
            )
            
            # Prepare input data
            input_data = {
                "input": request.message,
            }
            
            if request.user_image:
                input_data["image_url"] = request.user_image
                logger.info(f"Added image URL to request: {request.user_image[:30]}...")
            
            print(f'input_data: {input_data}')
            
            # Process the message
            response = agent_with_chat_history.invoke(
                input_data, 
                config={
                    "configurable": {"session_id": request.session_id},
                    "run_name": f"Agent:Session{request.session_id}"
                }
            )
            
            # Extract and process the response
            response_text = response['output']
            
            # If we manually added the user message, we need to manually add the AI response too

            # base_memory.add_ai_message(response_text)

            # Clean response text
            response_text = response_text.replace("**", "")

            return ChatResponse(response=response_text)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return ChatResponse(
                response=f"I encountered an error processing your request. Please try again.",
                error_status="error"
            )
