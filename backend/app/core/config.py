import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Dict, List, Optional

class Settings(BaseSettings):
    # API Keys
    ANTHROPIC_API_KEY: str = Field(..., env="ANTHROPIC_API_KEY")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    
    # Default LLM configuration
    DEFAULT_PROVIDER: str = Field(default="anthropic", env="DEFAULT_PROVIDER")
    DEFAULT_MODEL: str = Field(default="claude-3-5-sonnet-20240620", env="DEFAULT_MODEL")
    
    # Security settings
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=20, env="RATE_LIMIT_PER_MINUTE")
    
    # CORS configuration
    CORS_ORIGINS: List[str] = ["*"]
    
    # Available LLM models
    AVAILABLE_MODELS: Dict[str, List[str]] = {
        "anthropic": [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-5-sonnet-20240620",
            "claude-3-haiku-20240307"
        ],
        "openai": [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ]
    }
    
    class Config:
        env_file = ".env"

settings = Settings()