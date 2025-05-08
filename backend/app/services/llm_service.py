from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from app.api.models import Message, ChatRequest
from app.core.config import settings
from app.services.anthropic_service import get_anthropic_response
from app.services.openai_service import get_openai_response

async def get_llm_response(request: ChatRequest) -> Dict[str, Any]:
    """
    Route the request to the appropriate LLM provider and return the response.
    """
    # Set default provider if not specified
    provider = request.provider or settings.DEFAULT_PROVIDER
    
    # Set default model if not specified
    if not request.model:
        if provider == "anthropic":
            model = settings.DEFAULT_MODEL
        elif provider == "openai":
            model = "gpt-4"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider: {provider}"
            )
    else:
        model = request.model
    
    # Validate that the model is valid for the provider
    if model not in settings.AVAILABLE_MODELS.get(provider, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model {model} is not available for provider {provider}"
        )

    try:
        # Route to the appropriate provider
        if provider == "anthropic":
            response = await get_anthropic_response(
                messages=request.messages,
                model=model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=request.stream
            )
        elif provider == "openai":
            response = await get_openai_response(
                messages=request.messages,
                model=model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=request.stream
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {provider}"
            )
            
        return {
            "message": Message(role="assistant", content=response["content"]),
            "usage": response.get("usage"),
            "provider": provider,
            "model": model
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )