"""Tests for expense CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_expense(authenticated_client: AsyncClient):
    payload = {"description": "Office supplies", "amount": 49.99, "category": "office"}
    response = await authenticated_client.post("/api/expenses", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Office supplies"
    assert data["amount"] == 49.99
    assert data["category"] == "office"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_expenses(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/expenses", json={"description": "E1", "amount": 10.0})
    await authenticated_client.post("/api/expenses", json={"description": "E2", "amount": 20.0})
    response = await authenticated_client.get("/api/expenses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_expense_summary(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/expenses", json={"description": "Travel", "amount": 100.0, "category": "travel"})
    await authenticated_client.post("/api/expenses", json={"description": "Software", "amount": 50.0, "category": "software"})
    await authenticated_client.post("/api/expenses", json={"description": "More Travel", "amount": 75.0, "category": "travel"})
    response = await authenticated_client.get("/api/expenses/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 225.0
    assert data["count"] == 3
    assert data["by_category"]["travel"] == 175.0
    assert data["by_category"]["software"] == 50.0


@pytest.mark.asyncio
async def test_delete_expense(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/expenses", json={"description": "Del", "amount": 5.0})
    expense_id = create_resp.json()["id"]
    response = await authenticated_client.delete(f"/api/expenses/{expense_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Expense deleted"
