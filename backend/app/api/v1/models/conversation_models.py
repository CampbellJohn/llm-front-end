from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.api.v1.models.openai_models import Message
import uuid
import json

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    model: Optional[str] = None
    provider: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Chat about AI",
                "messages": [
                    {"role": "user", "content": "Tell me about AI"},
                    {"role": "assistant", "content": "AI is a branch of computer science..."}
                ],
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:05:00",
                "model": "gpt-3.5-turbo",
                "provider": "openai"
            }
        }
        
    def model_dump(self) -> Dict[str, Any]:
        """Compatible with both Pydantic v1 and v2"""
        if hasattr(super(), "model_dump"):
            return super().model_dump()
        return self.dict()
        
    def dict(self) -> Dict[str, Any]:
        """Custom dict method for MongoDB compatibility"""
        data = super().dict() if hasattr(super(), "dict") else super().model_dump()
        # Convert datetime objects to ISO format strings for MongoDB compatibility
        if "created_at" in data and isinstance(data["created_at"], datetime):
            data["created_at"] = data["created_at"].isoformat()
        if "updated_at" in data and isinstance(data["updated_at"], datetime):
            data["updated_at"] = data["updated_at"].isoformat()
        return data

class ConversationCreate(BaseModel):
    title: str
    messages: List[Message] = []
    model: Optional[str] = None
    provider: Optional[str] = None

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    messages: Optional[List[Message]] = None
    model: Optional[str] = None
    provider: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    title: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    model: Optional[str] = None
    provider: Optional[str] = None
