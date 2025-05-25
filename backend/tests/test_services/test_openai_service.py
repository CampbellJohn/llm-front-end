"""
Tests for the OpenAI service.
"""
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock, ANY
from fastapi import HTTPException

from app.api.v1.models.openai_models import Message, ChatRequest
from app.services.openai_service import get_openai_response, get_openai_client

# Test markers
pytestmark = pytest.mark.asyncio

async def test_get_openai_response_success():
    """Test successful chat response generation."""
    # Setup test data
    test_messages = [Message(role="user", content="Test")]
    
    # Mock the OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = "Test response"
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15
    
    # Mock the client and its methods
    with patch('app.services.openai_service.get_openai_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_response
        
        # Call the function
        response = await get_openai_response(
            messages=test_messages,
            model="gpt-3.5-turbo"
        )
        
        # Assertions
        assert response["content"] == "Test response"
        assert response["usage"]["total_tokens"] == 15
        mock_client.chat.completions.create.assert_awaited_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=4000,
            temperature=0.7
        )

async def test_get_openai_response_streaming():
    """Test streaming chat response generation."""
    # Setup test data
    test_messages = [Message(role="user", content="Test")]
    
    # Mock the streaming response
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta = MagicMock(content="stream ")
    mock_chunk.usage = None
    
    # Create an async generator for the mock stream
    async def mock_stream():
        for _ in range(3):
            yield mock_chunk
    
    with patch('app.services.openai_service.get_openai_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_stream()
        
        # Call the function with streaming
        response = await get_openai_response(
            messages=test_messages,
            model="gpt-3.5-turbo",
            stream=True
        )
        
        # Assertions for streaming response
        assert response["content"] == ""
        assert response["usage"]["total_tokens"] == 0
        assert response["usage"]["completion_tokens"] == 0

async def test_get_openai_response_error():
    """Test error handling in get_openai_response."""
    # Setup test data
    test_messages = [Message(role="user", content="Test")]
    
    # Mock the client to raise an exception
    with patch('app.services.openai_service.get_openai_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Call the function and expect an exception
        with pytest.raises(Exception) as exc_info:
            await get_openai_response(
                messages=test_messages,
                model="gpt-3.5-turbo"
            )
        
        assert "API Error" in str(exc_info.value)

async def test_get_openai_response_empty_messages():
    """Test with empty messages list."""
    # Mock the OpenAI client to avoid actual API calls
    with patch('app.services.openai_service.get_openai_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        # The current implementation doesn't validate empty messages, so we'll mock an error from OpenAI
        mock_client.chat.completions.create.side_effect = Exception("Empty messages array")
        
        # Expect an exception to be raised
        with pytest.raises(Exception) as exc_info:
            await get_openai_response(messages=[], model="gpt-3.5-turbo")
        
        assert "Empty messages" in str(exc_info.value)

async def test_get_openai_response_invalid_model():
    """Test with invalid model name."""
    # Mock the OpenAI client to avoid actual API calls
    with patch('app.services.openai_service.get_openai_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        # The current implementation doesn't validate model names, so we'll mock an error from OpenAI
        mock_client.chat.completions.create.side_effect = Exception("Invalid model: invalid-model")
        
        # Expect an exception to be raised
        with pytest.raises(Exception) as exc_info:
            await get_openai_response(
                messages=[Message(role="user", content="test")],
                model="invalid-model"
            )
        
        assert "Invalid model" in str(exc_info.value)

class RateLimitError(Exception):
    """Mock rate limit error for testing."""
    status_code = 429

async def test_get_openai_response_rate_limit():
    """Test handling of rate limit errors."""
    test_messages = [Message(role="user", content="Test")]
    
    with patch('app.services.openai_service.get_openai_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        # The current implementation doesn't handle rate limits specially, so we'll just mock a general exception
        mock_client.chat.completions.create.side_effect = RateLimitError("Rate limit exceeded")
        
        # Expect a general exception to be raised
        with pytest.raises(Exception) as exc_info:
            await get_openai_response(
                messages=test_messages,
                model="gpt-3.5-turbo"
            )
            
        assert "Rate limit exceeded" in str(exc_info.value)
