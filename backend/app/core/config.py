from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://admin:password@mongodb:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "llm_chat_db")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a global settings object
settings = Settings()
