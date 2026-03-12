"""Tests for task CRUD endpoints and organization isolation."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, get_password_hash
from app.models import Organization, User


@pytest.mark.asyncio
async def test_create_task(authenticated_client: AsyncClient):
    payload = {"title": "Test Task", "description": "A test task", "priority": "high"}
    response = await authenticated_client.post("/api/tasks", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "A test task"
    assert data["priority"] == "high"
    assert data["status"] == "todo"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_tasks(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/tasks", json={"title": "Task A"})
    await authenticated_client.post("/api/tasks", json={"title": "Task B"})
    response = await authenticated_client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_tasks_filter_by_status(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/tasks", json={"title": "Todo Task", "status": "todo"})
    await authenticated_client.post("/api/tasks", json={"title": "Done Task", "status": "done"})
    response = await authenticated_client.get("/api/tasks", params={"status": "todo"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Todo Task"


@pytest.mark.asyncio
async def test_get_task(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/tasks", json={"title": "Specific Task"})
    task_id = create_resp.json()["id"]
    response = await authenticated_client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Task"


@pytest.mark.asyncio
async def test_get_task_not_found(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/api/tasks/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/tasks", json={"title": "Old Title"})
    task_id = create_resp.json()["id"]
    response = await authenticated_client.patch(f"/api/tasks/{task_id}", json={"title": "New Title", "status": "in_progress"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["status"] == "in_progress"


@pytest.mark.asyncio
async def test_delete_task(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/tasks", json={"title": "To Delete"})
    task_id = create_resp.json()["id"]
    response = await authenticated_client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    # Verify deletion
    get_resp = await authenticated_client.get(f"/api/tasks/{task_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_org_isolation(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
):
    """Tasks from one organization should not be visible to another."""
    # Create second org and user
    org2 = Organization(name="Other Org")
    db_session.add(org2)
    await db_session.commit()
    await db_session.refresh(org2)

    user2 = User(
        email="other@example.com",
        hashed_password=get_password_hash("otherpass123"),
        full_name="Other User",
        role="admin",
        organization_id=org2.id,
    )
    db_session.add(user2)
    await db_session.commit()
    await db_session.refresh(user2)

    # Create task as first user
    token1 = create_access_token(data={"sub": str(test_user.id)})
    headers1 = {"Authorization": f"Bearer {token1}"}
    await client.post("/api/tasks", json={"title": "Org1 Task"}, headers=headers1)

    # List tasks as second user — should see none
    token2 = create_access_token(data={"sub": str(user2.id)})
    headers2 = {"Authorization": f"Bearer {token2}"}
    response = await client.get("/api/tasks", headers=headers2)
    assert response.status_code == 200
    assert len(response.json()) == 0
