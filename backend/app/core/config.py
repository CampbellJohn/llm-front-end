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
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_PROVIDER: str = "openai"
    
    # API configuration
    API_PREFIX: str = "/api"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a global settings object
settings = Settings()
