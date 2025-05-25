from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging
import uuid
from app.core.database import get_database
from app.api.v1.models.conversation_models import Conversation, ConversationCreate, ConversationUpdate
from pymongo.collection import Collection

# Configure logger
logger = logging.getLogger(__name__)


COLLECTION_NAME = "conversations"

def get_collection() -> Collection:
    """Get the conversations collection"""
    try:
        logger.debug("Accessing MongoDB collection", extra={"collection": COLLECTION_NAME})
        db = get_database()
        collection = db[COLLECTION_NAME]
        logger.debug("Successfully accessed collection", extra={"collection": COLLECTION_NAME})
        return collection
    except Exception as e:
        logger.error("Failed to access collection", extra={
            "collection": COLLECTION_NAME,
            "error": str(e)
        }, exc_info=True)
        raise

# Helper function to convert Pydantic models to JSON-compatible dict
def model_to_dict(obj) -> Dict[str, Any]:
    """Convert Pydantic model to a MongoDB-compatible dict"""
    try:
        if hasattr(obj, "model_dump"):
            # For Pydantic v2
            return obj.model_dump()
        elif hasattr(obj, "dict"):
            # For Pydantic v1
            return obj.dict()
        # Fallback for non-Pydantic objects
        return dict(obj)
    except Exception as e:
        logger.error("Failed to convert model to dict", extra={"error": str(e)}, exc_info=True)
        raise

async def create_conversation(conversation: ConversationCreate) -> Conversation:
    """Create a new conversation"""
    log_context = {"operation": "create_conversation", "conversation_title": conversation.title}
    logger.info("Creating new conversation", extra=log_context)
    
    try:
        # Log input data (safely)
        logger.debug("Input data for conversation", extra={
            "title": conversation.title,
            "model": conversation.model,
            "provider": conversation.provider,
            "message_count": len(conversation.messages) if conversation.messages else 0,
            **log_context
        })
        
        new_conversation = Conversation(
            title=conversation.title,
            messages=conversation.messages,
            model=conversation.model,
            provider=conversation.provider
        )
        
        # Convert to dict in a way that's compatible with both Pydantic v1 and v2
        conversation_dict = model_to_dict(new_conversation)
        
        # Ensure MongoDB can serialize all values
        for key, value in conversation_dict.items():
            if isinstance(value, datetime):
                conversation_dict[key] = value.isoformat()
        
        logger.debug("Prepared conversation document for insertion", extra=log_context)
        
        # Log the insert operation
        logger.debug("Inserting conversation into database", extra=log_context)
        result = await get_collection().insert_one(conversation_dict)
        
        logger.info("Successfully created conversation", extra={
            "conversation_id": str(result.inserted_id), 
            **log_context
        })
        
        return new_conversation
    except Exception as e:
        logger.error("Failed to create conversation", extra={"error": str(e), **log_context}, exc_info=True)
        raise

async def get_conversation(conversation_id: str) -> Optional[Conversation]:
    """Get a conversation by ID"""
    log_context = {"operation": "get_conversation", "conversation_id": conversation_id}
    logger.debug("Looking for conversation", extra=log_context)
    
    try:
        if not conversation_id:
            logger.warning("Empty conversation ID provided", extra=log_context)
            return None
            
        conversation = await get_collection().find_one({"id": conversation_id})
        if conversation:
            logger.debug("Successfully retrieved conversation", extra=log_context)
            return Conversation(**conversation)
            
        logger.info("Conversation not found", extra=log_context)
        return None
    except Exception as e:
        logger.error("Error retrieving conversation", extra={"error": str(e), **log_context}, exc_info=True)
        raise

async def list_conversations(skip: int = 0, limit: int = 10) -> List[Conversation]:
    """List all conversations with pagination"""
    log_context = {
        "operation": "list_conversations",
        "skip": skip,
        "limit": limit
    }
    logger.info("Listing conversations", extra=log_context)
    
    try:
        collection = get_collection()
        cursor = collection.find().sort("updated_at", -1).skip(skip).limit(limit)
        conversations = await cursor.to_list(length=limit)
        
        logger.debug("Retrieved conversations", extra={
            "count": len(conversations),
            **log_context
        })
        return [Conversation(**conv) for conv in conversations]
    except Exception as e:
        logger.error("Error listing conversations", extra={"error": str(e), **log_context}, exc_info=True)
        raise

async def update_conversation(conversation_id: str, conversation_update: ConversationUpdate) -> Optional[Conversation]:
    """Update a conversation"""
    log_context = {"operation": "update_conversation", "conversation_id": conversation_id}
    logger.info("Updating conversation", extra=log_context)
    
    try:
        # Get the current conversation
        logger.debug("Retrieving current conversation data", extra=log_context)
        current = await get_conversation(conversation_id)
        if not current:
            logger.warning("Cannot update - conversation not found", extra=log_context)
            return None
        
        # Prepare update data
        update_data = model_to_dict(conversation_update)
        update_data = {k: v for k, v in update_data.items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        logger.debug("Update data prepared", extra={
            "updates": str(update_data),
            **log_context
        })
        
        # Update in database
        logger.debug("Executing database update", extra=log_context)
        result = await get_collection().update_one(
            {"id": conversation_id},
            {"$set": update_data}
        )
        
        logger.info("Update result", extra={
            "matched": result.matched_count, 
            "modified": result.modified_count,
            **log_context
        })
        
        if result.modified_count:
            logger.debug("Retrieving updated conversation", extra=log_context)
            return await get_conversation(conversation_id)
            
        logger.debug("No modifications made to conversation", extra=log_context)
        return current
    except Exception as e:
        logger.error("Error updating conversation", extra={"error": str(e), **log_context}, exc_info=True)
        raise

async def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation"""
    log_context = {"operation": "delete_conversation", "conversation_id": conversation_id}
    logger.info("Deleting conversation", extra=log_context)
    
    try:
        if not conversation_id:
            logger.warning("Empty conversation ID provided for deletion", extra=log_context)
            return False
            
        result = await get_collection().delete_one({"id": conversation_id})
        was_deleted = result.deleted_count > 0
        
        if was_deleted:
            logger.info("Successfully deleted conversation", extra=log_context)
        else:
            logger.info("No conversation found to delete", extra=log_context)
            
        return was_deleted
    except Exception as e:
        logger.error("Error deleting conversation", extra={"error": str(e), **log_context}, exc_info=True)
        raise

async def add_message_to_conversation(conversation_id: str, message: dict) -> Optional[Conversation]:
    """Add a message to a conversation"""
    log_context = {
        "operation": "add_message_to_conversation",
        "conversation_id": conversation_id,
        "message_role": message.get("role", "unknown"),
        "message_length": len(message.get("content", "")) if message else 0
    }
    logger.info("Adding message to conversation", extra=log_context)
    
    try:
        if not conversation_id:
            logger.warning("Empty conversation ID provided", extra=log_context)
            return None
            
        if not message or not isinstance(message, dict):
            logger.error("Invalid message format", extra=log_context)
            return None
            
        logger.debug("Executing database update to add message", extra=log_context)
        result = await get_collection().update_one(
            {"id": conversation_id},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info("Message add result", extra={
            "matched": result.matched_count, 
            "modified": result.modified_count,
            **log_context
        })
        
        if result.modified_count:
            logger.debug("Retrieving updated conversation with new message", extra=log_context)
            return await get_conversation(conversation_id)
            
        logger.warning("No conversation modified when adding message", extra=log_context)
        return None
    except Exception as e:
        logger.error("Error adding message to conversation", extra={
            "error": str(e),
            **log_context
        }, exc_info=True)
        raise
