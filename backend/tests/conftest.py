"""
Pytest configuration and fixtures for testing the backend application.
"""
import os
import asyncio
from typing import AsyncGenerator, Generator, Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from bson import ObjectId

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
from unittest.mock import AsyncMock, MagicMock

from app.main import app as original_app
from app.core.config import settings
from app.api.v1.endpoints.openai_Router import router as openai_router
from app.api.v1.endpoints.conversation_router import router as conversation_router

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["MONGODB_URL"] = "mongomock://localhost"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def create_test_app():
    """Create a FastAPI test application with mocked dependencies."""
    # Create a new FastAPI app without the database connection events
    test_app = FastAPI(
        title="Test LLM Chat API",
        description="Test API for LLM Chat",
    )
    
    # Add CORS middleware
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    test_app.include_router(openai_router, prefix=settings.API_PREFIX)
    test_app.include_router(conversation_router, prefix=f"{settings.API_PREFIX}/conversations", tags=["conversations"])
    
    # Add test routes
    @test_app.get("/")
    async def root():
        return {"message": "Test API"}
    
    @test_app.get("/health")
    async def health_check():
        return {"status": "test_healthy"}
    
    return test_app

@pytest.fixture(scope="function")
async def test_app():
    """Create a FastAPI test application with mocked dependencies."""
    return create_test_app()

@pytest.fixture(scope="function")
async def test_client(test_app) -> TestClient:
    """Create a test client for the FastAPI application with mocked MongoDB."""
    with TestClient(test_app) as client:
        yield client


from unittest.mock import AsyncMock, MagicMock
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
import pytest
from app.core.database import MongoDB, get_database

@pytest.fixture(scope="function")
async def mock_mongodb(monkeypatch, sample_conversation):
    """Create a mock MongoDB client for testing with proper async support."""
    # Create a mock database
    mock_db = MagicMock(spec=AsyncIOMotorDatabase)
    
    # Create a mock collection
    mock_collection = MagicMock(spec=AsyncIOMotorCollection)
    
    # Store test data in memory
    test_conversations = {}
    
    # Configure the collection methods
    async def mock_find(*args, **kwargs):
        # Convert test_conversations dict to list of values
        conversations = list(test_conversations.values())
        
        # Apply skip and limit if provided
        skip = kwargs.get('skip', 0)
        limit = kwargs.get('limit', 0)
        
        # Sort by updated_at in descending order
        sorted_conversations = sorted(
            conversations,
            key=lambda x: x.get('updated_at', '1970-01-01T00:00:00'),
            reverse=True
        )
        
        # Apply skip and limit
        result = sorted_conversations[skip:skip + limit] if limit else sorted_conversations[skip:]
        
        # Create a mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = result
        return mock_cursor
    
    async def mock_find_one(query, *args, **kwargs):
        if not query:
            return None
        
        # Handle query by id
        if 'id' in query:
            return test_conversations.get(query['id'])
        elif '_id' in query:
            return test_conversations.get(str(query['_id']))
        return None
    
    async def mock_insert_one(document, *args, **kwargs):
        doc_id = str(ObjectId())
        document['_id'] = doc_id
        document['id'] = doc_id
        document['created_at'] = datetime.utcnow()
        document['updated_at'] = datetime.utcnow()
        test_conversations[doc_id] = document
        
        mock_result = MagicMock()
        mock_result.inserted_id = doc_id
        return mock_result
    
    async def mock_update_one(filter_query, update_data, *args, **kwargs):
        doc_id = filter_query.get('id') or filter_query.get('_id')
        if not doc_id or doc_id not in test_conversations:
            mock_result = MagicMock()
            mock_result.matched_count = 0
            return mock_result
            
        # Get the document to update
        doc = test_conversations[doc_id]
        
        # Apply $set updates
        if '$set' in update_data:
            for key, value in update_data['$set'].items():
                if key == 'messages':
                    doc['messages'] = value
                else:
                    doc[key] = value
            
            # Always update updated_at
            doc['updated_at'] = datetime.utcnow()
        
        mock_result = MagicMock()
        mock_result.matched_count = 1
        return mock_result
    
    async def mock_delete_one(filter_query, *args, **kwargs):
        doc_id = filter_query.get('id') or filter_query.get('_id')
        if doc_id and doc_id in test_conversations:
            del test_conversations[doc_id]
            mock_result = MagicMock()
            mock_result.deleted_count = 1
            return mock_result
        
        mock_result = MagicMock()
        mock_result.deleted_count = 0
        return mock_result
    
    # Configure the mock collection methods
    mock_collection.find.side_effect = mock_find
    mock_collection.find_one.side_effect = mock_find_one
    mock_collection.insert_one.side_effect = mock_insert_one
    mock_collection.update_one.side_effect = mock_update_one
    mock_collection.delete_one.side_effect = mock_delete_one
    
    # Configure the database to return our mock collection
    mock_db.__getitem__.return_value = mock_collection
    
    # Create a mock client
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    # Patch the MongoDB class
    monkeypatch.setattr("app.core.database.MongoDB.client", mock_client)
    monkeypatch.setattr("app.core.database.MongoDB.db", mock_db)
    
    # Patch get_database to return our mock db directly, not as a coroutine
    def mock_get_database():
        return mock_db
        
    monkeypatch.setattr("app.core.database.get_database", mock_get_database)
    
    # Patch connect_to_mongo to do nothing
    async def mock_connect_to_mongo():
        return mock_client
        
    monkeypatch.setattr("app.core.database.connect_to_mongo", mock_connect_to_mongo)
    
    # Initialize the database connection
    MongoDB.client = mock_client
    MongoDB.db = mock_db
    
    # Add a helper method to get the test data
    mock_db.get_test_data = lambda: test_conversations
    
    try:
        yield mock_db
    finally:
        # Clean up
        mock_client.close = AsyncMock()
        await mock_client.close()


@pytest.fixture
def mock_openai() -> Generator[MagicMock, None, None]:
    """Mock the OpenAI client for testing."""
    with patch("app.services.openai_service.get_openai_client") as mock_get_client, \
         patch("openai.OpenAI") as mock_openai_class, \
         patch("openai.AsyncOpenAI") as mock_async_openai_class:
        
        # Create a mock client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Create a mock response for non-streaming
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = "This is a test response"
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 10
        
        # Create a mock streaming response
        class MockStreamResponse:
            def __init__(self):
                self.choices = [MagicMock()]
                self.choices[0].delta = {"content": "This is a test response"}
                self.choices[0].finish_reason = "stop"
        
        # Create a mock streaming generator
        async def mock_stream_generator():
            yield {
                "id": "test-123",
                "object": "chat.completion.chunk",
                "created": 1234567890,
                "model": "gpt-3.5-turbo",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "This is a test response"},
                        "finish_reason": "stop"
                    }
                ]
            }
        
        # Create an async function that returns our mock response
        async def mock_create_async(*args, **kwargs):
            # Check if streaming is requested
            if kwargs.get('stream', False):
                return mock_stream_generator()
            return mock_response
        
        # Configure the client to use our mock create function
        mock_client.chat.completions.create = AsyncMock(side_effect=mock_create_async)
        
        # Mock the async client
        mock_async_client = MagicMock()
        mock_async_client.chat.completions.create = AsyncMock(side_effect=mock_create_async)
        mock_async_openai_class.return_value = mock_async_client
        
        # Mock the sync client
        def mock_create_sync(*args, **kwargs):
            if kwargs.get('stream', False):
                return [MockStreamResponse()]
            return mock_response
            
        mock_sync_client = MagicMock()
        mock_sync_client.chat.completions.create = MagicMock(side_effect=mock_create_sync)
        mock_openai_class.return_value = mock_sync_client
        
        # Configure the mock to handle max_tokens validation
        def validate_max_tokens(**kwargs):
            max_tokens = kwargs.get('max_tokens')
            if max_tokens and max_tokens > 4096:
                raise ValueError("max_tokens is too large")
            if kwargs.get('stream', False):
                return mock_create_async(**kwargs)
            return mock_response
        
        mock_client.chat.completions.create.side_effect = validate_max_tokens
        
        yield mock_client


@pytest.fixture
def sample_conversation() -> dict:
    """Return a sample conversation for testing."""
    return {
        "title": "Test Conversation",
        "messages": [
            {"role": "user", "content": "Hello, world!"},
            {"role": "assistant", "content": "Hi there! How can I help you?"}
        ]
    }
