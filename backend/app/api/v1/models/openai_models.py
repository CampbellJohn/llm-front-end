from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

class Message(BaseModel):
    role: Literal["user", "assistant", "system"] = "user"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    provider: Optional[Literal["openai"]] = None
    max_tokens: Optional[int] = 8000
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    message: Message
    usage: Optional[Dict[str, Any]] = None
    provider: str
    model: str

class ModelInfo(BaseModel):
    id: str
    provider: str
    name: str

class ModelListResponse(BaseModel):
    models: List[ModelInfo]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None