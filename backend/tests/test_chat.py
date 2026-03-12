"""Tests for chat endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_greeting(authenticated_client: AsyncClient):
    response = await authenticated_client.post("/api/chat", json={"message": "hello"})
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "assistant"
    assert len(data["content"]) > 0
    assert data["tool_used"] is None


@pytest.mark.asyncio
async def test_chat_dashboard(authenticated_client: AsyncClient):
    response = await authenticated_client.post("/api/chat", json={"message": "show dashboard"})
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "assistant"
    assert data["tool_used"] == "get_dashboard"
    assert "Tasks" in data["content"] or "tasks" in data["content"].lower()


@pytest.mark.asyncio
async def test_chat_create_task(authenticated_client: AsyncClient):
    response = await authenticated_client.post("/api/chat", json={"message": "create task Test Task"})
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "assistant"
    assert data["tool_used"] == "create_task"
    assert "created" in data["content"].lower() or "task" in data["content"].lower()


@pytest.mark.asyncio
async def test_chat_history(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/chat", json={"message": "hello"})
    response = await authenticated_client.get("/api/chat/history")
    assert response.status_code == 200
    data = response.json()
    # Should have at least user message + assistant response
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_chat_clear_history(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/chat", json={"message": "hi"})
    response = await authenticated_client.delete("/api/chat/history")
    assert response.status_code == 200
    assert response.json()["message"] == "Chat history cleared"
    # Verify history is empty
    history_resp = await authenticated_client.get("/api/chat/history")
    assert len(history_resp.json()) == 0


@pytest.mark.asyncio
async def test_chat_unauthorized(client: AsyncClient):
    response = await client.post("/api/chat", json={"message": "hello"})
    assert response.status_code == 401
