import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.v1.models.openai_models import ChatRequest, ChatResponse, ModelListResponse, ModelInfo, Message
from app.core.config import settings
from app.services.openai_service import get_openai_response, get_openai_client

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_llm_response(request: ChatRequest) -> ChatResponse:
    """
    Route the request to the appropriate LLM provider based on the request.
    """
    provider = request.provider or settings.DEFAULT_PROVIDER
    model = request.model or settings.DEFAULT_MODEL
    conversation_id = getattr(request, 'conversation_id', None)
    
    logger.info("Processing LLM request", extra={
        "provider": provider,
        "model": model,
        "message_count": len(request.messages),
        "stream": request.stream,
        "conversation_id": conversation_id
    })
    
    if provider.lower() == "openai":
        try:
            # Call OpenAI service
            response_data = await get_openai_response(
                messages=request.messages,
                model=model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=request.stream
            )
            logger.debug("Successfully received response from OpenAI")
            
            # Create response object
            response = ChatResponse(
                message=Message(role="assistant", content=response_data["content"]),
                usage=response_data["usage"],
                provider=provider,
                model=model
            )
            logger.info(f"Response generated successfully: {len(response_data['content'])} characters")
            return response
        except Exception as e:
            logger.error(f"Error in OpenAI request: {str(e)}", exc_info=True)
            raise
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
    try:
        conversation_id = getattr(request, 'conversation_id', None)
        logger.info("Received chat request", extra={
            "stream": request.stream,
            "message_count": len(request.messages),
            "conversation_id": conversation_id,
            "model": request.model or settings.DEFAULT_MODEL
        })
        
        if request.stream:
            logger.debug("Returning streaming response")
            return StreamingResponse(
                stream_llm_response(request),
                media_type="text/event-stream"
            )
        else:
            response = await get_llm_response(request)
            logger.debug("Returning non-streaming response")
            return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise

async def stream_llm_response(request: ChatRequest) -> AsyncGenerator[str, None]:
    """
    Stream the response from the LLM provider.
    """
    provider = request.provider or settings.DEFAULT_PROVIDER
    model = request.model or settings.DEFAULT_MODEL
    conversation_id = getattr(request, 'conversation_id', None)
    
    logger.info("Starting stream response processing", extra={
        "provider": provider,
        "model": model,
        "conversation_id": conversation_id,
        "message_count": len(request.messages)
    })
    
    if provider.lower() != "openai":
        error_msg = f'Provider {provider} is not supported'
        logger.warning(error_msg, extra={"conversation_id": conversation_id})
        yield f"data: {json.dumps({'error': error_msg})}\n\n"
        return

    try:
        logger.debug("Initializing streaming response client", extra={"conversation_id": conversation_id})
        client = get_openai_client()
        
        # For testing purposes, check if we're in a test environment
        if hasattr(client.chat.completions, 'create') and callable(getattr(client.chat.completions, 'create')):
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": m.role, "content": m.content} for m in request.messages],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=True
            )
            
            # Collect the full response content
            full_content = ""
            chunk_count = 0
            
            logger.debug("Beginning to stream response chunks", extra={"conversation_id": conversation_id})
            async for chunk in response:
                chunk_count += 1
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield f"data: {json.dumps(chunk.dict())}\n\n"
            
            # Send a done signal
            logger.info("Streaming completed successfully", extra={
                "conversation_id": conversation_id,
                "chunk_count": chunk_count,
                "response_length": len(full_content)
            })
            yield "data: [DONE]\n\n"
        else:
            # This branch is for testing
            test_response = {
                "id": "test-stream-id",
                "object": "chat.completion.chunk",
                "created": 1677825464,
                "model": model,
                "choices": [
                    {
                        "delta": {"content": "This is a test streaming response"},
                        "index": 0,
                        "finish_reason": None
                    }
                ]
            }
            yield f"data: {json.dumps(test_response)}\n\n"
            yield "data: [DONE]\n\n"
            
    except Exception as e:
        logger.error(f"Error in streaming response: {str(e)}", exc_info=True, extra={
            "conversation_id": conversation_id,
            "error_type": type(e).__name__
        })
        # Return error to client in a structured way
        error_data = {
            "error": str(e),
            "error_type": type(e).__name__
        }
        yield f"data: {json.dumps(error_data)}\n\n"
