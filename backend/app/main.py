from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.openai_Router import router as openai_router
from app.api.v1.endpoints.conversation_router import router as conversation_router
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection

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

# Database connection events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Include routers
app.include_router(openai_router, prefix=settings.API_PREFIX)
app.include_router(conversation_router, prefix=f"{settings.API_PREFIX}/conversations", tags=["conversations"])

@app.get("/")
async def root():
    return {"message": "Welcome to the LLM Chat API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# The app is run using the run.py script in the backend directory
