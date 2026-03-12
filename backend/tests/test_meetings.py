"""Tests for meeting CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_meeting(authenticated_client: AsyncClient):
    payload = {
        "title": "Team Standup",
        "meeting_date": "2026-04-01",
        "meeting_time": "09:00",
        "duration_minutes": 30,
        "location": "Room A",
    }
    response = await authenticated_client.post("/api/meetings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Team Standup"
    assert data["meeting_date"] == "2026-04-01"
    assert data["meeting_time"] == "09:00"
    assert data["duration_minutes"] == 30
    assert data["location"] == "Room A"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_meetings_ordered_by_date(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/meetings", json={"title": "Later", "meeting_date": "2026-06-01"})
    await authenticated_client.post("/api/meetings", json={"title": "Earlier", "meeting_date": "2026-04-01"})
    response = await authenticated_client.get("/api/meetings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Earlier"
    assert data[1]["title"] == "Later"


@pytest.mark.asyncio
async def test_delete_meeting(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/meetings", json={"title": "Del", "meeting_date": "2026-05-01"})
    meeting_id = create_resp.json()["id"]
    response = await authenticated_client.delete(f"/api/meetings/{meeting_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Meeting deleted"
