import pytest


@pytest.mark.asyncio
async def test_create_task(client):
    payload = {"title": "Test Task", "description": "A test task", "priority": "high"}
    response = await client.post("/api/tasks", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "A test task"
    assert data["priority"] == "high"
    assert data["status"] == "todo"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_tasks(client):
    await client.post("/api/tasks", json={"title": "Task A"})
    await client.post("/api/tasks", json={"title": "Task B"})
    response = await client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_tasks_filter_by_status(client):
    await client.post("/api/tasks", json={"title": "Todo Task", "status": "todo"})
    await client.post("/api/tasks", json={"title": "Done Task", "status": "done"})
    response = await client.get("/api/tasks", params={"status": "todo"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Todo Task"


@pytest.mark.asyncio
async def test_get_task(client):
    create_resp = await client.post("/api/tasks", json={"title": "Specific Task"})
    task_id = create_resp.json()["id"]
    response = await client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Task"


@pytest.mark.asyncio
async def test_get_task_not_found(client):
    response = await client.get("/api/tasks/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task(client):
    create_resp = await client.post("/api/tasks", json={"title": "Old Title"})
    task_id = create_resp.json()["id"]
    response = await client.patch(f"/api/tasks/{task_id}", json={"title": "New Title", "status": "in_progress"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["status"] == "in_progress"


@pytest.mark.asyncio
async def test_delete_task(client):
    create_resp = await client.post("/api/tasks", json={"title": "To Delete"})
    task_id = create_resp.json()["id"]
    response = await client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    # Verify deletion
    get_resp = await client.get(f"/api/tasks/{task_id}")
    assert get_resp.status_code == 404
