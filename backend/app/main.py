import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.openai_Router import router as openai_router
from app.api.v1.endpoints.conversation_router import router as conversation_router
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.logging_config import setup_logging, RequestLoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to the database
    logger.info("Starting application...")
    try:
        logger.info("Connecting to MongoDB...")
        await connect_to_mongo()
        logger.info("Successfully connected to MongoDB")
        
        # Log application info
        logger.info("Application startup complete", extra={
            "app_name": app.title,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        })
        
        yield
        
    except Exception as e:
        logger.critical("Application startup failed", exc_info=True, extra={
            "error": str(e),
            "error_type": type(e).__name__
        })
        raise
    finally:
        # Shutdown: close database connection
        logger.info("Shutting down application...")
        try:
            await close_mongo_connection()
            logger.info("Successfully closed MongoDB connection")
        except Exception as e:
            logger.error("Error closing MongoDB connection", exc_info=True, extra={
                "error": str(e),
                "error_type": type(e).__name__
            })
        logger.info("Application shutdown complete")

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Chat API",
    description="API for interacting with various LLM providers",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS.split(",") if settings.CORS_ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connections are now handled by the lifespan context manager above

# Include routers with logging
logger.info("Including routers...")
app.include_router(openai_router, prefix=settings.API_PREFIX)
logger.info(f"Added OpenAI router at {settings.API_PREFIX}")

app.include_router(
    conversation_router, 
    prefix=f"{settings.API_PREFIX}/conversations", 
    tags=["conversations"]
)
logger.info(f"Added Conversations router at {settings.API_PREFIX}/conversations")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to the LLM Chat API. Please see our documentation at /docs.",
        "status": "operational",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    import platform
    from datetime import datetime
    
    # Basic system info (without psutil)
    system_info = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }
    
    logger.info("Health check endpoint called", extra={"system_info": system_info})
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "system": system_info
    }

# The app is run using the run.py script in the backend directory
