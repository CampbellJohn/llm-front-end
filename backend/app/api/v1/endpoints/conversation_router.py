from fastapi import APIRouter, HTTPException, status, Query, Request, Depends
from typing import List, Dict, Any, Optional
import logging
import uuid
from datetime import datetime
from pydantic import BaseModel

from app.api.v1.models.conversation_models import ConversationCreate, ConversationUpdate, ConversationResponse
from app.services.conversation_service import (
    create_conversation, 
    get_conversation, 
    list_conversations, 
    update_conversation, 
    delete_conversation,
    add_message_to_conversation
)
from app.api.v1.models.openai_models import Message

# Set up logger
logger = logging.getLogger(__name__)

# Dependencies
def get_request_id() -> str:
    """Generate a unique request ID for tracing."""
    return f"conv_req_{uuid.uuid4().hex}"

class LogContext(BaseModel):
    """Context for request logging."""
    request_id: str = Depends(get_request_id)
    method: str
    path: str
    client: Optional[str] = None
    path_params: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None

async def log_request(
    context: LogContext,
    request: Request,
    **extra: Any
) -> LogContext:
    """Log information about the incoming request."""
    context.client = request.client.host if request.client else "unknown"
    
    logger.info(
        "Request received",
        extra={
            "request_id": context.request_id,
            "endpoint": f"{context.method} {context.path}",
            "client": context.client,
            "path_params": context.path_params or {},
            "query_params": dict(context.query_params) if context.query_params else {},
            "body": context.body or {},
            **extra
        }
    )
    return context

async def log_response(
    context: LogContext,
    status_code: int,
    response_data: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None
) -> None:
    """Log information about the response being sent."""
    log_data = {
        "request_id": context.request_id,
        "endpoint": f"{context.method} {context.path}",
        "status_code": status_code,
        "response_data": response_data or {}
    }
    
    if error:
        log_data.update({
            "error": str(error),
            "error_type": error.__class__.__name__
        })
        logger.error("Request completed with error", extra=log_data, exc_info=True)
    else:
        logger.info("Request completed successfully", extra=log_data)

router = APIRouter()

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_conversation(
    conversation: ConversationCreate, 
    request: Request,
    context: LogContext = Depends(lambda: LogContext(method="POST", path="/"))
):
    """
    Create a new conversation
    """
    try:
        # Log the incoming request
        context = await log_request(
            context=context,
            request=request,
            body={"title": conversation.title, "message_count": len(conversation.messages) if conversation.messages else 0}
        )
        
        logger.debug("Creating new conversation", extra={
            "request_id": context.request_id,
            "title": conversation.title,
            "message_count": len(conversation.messages) if conversation.messages else 0
        })
        
        # Process the request
        result = await create_conversation(conversation)
        
        # Log successful creation
        logger.info("Successfully created conversation", extra={
            "request_id": context.request_id,
            "conversation_id": str(result.id),
            "title": result.title
        })
        
        return result
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions as they are already properly formatted
        await log_response(
            context=context,
            status_code=http_exc.status_code,
            error=http_exc
        )
        raise
        
    except Exception as e:
        error_msg = f"Error creating conversation: {str(e)}"
        logger.error(error_msg, extra={"request_id": context.request_id}, exc_info=True)
        
        await log_response(
            context=context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=e
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@router.get("/", response_model=List[ConversationResponse])
async def list_all_conversations(
    skip: int = Query(0, ge=0), 
    limit: int = Query(10, ge=1, le=100),
    request: Request = None,
    context: LogContext = Depends(lambda: LogContext(method="GET", path="/"))
):
    """
    List all conversations with pagination
    """
    try:
        # Log the incoming request
        context = await log_request(
            context=context,
            request=request,
            query_params={"skip": skip, "limit": limit}
        )
        
        logger.debug("Listing conversations", extra={
            "request_id": context.request_id,
            "skip": skip,
            "limit": limit
        })
        
        # Process the request
        conversations = await list_conversations(skip=skip, limit=limit)
        
        # Log successful response
        logger.info("Successfully listed conversations", extra={
            "request_id": context.request_id,
            "count": len(conversations)
        })
        
        return conversations
        
    except Exception as e:
        error_msg = f"Error listing conversations: {str(e)}"
        logger.error(error_msg, extra={"request_id": context.request_id}, exc_info=True)
        
        await log_response(
            context=context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=e
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_by_id(
    conversation_id: str,
    request: Request = None,
    context: LogContext = Depends(lambda: LogContext(method="GET", path="/{conversation_id}"))
):
    """
    Get a specific conversation by ID
    """
    try:
        # Log the incoming request
        context = await log_request(
            context=context,
            request=request,
            path_params={"conversation_id": conversation_id}
        )
        
        logger.debug("Fetching conversation", extra={
            "request_id": context.request_id,
            "conversation_id": conversation_id
        })
        
        # Process the request
        conversation = await get_conversation(conversation_id)
        
        if not conversation:
            error_msg = f"Conversation with ID {conversation_id} not found"
            logger.warning(error_msg, extra={"request_id": context.request_id})
            
            await log_response(
                context=context,
                status_code=status.HTTP_404_NOT_FOUND,
                error=ValueError(error_msg)
            )
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        
        # Log successful response
        logger.info("Successfully retrieved conversation", extra={
            "request_id": context.request_id,
            "conversation_id": conversation_id
        })
        
        return conversation
        
    except HTTPException as http_exc:
        if http_exc.status_code != 404:  # Already logged 404 above
            await log_response(
                context=context,
                status_code=http_exc.status_code,
                error=http_exc
            )
        raise
        
    except Exception as e:
        error_msg = f"Error retrieving conversation: {str(e)}"
        logger.error(error_msg, extra={"request_id": context.request_id}, exc_info=True)
        
        await log_response(
            context=context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=e
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation_by_id(
    conversation_id: str, 
    conversation_update: ConversationUpdate,
    request: Request = None,
    context: LogContext = Depends(lambda: LogContext(method="PUT", path="/{conversation_id}"))
):
    """
    Update a conversation by ID
    """
    try:
        # Log the incoming request
        update_fields = {k: v for k, v in conversation_update.dict().items() if v is not None}
        context = await log_request(
            context=context,
            request=request,
            path_params={"conversation_id": conversation_id},
            body=update_fields
        )
        
        logger.debug("Updating conversation", extra={
            "request_id": context.request_id,
            "conversation_id": conversation_id,
            "update_fields": list(update_fields.keys())
        })
        
        # Process the request
        updated_conversation = await update_conversation(conversation_id, conversation_update)
        
        if not updated_conversation:
            error_msg = f"Conversation with ID {conversation_id} not found"
            logger.warning(error_msg, extra={"request_id": context.request_id})
            
            await log_response(
                context=context,
                status_code=status.HTTP_404_NOT_FOUND,
                error=ValueError(error_msg)
            )
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        
        # Log successful update
        logger.info("Successfully updated conversation", extra={
            "request_id": context.request_id,
            "conversation_id": conversation_id,
            "updated_fields": list(update_fields.keys())
        })
        
        return updated_conversation
        
    except HTTPException as http_exc:
        if http_exc.status_code != 404:  # Already logged 404 above
            await log_response(
                context=context,
                status_code=http_exc.status_code,
                error=http_exc
            )
        raise
        
    except Exception as e:
        error_msg = f"Error updating conversation: {str(e)}"
        logger.error(error_msg, extra={"request_id": context.request_id}, exc_info=True)
        
        await log_response(
            context=context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=e
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_by_id(
    conversation_id: str,
    request: Request = None,
    context: LogContext = Depends(lambda: LogContext(method="DELETE", path="/{conversation_id}"))
):
    """
    Delete a conversation by ID
    """
    try:
        # Log the incoming request
        context = await log_request(
            context=context,
            request=request,
            path_params={"conversation_id": conversation_id}
        )
        
        logger.debug("Deleting conversation", extra={
            "request_id": context.request_id,
            "conversation_id": conversation_id
        })
        
        # Process the request
        deleted = await delete_conversation(conversation_id)
        
        if not deleted:
            error_msg = f"Conversation with ID {conversation_id} not found"
            logger.warning(error_msg, extra={"request_id": context.request_id})
            
            await log_response(
                context=context,
                status_code=status.HTTP_404_NOT_FOUND,
                error=ValueError(error_msg)
            )
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        
        # Log successful deletion
        logger.info("Successfully deleted conversation", extra={
            "request_id": context.request_id,
            "conversation_id": conversation_id
        })
        
        return None
        
    except HTTPException as http_exc:
        if http_exc.status_code != 404:  # Already logged 404 above
            await log_response(
                context=context,
                status_code=http_exc.status_code,
                error=http_exc
            )
        raise
        
    except Exception as e:
        error_msg = f"Error deleting conversation: {str(e)}"
        logger.error(error_msg, extra={"request_id": context.request_id}, exc_info=True)
        
        await log_response(
            context=context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=e
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@router.post("/{conversation_id}/messages", response_model=ConversationResponse)
async def add_message(
    conversation_id: str, 
    message: Message,
    request: Request = None,
    context: LogContext = Depends(lambda: LogContext(method="POST", path="/{conversation_id}/messages"))
):
    """
    Add a message to an existing conversation
    """
    try:
        # Log the incoming request
        message_data = message.dict()
        context = await log_request(
            context=context,
            request=request,
            path_params={"conversation_id": conversation_id},
            body={"role": message.role, "content_length": len(message.content) if message.content else 0}
        )
        
        logger.debug("Adding message to conversation", extra={
            "request_id": context.request_id,
            "conversation_id": conversation_id,
            "message_role": message.role,
            "content_length": len(message.content) if message.content else 0
        })
        
        # Process the request
        conversation = await add_message_to_conversation(conversation_id, message_data)
        
        if not conversation:
            error_msg = f"Conversation with ID {conversation_id} not found"
            logger.warning(error_msg, extra={"request_id": context.request_id})
            
            await log_response(
                context=context,
                status_code=status.HTTP_404_NOT_FOUND,
                error=ValueError(error_msg)
            )
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        
        # Log successful message addition
        logger.info("Successfully added message to conversation", extra={
            "request_id": context.request_id,
            "conversation_id": conversation_id,
            "message_count": len(conversation.messages) if hasattr(conversation, 'messages') else 0
        })
        
        return conversation
        
    except HTTPException as http_exc:
        if http_exc.status_code != 404:  # Already logged 404 above
            await log_response(
                context=context,
                status_code=http_exc.status_code,
                error=http_exc
            )
        raise
        
    except Exception as e:
        error_msg = f"Error adding message to conversation: {str(e)}"
        logger.error(error_msg, extra={"request_id": context.request_id}, exc_info=True)
        
        await log_response(
            context=context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=e
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
