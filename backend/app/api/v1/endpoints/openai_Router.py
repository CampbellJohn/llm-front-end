from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.api.v1.models.openai_models import ChatRequest, ChatResponse, ModelListResponse, ModelInfo
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