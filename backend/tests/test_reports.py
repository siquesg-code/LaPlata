"""Tests for report CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_report(authenticated_client: AsyncClient):
    payload = {"title": "Monthly Report", "content": "Report content here", "report_type": "general"}
    response = await authenticated_client.post("/api/reports", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Monthly Report"
    assert data["content"] == "Report content here"
    assert data["report_type"] == "general"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_reports(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/reports", json={"title": "R1", "content": "C1"})
    await authenticated_client.post("/api/reports", json={"title": "R2", "content": "C2"})
    response = await authenticated_client.get("/api/reports")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
