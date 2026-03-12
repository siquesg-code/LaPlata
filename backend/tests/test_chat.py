"""Tests for chat endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_send_chat_message(authenticated_client: AsyncClient):
    response = await authenticated_client.post("/api/chat", json={
        "message": "show me the dashboard",
    })
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert data["role"] == "assistant"


@pytest.mark.asyncio
async def test_get_chat_history(authenticated_client: AsyncClient):
    # Send a message first
    await authenticated_client.post("/api/chat", json={
        "message": "hello",
    })
    response = await authenticated_client.get("/api/chat/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_clear_chat_history(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/chat", json={
        "message": "test message",
    })
    response = await authenticated_client.delete("/api/chat/history")
    assert response.status_code == 200

    # Verify history is cleared
    history = await authenticated_client.get("/api/chat/history")
    assert len(history.json()) == 0


@pytest.mark.asyncio
async def test_chat_unauthorized(client: AsyncClient):
    response = await client.post("/api/chat", json={
        "message": "hello",
    })
    assert response.status_code == 401
