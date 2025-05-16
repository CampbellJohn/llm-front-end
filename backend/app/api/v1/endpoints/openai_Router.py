from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.models.openai_models import ChatRequest, ChatResponse, ModelListResponse, ModelInfo, Message
from app.core.config import settings
from app.services.openai_service import get_openai_response
from typing import List, Dict, Any
from pydantic import BaseModel

class DefaultConfigResponse(BaseModel):
    provider: str
    model: str

router = APIRouter()

async def get_llm_response(request: ChatRequest) -> ChatResponse:
    """
    Route the request to the appropriate LLM provider based on the request.
    """
    provider = request.provider or settings.DEFAULT_PROVIDER
    model = request.model or settings.DEFAULT_MODEL
    
    if provider.lower() == "openai":
        # Call OpenAI service
        response_data = await get_openai_response(
            messages=request.messages,
            model=model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=request.stream
        )
        
        # Create response object
        return ChatResponse(
            message=Message(role="assistant", content=response_data["content"]),
            usage=response_data["usage"],
            provider=provider,
            model=model
        )
    else:
        # For now, we only support OpenAI
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{provider}' is not supported"
        )

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a chat request to the LLM provider.
    """
    response = await get_llm_response(request)
    return response

@router.get("/models", response_model=ModelListResponse)
async def list_models():
    """
    List available models.
    """
    # For now, we'll just return a static list of OpenAI models
    # In a production app, you might want to fetch this from the OpenAI API
    models = [
        ModelInfo(id="gpt-3.5-turbo", provider="openai", name="GPT-3.5 Turbo"),
        ModelInfo(id="gpt-4", provider="openai", name="GPT-4"),
        ModelInfo(id="gpt-4-turbo", provider="openai", name="GPT-4 Turbo")
    ]
    
    return ModelListResponse(models=models)

@router.get("/default-config", response_model=DefaultConfigResponse)
async def get_default_config():
    """
    Get the default model and provider configuration.
    """
    return DefaultConfigResponse(
        provider=settings.DEFAULT_PROVIDER,
        model=settings.DEFAULT_MODEL
    )