"""
Tests for the conversation service.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.services.conversation_service import (
    get_collection,
    create_conversation,
    get_conversation,
    list_conversations,
    update_conversation,
    delete_conversation,
    add_message_to_conversation
)
from app.api.v1.models.conversation_models import (
    Conversation,
    ConversationCreate,
    ConversationUpdate
)

# Fixtures
@pytest.fixture
def mock_collection():
    return MagicMock()

@pytest.fixture
def sample_conversation_data():
    return {
        "id": "test_id_123",
        "title": "Test Conversation",
        "messages": [
            {"role": "user", "content": "Hello", "timestamp": "2023-01-01T00:00:00Z"}
        ],
        "model": "gpt-3.5-turbo",
        "provider": "openai",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_conversation_create():
    return ConversationCreate(
        title="New Conversation",
        messages=[{"role": "user", "content": "Hello"}],
        model="gpt-3.5-turbo",
        provider="openai"
    )

# Tests
@pytest.mark.asyncio
async def test_get_collection(mock_collection):
    """Test that get_collection returns the correct collection."""
    # Mock the database module to avoid the "connection not established" error
    with patch('app.services.conversation_service.get_database') as mock_db:
        mock_db.return_value = {"conversations": mock_collection}
        collection = get_collection()
        assert collection == mock_collection

@pytest.mark.asyncio
async def test_create_conversation(mock_collection, sample_conversation_create):
    """Test creating a new conversation."""
    with patch('app.services.conversation_service.get_collection', return_value=mock_collection):
        # Mock the insert_one method
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="test_id_123"))
        
        # Call the function
        result = await create_conversation(sample_conversation_create)
        
        # Verify the result
        assert result is not None
        assert result.title == "New Conversation"
        assert len(result.messages) == 1
        assert result.model == "gpt-3.5-turbo"
        assert result.provider == "openai"
        
        # Verify the database was called correctly
        mock_collection.insert_one.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_conversation_found(mock_collection, sample_conversation_data):
    """Test getting an existing conversation."""
    with patch('app.services.conversation_service.get_collection', return_value=mock_collection):
        # Mock the find_one method
        mock_collection.find_one = AsyncMock(return_value=sample_conversation_data)
        
        # Call the function
        result = await get_conversation("test_id_123")
        
        # Verify the result
        assert result is not None
        assert result.id == "test_id_123"
        assert result.title == "Test Conversation"
        assert len(result.messages) == 1
        mock_collection.find_one.assert_awaited_once_with({"id": "test_id_123"})

@pytest.mark.asyncio
async def test_get_conversation_not_found(mock_collection):
    """Test getting a non-existent conversation."""
    with patch('app.services.conversation_service.get_collection', return_value=mock_collection):
        # Mock the find_one method to return None
        mock_collection.find_one = AsyncMock(return_value=None)
        
        # Call the function
        result = await get_conversation("nonexistent_id")
        
        # Verify the result
        assert result is None
        mock_collection.find_one.assert_awaited_once_with({"id": "nonexistent_id"})

@pytest.mark.asyncio
async def test_list_conversations(mock_collection, sample_conversation_data):
    """Test listing conversations with pagination."""
    with patch('app.services.conversation_service.get_collection', return_value=mock_collection):
        # Create a mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [sample_conversation_data]
        
        # Set up the method chain
        mock_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_cursor
        
        # Call the function
        result = await list_conversations(skip=0, limit=10)
        
        # Verify the result
        assert len(result) == 1
        assert result[0].id == "test_id_123"
        
        # Verify the database was called correctly
        mock_collection.find.assert_called_once()
        mock_cursor.to_list.assert_awaited_once_with(length=10)

@pytest.mark.asyncio
async def test_update_conversation(mock_collection, sample_conversation_data):
    """Test updating a conversation."""
    with patch('app.services.conversation_service.get_collection', return_value=mock_collection):
        # Mock the database methods
        # First call returns the original conversation, second call returns the updated one
        updated_data = dict(sample_conversation_data)
        updated_data["title"] = "Updated Title"
        updated_data["model"] = "gpt-4"
        mock_collection.find_one = AsyncMock(side_effect=[sample_conversation_data, updated_data])
        mock_collection.update_one = AsyncMock(return_value=MagicMock(matched_count=1, modified_count=1))
        
        # Create update data
        update_data = ConversationUpdate(title="Updated Title", model="gpt-4")
        
        # Call the function
        result = await update_conversation("test_id_123", update_data)
        
        # Verify the result
        assert result is not None
        assert result.title == "Updated Title"
        
        # Verify the database was called correctly
        mock_collection.update_one.assert_awaited_once()
        assert "$set" in mock_collection.update_one.call_args[0][1]
        assert "updated_at" in mock_collection.update_one.call_args[0][1]["$set"]

@pytest.mark.asyncio
async def test_delete_conversation(mock_collection):
    """Test deleting a conversation."""
    with patch('app.services.conversation_service.get_collection', return_value=mock_collection):
        # Mock the delete_one method
        mock_collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
        
        # Call the function
        result = await delete_conversation("test_id_123")
        
        # Verify the result
        assert result is True
        mock_collection.delete_one.assert_awaited_once_with({"id": "test_id_123"})

@pytest.mark.asyncio
async def test_add_message_to_conversation(mock_collection, sample_conversation_data):
    """Test adding a message to a conversation."""
    with patch('app.services.conversation_service.get_collection', return_value=mock_collection):
        # Mock the database methods
        mock_collection.update_one = AsyncMock(return_value=MagicMock(matched_count=1, modified_count=1))
        mock_collection.find_one = AsyncMock(return_value={
            **sample_conversation_data,
            "messages": sample_conversation_data["messages"] + [{"role": "assistant", "content": "Hi there!"}]
        })
        
        # Create a new message
        new_message = {"role": "user", "content": "Another message", "timestamp": "2023-01-01T00:01:00Z"}
        
        # Call the function
        result = await add_message_to_conversation("test_id_123", new_message)
        
        # Verify the result
        assert result is not None
        assert len(result.messages) == 2
        # Check if messages are already Message objects or still dictionaries
        if hasattr(result.messages[1], 'content'):
            # If they're Message objects
            assert result.messages[1].content == "Hi there!"
        else:
            # If they're still dictionaries
            assert result.messages[1]["content"] == "Hi there!"
        
        # Verify the database was called correctly
        mock_collection.update_one.assert_awaited_once()
        assert "$push" in mock_collection.update_one.call_args[0][1]
        assert "messages" in mock_collection.update_one.call_args[0][1]["$push"]
        assert "updated_at" in mock_collection.update_one.call_args[0][1]["$set"]

@pytest.mark.asyncio
async def test_add_message_to_nonexistent_conversation(mock_collection):
    """Test adding a message to a non-existent conversation."""
    with patch('app.services.conversation_service.get_collection', return_value=mock_collection):
        # Mock the update_one to return no modifications
        mock_collection.update_one = AsyncMock(return_value=MagicMock(matched_count=0, modified_count=0))
        
        # Call the function
        result = await add_message_to_conversation("nonexistent_id", {"role": "user", "content": "Hello"})
        
        # Verify the result
        assert result is None
        mock_collection.update_one.assert_awaited_once()
