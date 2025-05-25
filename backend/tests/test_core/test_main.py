"""
Tests for the main application module.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import platform

from app.main import app, health_check
from app.core.config import settings

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

# Test the health check endpoint via HTTP
def test_health_check_endpoint():
    """Test the /health endpoint returns expected data."""
    client = TestClient(app)
    response = client.get("/health")
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Parse the response
    result = response.json()
    
    # Check that all expected fields are present
    assert "status" in result
    assert result["status"] == "healthy"
    
    # Check environment information
    assert "environment" in result
    assert result["environment"] == settings.ENVIRONMENT
    
    # Check system information
    assert "system" in result
    system_info = result["system"]
    assert isinstance(system_info, dict)
    assert "machine" in system_info
    assert "processor" in system_info
    assert "python_version" in system_info
    assert "system" in system_info
    assert "release" in system_info

# Direct test of the health check function
@pytest.mark.asyncio
async def test_health_check_function():
    """Test the health_check function directly."""
    result = await health_check()
    
    # Check that all expected fields are present
    assert "status" in result
    assert result["status"] == "healthy"
    
    # Check environment information
    assert "environment" in result
    assert result["environment"] == settings.ENVIRONMENT
    
    # Check system information
    assert "system" in result
    system_info = result["system"]
    assert isinstance(system_info, dict)
    assert "machine" in system_info
    assert "processor" in system_info
    assert "python_version" in system_info
    assert "system" in system_info
    assert "release" in system_info
