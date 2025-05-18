from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging
from app.core.database import get_database
from app.api.v1.models.conversation_models import Conversation, ConversationCreate, ConversationUpdate
from pymongo.collection import Collection

COLLECTION_NAME = "conversations"

def get_collection() -> Collection:
    """Get the conversations collection"""
    try:
        return get_database()[COLLECTION_NAME]
    except Exception as e:
        logging.error(f"Error getting collection: {str(e)}")
        raise

# Helper function to convert Pydantic models to JSON-compatible dict
def model_to_dict(obj) -> Dict[str, Any]:
    """Convert Pydantic model to a MongoDB-compatible dict"""
    if hasattr(obj, "model_dump"):
        # For Pydantic v2
        return obj.model_dump()
    elif hasattr(obj, "dict"):
        # For Pydantic v1
        return obj.dict()
    else:
        # Fallback
        return dict(obj)

async def create_conversation(conversation: ConversationCreate) -> Conversation:
    """Create a new conversation"""
    try:
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
        
        print(f"Inserting conversation: {json.dumps(conversation_dict, default=str)}")
        result = await get_collection().insert_one(conversation_dict)
        print(f"Insert result: {result.inserted_id}")
        
        return new_conversation
    except Exception as e:
        print(f"Error creating conversation: {str(e)}")
        logging.error(f"Error creating conversation: {str(e)}")
        raise

async def get_conversation(conversation_id: str) -> Optional[Conversation]:
    """Get a conversation by ID"""
    try:
        conversation = await get_collection().find_one({"id": conversation_id})
        if conversation:
            return Conversation(**conversation)
        return None
    except Exception as e:
        logging.error(f"Error getting conversation: {str(e)}")
        raise

async def list_conversations(skip: int = 0, limit: int = 10) -> List[Conversation]:
    """List all conversations with pagination"""
    try:
        cursor = get_collection().find().sort("updated_at", -1).skip(skip).limit(limit)
        conversations = await cursor.to_list(length=limit)
        return [Conversation(**conv) for conv in conversations]
    except Exception as e:
        logging.error(f"Error listing conversations: {str(e)}")
        raise

async def update_conversation(conversation_id: str, conversation_update: ConversationUpdate) -> Optional[Conversation]:
    """Update a conversation"""
    try:
        # Get the current conversation
        current = await get_conversation(conversation_id)
        if not current:
            return None
        
        # Update only provided fields
        update_data = model_to_dict(conversation_update)
        update_data = {k: v for k, v in update_data.items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Update in database
        result = await get_collection().update_one(
            {"id": conversation_id},
            {"$set": update_data}
        )
        
        if result.modified_count:
            return await get_conversation(conversation_id)
        return current
    except Exception as e:
        logging.error(f"Error updating conversation: {str(e)}")
        raise

async def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation"""
    try:
        result = await get_collection().delete_one({"id": conversation_id})
        return result.deleted_count > 0
    except Exception as e:
        logging.error(f"Error deleting conversation: {str(e)}")
        raise

async def add_message_to_conversation(conversation_id: str, message: dict) -> Optional[Conversation]:
    """Add a message to a conversation"""
    try:
        result = await get_collection().update_one(
            {"id": conversation_id},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count:
            return await get_conversation(conversation_id)
        return None
    except Exception as e:
        logging.error(f"Error adding message to conversation: {str(e)}")
        raise
