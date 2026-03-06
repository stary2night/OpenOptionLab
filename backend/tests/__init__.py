"""
Test suite for OpenOptions Lab API
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
async def async_client():
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def auth_headers(async_client):
    """Get authentication headers for testing"""
    # Register test user
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    
    try:
        await async_client.post("/api/v1/auth/register", json=register_data)
    except:
        pass  # User may already exist
    
    # Login
    login_response = await async_client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "TestPassword123!"
    })
    
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

