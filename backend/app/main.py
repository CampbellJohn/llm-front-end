from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.openai_Router import router as openai_router
from app.api.v1.endpoints.conversation_router import router as conversation_router
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to the database
    await connect_to_mongo()
    yield
    # Shutdown: close database connection
    await close_mongo_connection()

app = FastAPI(
    title="LLM Chat API",
    description="API for interacting with various LLM providers",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connections are now handled by the lifespan context manager above

# Include routers
app.include_router(openai_router, prefix=settings.API_PREFIX)
app.include_router(conversation_router, prefix=f"{settings.API_PREFIX}/conversations", tags=["conversations"])

#@app.get("/")
#async def root():
#    return {"message": "Welcome to the LLM Chat API. Please see our documentation at /docs."}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# The app is run using the run.py script in the backend directory
