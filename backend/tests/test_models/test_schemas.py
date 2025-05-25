"""
Tests for Pydantic models and schemas.
"""
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.v1.models.openai_models import ChatRequest, ChatResponse, Message
from app.api.v1.models.conversation_models import Conversation


def test_message_model():
    """Test the Message model."""
    # Test valid message
    message = Message(role="user", content="Hello!")
    assert message.role == "user"
    assert message.content == "Hello!"
    
    # Test default role
    message = Message(content="Hello!")
    assert message.role == "user"
    
    # Test invalid role
    with pytest.raises(ValueError):
        Message(role="invalid", content="Hello!")


def test_chat_request_model():
    """Test the ChatRequest model."""
    # Test with minimal required fields
    request = ChatRequest(
        messages=[Message(role="user", content="Hello")]
    )
    assert len(request.messages) == 1
    assert request.messages[0].content == "Hello"
    assert request.model is None
    assert request.provider is None
    
    # Test with all fields
    request = ChatRequest(
        messages=[Message(role="user", content="Hello")],
        model="gpt-3.5-turbo",
        provider="openai",
        max_tokens=100,
        temperature=0.8,
        stream=True
    )
    assert request.model == "gpt-3.5-turbo"
    assert request.provider == "openai"
    assert request.max_tokens == 100
    assert request.temperature == 0.8
    assert request.stream is True


def test_chat_response_model():
    """Test the ChatResponse model."""
    # Test with required fields only
    response = ChatResponse(
        message=Message(role="assistant", content="Hello!"),
        provider="openai",
        model="gpt-3.5-turbo"
    )
    assert response.message.content == "Hello!"
    assert response.provider == "openai"
    assert response.model == "gpt-3.5-turbo"
    assert response.usage is None
    
    # Test with optional usage field
    response = ChatResponse(
        message=Message(role="assistant", content="Hello!"),
        usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        provider="openai",
        model="gpt-3.5-turbo"
    )
    assert response.usage["total_tokens"] == 15


def test_conversation_model():
    """Test the Conversation model."""
    # Test with minimal required fields
    conversation = Conversation(
        title="Test Conversation",
        messages=[Message(role="user", content="Hi"), Message(role="assistant", content="Hello!")]
    )
    assert isinstance(conversation.id, str)
    assert conversation.title == "Test Conversation"
    assert len(conversation.messages) == 2
    assert isinstance(conversation.created_at, datetime)
    assert conversation.model is None
    
    # Test with all fields
    conversation = Conversation(
        title="Test Conversation",
        messages=[Message(role="user", content="Hi"), Message(role="assistant", content="Hello!")],
        model="gpt-3.5-turbo",
        provider="openai"
    )
    assert conversation.model == "gpt-3.5-turbo"
    assert conversation.provider == "openai"
