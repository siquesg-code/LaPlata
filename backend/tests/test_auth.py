"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient

from app.models import User


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "securepass123",
        "full_name": "New User",
        "organization_name": "New Org",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user: User):
    response = await client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "anotherpass123",
        "full_name": "Another User",
        "organization_name": "Another Org",
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user: User):
    response = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user: User):
    response = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(authenticated_client: AsyncClient, test_user: User):
    response = await authenticated_client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(authenticated_client: AsyncClient):
    response = await authenticated_client.post("/api/auth/refresh")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
