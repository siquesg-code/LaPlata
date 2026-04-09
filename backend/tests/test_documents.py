"""Tests for document CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_document(authenticated_client: AsyncClient):
    payload = {"title": "Test Doc", "content": "Some content", "doc_type": "general"}
    response = await authenticated_client.post("/api/documents", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Doc"
    assert data["content"] == "Some content"
    assert data["doc_type"] == "general"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_documents(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/documents", json={"title": "Doc1"})
    await authenticated_client.post("/api/documents", json={"title": "Doc2"})
    response = await authenticated_client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_delete_document(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/documents", json={"title": "To Delete"})
    doc_id = create_resp.json()["id"]
    response = await authenticated_client.delete(f"/api/documents/{doc_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Document deleted"
