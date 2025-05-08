from fastapi import APIRouter, Depends, HTTPException, status
from app.api.models import ChatRequest, ChatResponse, ModelListResponse, ModelInfo
from app.services.llm_service import get_llm_response
from app.core.config import settings
from typing import List

router = APIRouter()

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
    Get a list of available models from all providers.
    """
    models = []
    
    # Add Anthropic models
    for model_id in settings.AVAILABLE_MODELS["anthropic"]:
        models.append(
            ModelInfo(
                id=model_id,
                provider="anthropic",
                name=model_id
            )
        )
    
    # Add OpenAI models
    for model_id in settings.AVAILABLE_MODELS["openai"]:
        models.append(
            ModelInfo(
                id=model_id,
                provider="openai",
                name=model_id
            )
        )
    
    return {"models": models}

@router.get("/providers")
async def list_providers():
    """
    Get a list of available LLM providers.
    """
    return {"providers": list(settings.AVAILABLE_MODELS.keys())}

@router.get("/default-config")
async def get_default_config():
    """
    Get the default LLM configuration.
    """
    return {
        "provider": settings.DEFAULT_PROVIDER,
        "model": settings.DEFAULT_MODEL
    }