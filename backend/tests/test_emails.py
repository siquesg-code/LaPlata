"""Tests for email CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_email(authenticated_client: AsyncClient):
    payload = {"to_address": "test@example.com", "subject": "Hello", "body": "Test body"}
    response = await authenticated_client.post("/api/emails", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["to_address"] == "test@example.com"
    assert data["subject"] == "Hello"
    assert data["body"] == "Test body"
    assert data["status"] == "draft"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_emails(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/emails", json={"to_address": "a@b.com", "subject": "S1", "body": "B1"})
    await authenticated_client.post("/api/emails", json={"to_address": "c@d.com", "subject": "S2", "body": "B2"})
    response = await authenticated_client.get("/api/emails")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_delete_email(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/emails", json={"to_address": "x@y.com", "subject": "Del", "body": "Body"})
    email_id = create_resp.json()["id"]
    response = await authenticated_client.delete(f"/api/emails/{email_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Email deleted"


@pytest.mark.asyncio
async def test_delete_email_not_found(authenticated_client: AsyncClient):
    response = await authenticated_client.delete("/api/emails/9999")
    assert response.status_code == 404
