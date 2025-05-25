"""
Tests for the main application module.
"""
import pytest
from fastapi import FastAPI

from app.main import app, health_check

# Simple test for the app instance
def test_app_instance():
    """Test that the app is a FastAPI instance with correct configuration."""
    assert isinstance(app, FastAPI)
    assert app.title == "LLM Chat API"
    assert app.description == "API for interacting with various LLM providers"

# Test the route handler directly
def test_health_route_exists():
    """Test that the health route exists in the app."""
    # Find the health route in the app routes
    health_route = None
    for route in app.routes:
        if route.path == "/health":
            health_route = route
            break
    
    assert health_route is not None

# Direct test of the health check function
@pytest.mark.asyncio
async def test_health_check_function():
    """Test the health_check function directly."""
    result = await health_check()
    assert result == {"status": "healthy"}
