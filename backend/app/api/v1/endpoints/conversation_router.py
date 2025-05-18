from fastapi import APIRouter, HTTPException, status, Query, Request
from typing import List, Optional
import logging
import traceback
from app.api.v1.models.conversation_models import Conversation, ConversationCreate, ConversationUpdate, ConversationResponse
from app.services.conversation_service import (
    create_conversation, 
    get_conversation, 
    list_conversations, 
    update_conversation, 
    delete_conversation,
    add_message_to_conversation
)
from app.api.v1.models.openai_models import Message

router = APIRouter()

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_conversation(conversation: ConversationCreate, request: Request):
    """
    Create a new conversation
    """
    try:
        print(f"Received request to create conversation: {conversation.title}")
        result = await create_conversation(conversation)
        print(f"Successfully created conversation with ID: {result.id}")
        return result
    except Exception as e:
        error_msg = f"Error creating conversation: {str(e)}"
        print(error_msg)
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@router.get("/", response_model=List[ConversationResponse])
async def list_all_conversations(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    """
    List all conversations with pagination
    """
    conversations = await list_conversations(skip=skip, limit=limit)
    return conversations

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_by_id(conversation_id: str):
    """
    Get a specific conversation by ID
    """
    conversation = await get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    return conversation

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation_by_id(conversation_id: str, conversation_update: ConversationUpdate):
    """
    Update a conversation by ID
    """
    updated_conversation = await update_conversation(conversation_id, conversation_update)
    if not updated_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    return updated_conversation

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_by_id(conversation_id: str):
    """
    Delete a conversation by ID
    """
    deleted = await delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    return None

@router.post("/{conversation_id}/messages", response_model=ConversationResponse)
async def add_message(conversation_id: str, message: Message):
    """
    Add a message to an existing conversation
    """
    conversation = await add_message_to_conversation(conversation_id, message.dict())
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    return conversation
