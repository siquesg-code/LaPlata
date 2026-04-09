"""Tests for dashboard endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_empty(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 0
    assert data["completed_tasks"] == 0
    assert data["pending_tasks"] == 0
    assert data["total_expenses"] == 0
    assert data["total_emails"] == 0
    assert data["upcoming_meetings"] == 0
    assert data["total_documents"] == 0
    assert data["total_reports"] == 0


@pytest.mark.asyncio
async def test_dashboard_with_data(authenticated_client: AsyncClient):
    # Create tasks
    await authenticated_client.post("/api/tasks", json={"title": "Task 1", "status": "todo"})
    await authenticated_client.post("/api/tasks", json={"title": "Task 2", "status": "done"})
    await authenticated_client.post("/api/tasks", json={"title": "Task 3", "status": "in_progress"})

    # Create expenses
    await authenticated_client.post("/api/expenses", json={"description": "E1", "amount": 100.0})
    await authenticated_client.post("/api/expenses", json={"description": "E2", "amount": 50.0})

    # Create emails
    await authenticated_client.post("/api/emails", json={"to_address": "a@b.com", "subject": "S", "body": "B"})

    # Create meetings (future date to count as upcoming)
    await authenticated_client.post("/api/meetings", json={"title": "M1", "meeting_date": "2099-01-01"})

    # Create documents
    await authenticated_client.post("/api/documents", json={"title": "Doc1"})

    # Create reports
    await authenticated_client.post("/api/reports", json={"title": "Rep1", "content": "C"})

    response = await authenticated_client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 3
    assert data["completed_tasks"] == 1
    assert data["pending_tasks"] == 2
    assert data["total_expenses"] == 150.0
    assert data["total_emails"] == 1
    assert data["upcoming_meetings"] == 1
    assert data["total_documents"] == 1
    assert data["total_reports"] == 1


@pytest.mark.asyncio
async def test_dashboard_unauthorized(client: AsyncClient):
    response = await client.get("/api/dashboard")
    assert response.status_code == 401
