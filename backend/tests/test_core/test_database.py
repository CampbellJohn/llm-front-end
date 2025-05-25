"""
Tests for the database module.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.database import (
    MongoDB,
    connect_to_mongo,
    create_indexes,
    close_mongo_connection,
    get_database
)

# Test markers
pytestmark = pytest.mark.asyncio

@pytest.fixture(autouse=True)
async def reset_mongodb_state():
    """Reset MongoDB class state before each test."""
    # Save original state
    original_client = MongoDB.client
    original_db = MongoDB.db
    
    # Reset for test
    MongoDB.client = None
    MongoDB.db = None
    
    # Run the test
    yield
    
    # Restore original state
    MongoDB.client = original_client
    MongoDB.db = original_db


async def test_connect_to_mongo_success():
    """Test successful MongoDB connection."""
    with patch("app.core.database.AsyncIOMotorClient") as mock_client, \
         patch("app.core.database.create_indexes") as mock_create_indexes:
        # Configure the mock client
        mock_db = MagicMock()
        mock_db.command = AsyncMock()
        mock_client.return_value = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        
        # Mock create_indexes to avoid calling it
        mock_create_indexes.return_value = AsyncMock()
        
        # Call the function
        await connect_to_mongo()
        
        # Assertions
        mock_client.assert_called_once()
        assert MongoDB.client is not None
        assert MongoDB.db is not None
        mock_db.command.assert_called_once_with('ping')
        mock_create_indexes.assert_called_once()


async def test_connect_to_mongo_retry_success():
    """Test MongoDB connection with retry logic."""
    with patch("app.core.database.AsyncIOMotorClient") as mock_client, \
         patch("app.core.database.create_indexes") as mock_create_indexes, \
         patch("app.core.database.asyncio.sleep") as mock_sleep:
        
        # Configure the mock to fail twice then succeed
        mock_db = MagicMock()
        mock_db.command = AsyncMock()
        
        # Create a side effect that raises exceptions for the first 2 attempts
        connection_attempts = 0
        
        def connection_side_effect(*args, **kwargs):
            nonlocal connection_attempts
            connection_attempts += 1
            if connection_attempts <= 2:
                raise Exception(f"Connection failed on attempt {connection_attempts}")
            
            # Return a successful client on the third attempt
            client_mock = MagicMock()
            client_mock.__getitem__.return_value = mock_db
            return client_mock
        
        mock_client.side_effect = connection_side_effect
        
        # Mock create_indexes to avoid calling it
        mock_create_indexes.return_value = AsyncMock()
        
        # Mock sleep to avoid actual delays
        mock_sleep.return_value = None
        
        # Call the function
        await connect_to_mongo()
        
        # Assertions
        assert mock_client.call_count == 3  # Called 3 times (2 failures + 1 success)
        assert mock_sleep.call_count == 2   # Sleep called twice after failures
        assert MongoDB.client is not None
        assert MongoDB.db is not None
        mock_db.command.assert_called_once_with('ping')
        mock_create_indexes.assert_called_once()


async def test_connect_to_mongo_all_attempts_fail():
    """Test MongoDB connection when all attempts fail."""
    with patch("app.core.database.AsyncIOMotorClient") as mock_client, \
         patch("app.core.database.asyncio.sleep") as mock_sleep:
        
        # Configure the mock to always fail
        mock_client.side_effect = Exception("Connection failed")
        
        # Mock sleep to avoid actual delays
        mock_sleep.return_value = None
        
        # Call the function and expect an exception
        with pytest.raises(Exception):
            await connect_to_mongo()
        
        # Assertions - we expect 5 attempts based on the range(5) in connect_to_mongo
        assert mock_client.call_count == 5  # Called for all 5 attempts
        assert mock_sleep.call_count == 4   # Sleep called 4 times (after first 4 failures)
        assert MongoDB.client is None
        assert MongoDB.db is None


async def test_create_indexes():
    """Test index creation for collections."""
    # Setup mock database
    MongoDB.db = MagicMock()
    MongoDB.db.conversations = MagicMock()
    MongoDB.db.conversations.create_index = AsyncMock()
    
    # Call the function
    await create_indexes()
    
    # Assertions
    MongoDB.db.conversations.create_index.assert_called_once_with("id", unique=True)


async def test_create_indexes_error():
    """Test error handling during index creation."""
    # Setup mock database with error
    MongoDB.db = MagicMock()
    MongoDB.db.conversations = MagicMock()
    MongoDB.db.conversations.create_index = AsyncMock(side_effect=Exception("Index creation failed"))
    
    # Call the function - should not raise exception
    await create_indexes()
    
    # Assertions
    MongoDB.db.conversations.create_index.assert_called_once_with("id", unique=True)


async def test_close_mongo_connection():
    """Test MongoDB connection closure."""
    # Setup mock
    MongoDB.client = MagicMock()
    
    # Call the function
    await close_mongo_connection()
    
    # Assertions
    MongoDB.client.close.assert_called_once()


async def test_close_mongo_connection_no_client():
    """Test MongoDB connection closure when no client exists."""
    # Setup - ensure client is None
    MongoDB.client = None
    
    # Call the function - should not raise exception
    await close_mongo_connection()
    
    # No assertions needed - just checking it doesn't raise an exception


def test_get_database_success():
    """Test successful database retrieval."""
    # Setup
    mock_db = MagicMock()
    MongoDB.db = mock_db
    
    # Call and assert
    result = get_database()
    assert result == mock_db


def test_get_database_not_initialized():
    """Test database retrieval when not initialized."""
    # Setup
    MongoDB.db = None
    
    # Call and assert
    with pytest.raises(RuntimeError, match="Database connection not established"):
        get_database()
