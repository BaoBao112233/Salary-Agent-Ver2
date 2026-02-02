import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from template.configs.environments import env
from template.router.v1.ai import RouterAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the FastAPI app
app = FastAPI(
    title=env.APP_NAME,
    description=env.APP_DESC,
    version=env.API_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include API routers
app.include_router(RouterAI)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5555, reload=True) 