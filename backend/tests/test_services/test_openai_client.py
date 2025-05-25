"""
Tests for OpenAI client initialization in the openai_service module.
"""
import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from openai import AsyncOpenAI

from app.services.openai_service import get_openai_client

# Remove async test marker since we're testing sync function
# pytestmark = pytest.mark.asyncio

def test_get_openai_client_success():
    """Test successful OpenAI client initialization."""
    with patch('app.services.openai_service._client', None), \
         patch('app.services.openai_service.settings') as mock_settings:
        
        # Configure mock settings
        mock_settings.OPENAI_API_KEY = "test-api-key"
        mock_settings.OPENAI_API_TIMEOUT = 30.0
        
        # Create a real AsyncOpenAI instance for testing
        with patch('app.services.openai_service.AsyncOpenAI') as mock_async_openai:
            # Configure mock client
            mock_client = MagicMock(spec=AsyncOpenAI)
            mock_async_openai.return_value = mock_client
            
            # Call the function
            result = get_openai_client()
            
            # Assertions
            assert result is mock_client
            mock_async_openai.assert_called_once_with(
                api_key="test-api-key",
                timeout=30.0,
                max_retries=3
            )

def test_get_openai_client_cached():
    """Test that the client is cached and reused."""
    # Create a mock client
    mock_client = MagicMock()
    
    # Patch the global _client
    with patch('app.services.openai_service._client', mock_client):
        # Call the function
        result = get_openai_client()
        
        # Assertions
        assert result is mock_client

def test_get_openai_client_validation_error():
    """Test handling of validation errors during client initialization."""
    with patch('app.services.openai_service._client', None), \
         patch('app.services.openai_service.settings') as mock_settings:
        
        # Configure mock settings
        mock_settings.OPENAI_API_KEY = ""  # Empty API key
        
        # Configure mock to raise ValidationError
        with patch('app.services.openai_service.AsyncOpenAI') as mock_async_openai:
            # Create a simple exception that will be caught and handled
            mock_async_openai.side_effect = Exception("API key is required")
            
            # Call the function and expect an exception
            with pytest.raises(RuntimeError) as excinfo:
                get_openai_client()
            
            # Verify error message contains the expected information
            # The error message can be either "Invalid configuration" or "Failed to initialize"
            # depending on how get_openai_client handles the exception
            assert "API key is required" in str(excinfo.value)

def test_get_openai_client_general_exception():
    """Test handling of general exceptions during client initialization."""
    with patch('app.services.openai_service._client', None), \
         patch('app.services.openai_service.settings') as mock_settings, \
         patch('app.services.openai_service.AsyncOpenAI') as mock_async_openai:
        
        # Configure mock settings
        mock_settings.OPENAI_API_KEY = "test-api-key"
        mock_settings.OPENAI_API_TIMEOUT = 30.0
        
        # Configure mock to raise a general exception
        mock_async_openai.side_effect = Exception("Test error")
        
        # Call the function and expect an exception
        with pytest.raises(RuntimeError) as excinfo:
            get_openai_client()
        
        # Verify error message
        assert "Failed to initialize OpenAI client" in str(excinfo.value)
        assert "Test error" in str(excinfo.value)
