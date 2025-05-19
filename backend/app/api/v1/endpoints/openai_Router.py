from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from app.api.v1.models.openai_models import ChatRequest, ChatResponse, ModelListResponse, ModelInfo, Message
from app.core.config import settings
from app.services.openai_service import get_openai_response, get_openai_client
from typing import AsyncGenerator
from pydantic import BaseModel
import json

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

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Send a chat request to the LLM provider.
    Supports both streaming and non-streaming responses.
    """
    if request.stream:
        return StreamingResponse(
            stream_llm_response(request),
            media_type="text/event-stream"
        )
    else:
        response = await get_llm_response(request)
        return response

async def stream_llm_response(request: ChatRequest) -> AsyncGenerator[str, None]:
    """
    Stream the response from the LLM provider.
    """
    provider = request.provider or settings.DEFAULT_PROVIDER
    model = request.model or settings.DEFAULT_MODEL
    
    if provider.lower() != "openai":
        yield f"data: {json.dumps({'error': f'Provider {provider} is not supported'})}\n\n"
        return

    try:
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in request.messages],
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=True
        )
        
        # Collect the full response content
        full_content = ""
        
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                yield f"data: {json.dumps(chunk.dict())}\n\n"
        
        # Send a done signal
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
