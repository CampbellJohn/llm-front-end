"""
Tests for the streaming functionality in the OpenAI router.
"""
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.models.openai_models import Message

# Test client
test_client = TestClient(app)

# Test markers
pytestmark = pytest.mark.asyncio

class AsyncIterator:
    """Mock async iterator for streaming responses."""
    def __init__(self, items):
        self.items = items
        self.index = 0
        
    def __aiter__(self):
        return self
        
    async def __anext__(self):
        if self.index < len(self.items):
            item = self.items[self.index]
            self.index += 1
            return item
        raise StopAsyncIteration

@pytest.fixture
def mock_openai_streaming_response():
    """Create a mock streaming response from OpenAI."""
    chunks = []
    
    # Create chunks with content
    for i, text in enumerate(["Hello", ", ", "world", "!"]):
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta = MagicMock()
        chunk.choices[0].delta.content = text
        chunk.dict = lambda text=text: {
            "id": f"chunk-{i}",
            "object": "chat.completion.chunk",
            "created": 1677825464,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": text},
                    "finish_reason": None
                }
            ]
        }
        chunks.append(chunk)
    
    # Final chunk with finish reason
    final_chunk = MagicMock()
    final_chunk.choices = [MagicMock()]
    final_chunk.choices[0].delta = MagicMock()
    final_chunk.choices[0].delta.content = None
    final_chunk.choices[0].finish_reason = "stop"
    final_chunk.dict = lambda: {
        "id": "chunk-final",
        "object": "chat.completion.chunk",
        "created": 1677825464,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }
        ]
    }
    chunks.append(final_chunk)
    
    return AsyncIterator(chunks)

async def test_stream_chat_endpoint():
    """Test the streaming chat endpoint with full content response."""
    # Setup test data
    request_data = {
        "messages": [{"role": "user", "content": "Stream test"}],
        "conversation_id": "test-conv-123",
        "model": "gpt-4",
        "stream": True
    }
    
    # Create response chunks manually instead of using the fixture
    chunks = []
    
    # Create chunks with content
    for i, text in enumerate(["Hello", ", ", "world", "!"]):
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta = MagicMock()
        chunk.choices[0].delta.content = text
        chunk.dict = lambda text=text: {
            "id": f"chunk-{i}",
            "object": "chat.completion.chunk",
            "created": 1677825464,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": text},
                    "finish_reason": None
                }
            ]
        }
        chunks.append(chunk)
    
    # Final chunk with finish reason
    final_chunk = MagicMock()
    final_chunk.choices = [MagicMock()]
    final_chunk.choices[0].delta = MagicMock()
    final_chunk.choices[0].delta.content = None
    final_chunk.choices[0].finish_reason = "stop"
    final_chunk.dict = lambda: {
        "id": "chunk-final",
        "object": "chat.completion.chunk",
        "created": 1677825464,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }
        ]
    }
    chunks.append(final_chunk)
    
    # Mock the streaming response
    with patch('app.api.v1.endpoints.openai_Router.get_openai_client') as mock_get_client:
        # Set up the mock client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Set up mock streaming response
        mock_completions = AsyncMock()
        mock_client.chat.completions.create = mock_completions
        
        # Set up the async iterator response
        mock_response = AsyncIterator(chunks)
        mock_completions.return_value = mock_response
        
        # Make the request
        with test_client.stream("POST", "/api/chat", json=request_data) as response:
            # Check status code
            assert response.status_code == status.HTTP_200_OK
            
            # Collect all the streaming data
            chunks = []
            for chunk in response.iter_lines():
                if chunk:
                    # SSE format: data: {...}
                    # Handle both string and bytes types
                    if isinstance(chunk, bytes):
                        chunk_str = chunk.decode('utf-8')
                    else:
                        chunk_str = chunk
                        
                    if chunk_str.startswith('data: ') and not chunk_str.endswith('[DONE]'):
                        chunk_data = json.loads(chunk_str[6:])  # Skip 'data: '
                        chunks.append(chunk_data)
            
            # Verify we got the expected chunks
            assert len(chunks) > 0
            
            # Verify the content in the chunks
            content = ""
            for chunk in chunks:
                if 'choices' in chunk and chunk['choices'][0].get('delta', {}).get('content'):
                    content += chunk['choices'][0]['delta']['content']
            
            # Verify the final content
            assert content == "Hello, world!"
            
            # Verify that the OpenAI API was called with the right parameters
            mock_completions.assert_awaited_once_with(
                model="gpt-4",
                messages=[{"role": "user", "content": "Stream test"}],
                max_tokens=8000,  # Default value used in the implementation
                temperature=0.7,  # Default
                stream=True
            )

async def test_stream_chat_endpoint_unsupported_provider():
    """Test the streaming chat endpoint with an unsupported provider."""
    # Setup test data with unsupported provider
    request_data = {
        "messages": [{"role": "user", "content": "Stream test"}],
        "provider": "unsupported",
        "stream": True
    }
    
    # Make the request
    response = test_client.post("/api/chat", json=request_data)
    
    # Check status code - the backend returns 422 for invalid providers
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Verify error content
    error_data = response.json()
    assert 'detail' in error_data
    assert isinstance(error_data['detail'], list)
    
    # Find the error related to the provider
    provider_error = False
    for error in error_data['detail']:
        if 'provider' in str(error):
            provider_error = True
            break
            
    assert provider_error, "No provider validation error found in response"

async def test_stream_chat_endpoint_error_handling():
    """Test error handling in the streaming chat endpoint."""
    # Setup test data
    request_data = {
        "messages": [{"role": "user", "content": "Stream test"}],
        "model": "gpt-4",
        "stream": True
    }
    
    # Mock the client to raise an exception
    with patch('app.api.v1.endpoints.openai_Router.get_openai_client') as mock_get_client:
        # Set up the mock client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Make the client raise an exception
        mock_client.chat.completions.create.side_effect = Exception("Test streaming error")
        
        # Make the request
        with test_client.stream("POST", "/api/chat", json=request_data) as response:
            # Check status code
            assert response.status_code == status.HTTP_200_OK
            
            # Collect the error response
            chunks = []
            for chunk in response.iter_lines():
                if chunk:
                    chunks.append(chunk)
            
            # Should have one error chunk
            assert len(chunks) == 1
            
            # Verify error content
            chunk_data = json.loads(chunks[0][6:])  # Skip 'data: '
            assert 'error' in chunk_data
            assert 'Test streaming error' in chunk_data['error']
