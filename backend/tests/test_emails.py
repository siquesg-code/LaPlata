import pytest


@pytest.mark.asyncio
async def test_create_email(client):
    payload = {"to_address": "test@example.com", "subject": "Hello", "body": "Test body"}
    response = await client.post("/api/emails", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["to_address"] == "test@example.com"
    assert data["subject"] == "Hello"
    assert data["body"] == "Test body"
    assert data["status"] == "draft"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_emails(client):
    await client.post("/api/emails", json={"to_address": "a@b.com", "subject": "S1", "body": "B1"})
    await client.post("/api/emails", json={"to_address": "c@d.com", "subject": "S2", "body": "B2"})
    response = await client.get("/api/emails")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_delete_email(client):
    create_resp = await client.post("/api/emails", json={"to_address": "x@y.com", "subject": "Del", "body": "Body"})
    email_id = create_resp.json()["id"]
    response = await client.delete(f"/api/emails/{email_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Email deleted"


@pytest.mark.asyncio
async def test_delete_email_not_found(client):
    response = await client.delete("/api/emails/9999")
    assert response.status_code == 404
