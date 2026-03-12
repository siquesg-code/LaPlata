"""Tests for dashboard endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_dashboard(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_tasks" in data
    assert "total_expenses" in data
    assert "total_emails" in data


@pytest.mark.asyncio
async def test_dashboard_unauthorized(client: AsyncClient):
    response = await client.get("/api/dashboard")
    assert response.status_code == 401
