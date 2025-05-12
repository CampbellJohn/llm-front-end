from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.openai_Router import router as api_router
from app.core.config import settings

app = FastAPI(
    title="LLM Chat API",
    description="API for interacting with various LLM providers",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {"message": "Welcome to the LLM Chat API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# The app is run using the run.py script in the backend directory
