from pydantic_settings import BaseSettings
import os
import logging
from dotenv import load_dotenv

# Set up logger
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
logger.debug("Environment variables loaded from .env file")

class Settings(BaseSettings):
    """
    Application settings.
    """
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Default model settings
    DEFAULT_MODEL: str = "gpt-4o-mini"
    DEFAULT_PROVIDER: str = "openai"
    
    # API configuration
    API_PREFIX: str = "/api"
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    if not MONGODB_URL:
        raise ValueError("MONGODB_URL environment variable is not set")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "llm_chat_db")
    
    # Application settings
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    CORS_ALLOWED_ORIGINS: str = os.getenv("CORS_ALLOWED_ORIGINS")
    if not CORS_ALLOWED_ORIGINS:
        raise ValueError("CORS_ALLOWED_ORIGINS environment variable is not set")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a global settings object
settings = Settings()

# Log configuration info (without sensitive data)
logger.info(f"Application initialized with environment: {settings.ENVIRONMENT}")
logger.info(f"Using MongoDB database: {settings.MONGODB_DB_NAME}")
logger.info(f"Using default LLM model: {settings.DEFAULT_MODEL} from {settings.DEFAULT_PROVIDER}")

# Check if API key is set
if not settings.OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY is not set in environment variables")
