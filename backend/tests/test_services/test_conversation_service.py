"""
Tests for the conversation service.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.conversation_service import (
    get_collection,
    model_to_dict,
    create_conversation,
    get_conversation,
    list_conversations,
    update_conversation,
    delete_conversation,
    add_message_to_conversation
)
from app.api.v1.models.conversation_models import (
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
async def test_add_message_to_nonexistent_conversation_no_exception(mock_collection):
    """Test adding a message to a non-existent conversation (no exception version)."""
    with patch('app.services.conversation_service.get_collection', return_value=mock_collection):
        # Mock the update_one to return no modifications
        mock_collection.update_one = AsyncMock(return_value=MagicMock(matched_count=0, modified_count=0))
        
        # Call the function
        result = await add_message_to_conversation("nonexistent_id", {"role": "user", "content": "Hello"})
        
        # Verify the result
        assert result is None
        mock_collection.update_one.assert_awaited_once()

@pytest.mark.asyncio
async def test_add_message_to_nonexistent_conversation():
    """Test adding a message to a non-existent conversation (returns None)."""
    # Create a fresh mock for this test to avoid state from other tests
    fresh_mock_collection = MagicMock()
    # Configure update_one to return a result with modified_count=0 (no documents modified)
    mock_result = MagicMock()
    mock_result.modified_count = 0
    fresh_mock_collection.update_one = AsyncMock(return_value=mock_result)
    
    with patch("app.services.conversation_service.get_collection") as mock_get_collection, \
         patch("app.services.conversation_service.get_conversation") as mock_get_conversation:
        
        mock_get_collection.return_value = fresh_mock_collection
        mock_get_conversation.return_value = None
        
        message = {"role": "user", "content": "Hello"}
        
        # Function should return None when conversation not found
        result = await add_message_to_conversation("nonexistent_id", message)
        
        # Verify the result is None
        assert result is None
        
        # Verify update was attempted but no documents were modified
        fresh_mock_collection.update_one.assert_called_once()


# Additional tests for error handling and edge cases

async def test_get_collection_error():
    """Test error handling in get_collection."""
    with patch("app.services.conversation_service.get_database") as mock_get_db:
        # Simulate a database error
        mock_get_db.side_effect = Exception("Database connection error")
        
        # Verify the error is properly handled and re-raised
        with pytest.raises(Exception) as exc_info:
            get_collection()
        
        assert "Database connection error" in str(exc_info.value)


def test_model_to_dict_pydantic_v2():
    """Test model_to_dict with a Pydantic v2 model."""
    # Create a mock object with model_dump method (Pydantic v2)
    mock_obj = MagicMock()
    mock_obj.model_dump.return_value = {"key": "value"}
    
    result = model_to_dict(mock_obj)
    assert result == {"key": "value"}
    mock_obj.model_dump.assert_called_once()


def test_model_to_dict_pydantic_v1():
    """Test model_to_dict with a Pydantic v1 model."""
    # Let's directly patch the model_to_dict function to test the Pydantic v1 path
    with patch('app.services.conversation_service.model_to_dict') as mock_model_to_dict:
        # Set up the original function to be called
        mock_model_to_dict.side_effect = lambda obj: model_to_dict(obj)
        
        # Create a class that simulates a Pydantic v1 model
        class PydanticV1Model:
            def dict(self):
                return {"key": "value"}
            
            # This will raise AttributeError when accessed
            @property
            def model_dump(self):
                raise AttributeError("'PydanticV1Model' object has no attribute 'model_dump'")
        
        # Create an instance and call the function
        model = PydanticV1Model()
        
        # Call the real function with our test model
        with patch('app.services.conversation_service.model_to_dict', wraps=model_to_dict):
            result = model_to_dict(model)
            assert result == {"key": "value"}


def test_model_to_dict_fallback():
    """Test model_to_dict fallback for non-Pydantic objects."""
    # Create a dict-like object that can be converted to a dict
    class DictLike:
        def __init__(self):
            self.key = "value"
        
        def __iter__(self):
            yield "key", "value"
    
    obj = DictLike()
    result = model_to_dict(obj)
    assert result == {"key": "value"}


async def test_create_conversation_with_datetime():
    """Test creating a conversation with datetime fields."""
    # Create a conversation with a datetime field
    now = datetime.now()
    conversation = ConversationCreate(
        title="Test with datetime",
        messages=[{"role": "user", "content": "Hello", "timestamp": now}],
        model="gpt-3.5-turbo",
        provider="openai"
    )
    
    with patch("app.services.conversation_service.get_collection") as mock_get_collection:
        mock_collection = AsyncMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.insert_one.return_value = AsyncMock(inserted_id="new_id")
        
        result = await create_conversation(conversation)
        
        # Verify the datetime was properly serialized
        call_args = mock_collection.insert_one.call_args[0][0]
        for message in call_args["messages"]:
            if "timestamp" in message:
                # Check that timestamp is a string (serialized)
                assert isinstance(message["timestamp"], str)


async def test_create_conversation_error(sample_conversation_create):
    """Test error handling in create_conversation."""
    with patch("app.services.conversation_service.get_collection") as mock_get_collection:
        mock_collection = AsyncMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.insert_one.side_effect = Exception("Insert error")
        
        with pytest.raises(Exception) as exc_info:
            await create_conversation(sample_conversation_create)
        
        assert "Insert error" in str(exc_info.value)


async def test_get_conversation_error():
    """Test error handling in get_conversation."""
    with patch("app.services.conversation_service.get_collection") as mock_get_collection:
        mock_collection = AsyncMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.find_one.side_effect = Exception("Find error")
        
        with pytest.raises(Exception) as exc_info:
            await get_conversation("test_id")
        
        assert "Find error" in str(exc_info.value)


async def test_list_conversations_error():
    """Test error handling in list_conversations."""
    with patch("app.services.conversation_service.get_collection") as mock_get_collection:
        # Create a properly configured mock
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Create a mock cursor with the necessary methods
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        
        # Make the find method raise an exception
        mock_collection.find.side_effect = Exception("Find error")
        
        with pytest.raises(Exception) as exc_info:
            await list_conversations()
        
        assert "Find error" in str(exc_info.value)


async def test_update_conversation_error():
    """Test error handling in update_conversation."""
    with patch("app.services.conversation_service.get_collection") as mock_get_collection, \
         patch("app.services.conversation_service.get_conversation") as mock_get_conversation:
        
        # Mock the collection
        mock_collection = AsyncMock()
        mock_get_collection.return_value = mock_collection
        
        # Make update_one raise an exception
        mock_collection.update_one.side_effect = Exception("Update error")
        
        # Mock the existing conversation
        mock_get_conversation.return_value = {
            "id": "test_id",
            "title": "Old Title",
            "messages": []
        }
        
        update_data = ConversationUpdate(title="Updated Title")
        
        with pytest.raises(Exception) as exc_info:
            await update_conversation("test_id", update_data)
        
        assert "Update error" in str(exc_info.value)


async def test_delete_conversation_error():
    """Test error handling in delete_conversation."""
    with patch("app.services.conversation_service.get_collection") as mock_get_collection:
        mock_collection = AsyncMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.delete_one.side_effect = Exception("Delete error")
        
        with pytest.raises(Exception) as exc_info:
            await delete_conversation("test_id")
        
        assert "Delete error" in str(exc_info.value)


async def test_list_conversations_empty():
    """Test listing conversations when there are none."""
    with patch("app.services.conversation_service.get_collection") as mock_get_collection:
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Create a properly configured mock cursor
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[])
        
        # Set up the find method to return our mock cursor
        mock_collection.find.return_value = mock_cursor
        
        result = await list_conversations()
        
        assert result == []
        mock_collection.find.assert_called_once()
        mock_cursor.sort.assert_called_once_with("updated_at", -1)
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(10)


async def test_add_message_with_special_fields():
    """Test adding a message with special fields."""
    with patch("app.services.conversation_service.get_collection") as mock_get_collection, \
         patch("app.services.conversation_service.get_conversation") as mock_get_conversation:
        
        mock_collection = AsyncMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock an existing conversation
        mock_get_conversation.return_value = {
            "id": "test_id",
            "messages": []
        }
        
        # Message with special fields
        message = {
            "role": "assistant",
            "content": "Hello",
            "function_call": {"name": "test_function", "arguments": "{}"},
            "timestamp": "2023-01-01T00:00:00Z"
        }
        
        await add_message_to_conversation("test_id", message)
        
        # Verify the update operation
        mock_collection.update_one.assert_called_once()
        update_query = mock_collection.update_one.call_args[0][1]
        assert "$push" in update_query
        assert "messages" in update_query["$push"]
        assert "function_call" in update_query["$push"]["messages"]


async def test_add_message_error():
    """Test error handling in add_message_to_conversation."""
    with patch("app.services.conversation_service.get_collection") as mock_get_collection, \
         patch("app.services.conversation_service.get_conversation") as mock_get_conversation:
        
        mock_collection = AsyncMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.update_one.side_effect = Exception("Update error")
        
        # Mock an existing conversation
        mock_get_conversation.return_value = {
            "id": "test_id",
            "messages": []
        }
        
        message = {"role": "user", "content": "Hello"}
        
        with pytest.raises(Exception) as exc_info:
            await add_message_to_conversation("test_id", message)
        
        assert "Update error" in str(exc_info.value)
