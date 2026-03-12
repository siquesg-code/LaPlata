"""Tests for AI agent tool functions, rule-based processing, and helpers."""

import json

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent import (
    _add_expense,
    _complete_task,
    _create_task,
    _draft_email,
    _extract_after,
    _extract_dollar_amount,
    _extract_email_address,
    _extract_number,
    _generate_report,
    _get_dashboard,
    _list_tasks,
    _process_with_rules,
    _schedule_meeting,
    _summarize_document,
    execute_tool,
)
from app.models import Organization


@pytest.fixture
def org_id(test_org: Organization) -> int:
    return test_org.id


# --- execute_tool dispatch tests ---


@pytest.mark.asyncio
async def test_execute_tool_create_task(db_session: AsyncSession, org_id: int):
    result = await execute_tool("create_task", {"title": "Dispatch Test"}, db_session, org_id)
    data = json.loads(result)
    assert data["success"] is True
    assert data["task"]["title"] == "Dispatch Test"


@pytest.mark.asyncio
async def test_execute_tool_unknown(db_session: AsyncSession, org_id: int):
    result = await execute_tool("unknown_tool", {}, db_session, org_id)
    assert "Unknown tool" in result


# --- Individual tool function tests ---


@pytest.mark.asyncio
async def test_create_task(db_session: AsyncSession, org_id: int):
    result = await _create_task(db_session, {"title": "My Task", "priority": "high"}, org_id)
    data = json.loads(result)
    assert data["success"] is True
    assert data["task"]["title"] == "My Task"
    assert data["task"]["priority"] == "high"


@pytest.mark.asyncio
async def test_list_tasks(db_session: AsyncSession, org_id: int):
    await _create_task(db_session, {"title": "Task A"}, org_id)
    await _create_task(db_session, {"title": "Task B"}, org_id)
    result = await _list_tasks(db_session, {}, org_id)
    data = json.loads(result)
    assert data["count"] == 2


@pytest.mark.asyncio
async def test_complete_task(db_session: AsyncSession, org_id: int):
    create_result = await _create_task(db_session, {"title": "To Complete"}, org_id)
    task_id = json.loads(create_result)["task"]["id"]
    result = await _complete_task(db_session, {"task_id": task_id}, org_id)
    data = json.loads(result)
    assert data["success"] is True
    assert "completed" in data["message"].lower() or "done" in data["message"].lower()


@pytest.mark.asyncio
async def test_draft_email(db_session: AsyncSession, org_id: int):
    result = await _draft_email(db_session, {
        "to_address": "test@example.com",
        "subject": "Test Subject",
        "body": "Test Body",
    }, org_id)
    data = json.loads(result)
    assert data["success"] is True
    assert data["email"]["to"] == "test@example.com"


@pytest.mark.asyncio
async def test_add_expense(db_session: AsyncSession, org_id: int):
    result = await _add_expense(db_session, {
        "description": "Lunch",
        "amount": 25.50,
        "category": "travel",
    }, org_id)
    data = json.loads(result)
    assert data["success"] is True
    assert data["expense"]["amount"] == 25.50
    assert data["expense"]["category"] == "travel"


@pytest.mark.asyncio
async def test_summarize_document(db_session: AsyncSession, org_id: int):
    result = await _summarize_document(db_session, {
        "title": "Test Doc",
        "content": "First sentence. Second sentence. Third sentence. Fourth sentence.",
    }, org_id)
    data = json.loads(result)
    assert data["success"] is True
    assert data["document"]["title"] == "Test Doc"
    assert len(data["document"]["summary"]) > 0


@pytest.mark.asyncio
async def test_schedule_meeting(db_session: AsyncSession, org_id: int):
    result = await _schedule_meeting(db_session, {
        "title": "Standup",
        "meeting_date": "2026-05-01",
        "meeting_time": "09:00",
    }, org_id)
    data = json.loads(result)
    assert data["success"] is True
    assert data["meeting"]["title"] == "Standup"
    assert data["meeting"]["date"] == "2026-05-01"


@pytest.mark.asyncio
async def test_generate_report_expense(db_session: AsyncSession, org_id: int):
    await _add_expense(db_session, {"description": "Travel", "amount": 100.0, "category": "travel"}, org_id)
    result = await _generate_report(db_session, {"title": "Expense Report", "report_type": "expense"}, org_id)
    data = json.loads(result)
    assert data["success"] is True
    assert "Expense" in data["report"]["title"]


@pytest.mark.asyncio
async def test_generate_report_task(db_session: AsyncSession, org_id: int):
    await _create_task(db_session, {"title": "Task 1"}, org_id)
    result = await _generate_report(db_session, {"title": "Task Report", "report_type": "task"}, org_id)
    data = json.loads(result)
    assert data["success"] is True
    assert "Task" in data["report"]["content"]


@pytest.mark.asyncio
async def test_generate_report_meeting(db_session: AsyncSession, org_id: int):
    await _schedule_meeting(db_session, {"title": "M1", "meeting_date": "2099-01-01"}, org_id)
    result = await _generate_report(db_session, {"title": "Meeting Report", "report_type": "meeting"}, org_id)
    data = json.loads(result)
    assert data["success"] is True
    assert "Meeting" in data["report"]["content"]


@pytest.mark.asyncio
async def test_generate_report_general(db_session: AsyncSession, org_id: int):
    result = await _generate_report(db_session, {"title": "General Report", "report_type": "general"}, org_id)
    data = json.loads(result)
    assert data["success"] is True
    assert "Business Overview" in data["report"]["content"]


@pytest.mark.asyncio
async def test_get_dashboard(db_session: AsyncSession, org_id: int):
    result = await _get_dashboard(db_session, org_id)
    data = json.loads(result)
    assert data["total_tasks"] == 0
    assert data["total_expenses"] == 0


# --- _process_with_rules tests ---


@pytest.mark.asyncio
async def test_rules_dashboard(db_session: AsyncSession, org_id: int):
    response, tool = await _process_with_rules("show me the dashboard", db_session, org_id)
    assert tool == "get_dashboard"
    assert "Dashboard" in response or "Tasks" in response


@pytest.mark.asyncio
async def test_rules_create_task(db_session: AsyncSession, org_id: int):
    response, tool = await _process_with_rules("create task Buy groceries", db_session, org_id)
    assert tool == "create_task"
    assert "created" in response.lower() or "task" in response.lower()


@pytest.mark.asyncio
async def test_rules_list_tasks(db_session: AsyncSession, org_id: int):
    await _create_task(db_session, {"title": "Existing"}, org_id)
    response, tool = await _process_with_rules("list tasks", db_session, org_id)
    assert tool == "list_tasks"


@pytest.mark.asyncio
async def test_rules_complete_task(db_session: AsyncSession, org_id: int):
    create_result = await _create_task(db_session, {"title": "To Do"}, org_id)
    task_id = json.loads(create_result)["task"]["id"]
    response, tool = await _process_with_rules(f"complete task {task_id}", db_session, org_id)
    assert tool == "complete_task"


@pytest.mark.asyncio
async def test_rules_draft_email(db_session: AsyncSession, org_id: int):
    response, tool = await _process_with_rules("draft email to someone about project", db_session, org_id)
    assert tool == "draft_email"
    assert "email" in response.lower() or "drafted" in response.lower()


@pytest.mark.asyncio
async def test_rules_add_expense(db_session: AsyncSession, org_id: int):
    response, tool = await _process_with_rules("add expense $50 for office supplies", db_session, org_id)
    assert tool == "add_expense"
    assert "expense" in response.lower() or "logged" in response.lower()


@pytest.mark.asyncio
async def test_rules_schedule_meeting(db_session: AsyncSession, org_id: int):
    response, tool = await _process_with_rules("schedule meeting with team tomorrow", db_session, org_id)
    assert tool == "schedule_meeting"
    assert "meeting" in response.lower() or "scheduled" in response.lower()


@pytest.mark.asyncio
async def test_rules_generate_report(db_session: AsyncSession, org_id: int):
    response, tool = await _process_with_rules("generate report for this month", db_session, org_id)
    assert tool == "generate_report"


@pytest.mark.asyncio
async def test_rules_summarize_document(db_session: AsyncSession, org_id: int):
    response, tool = await _process_with_rules("summarize this document about the project plan", db_session, org_id)
    assert tool == "summarize_document"
    assert "summary" in response.lower() or "document" in response.lower()


@pytest.mark.asyncio
async def test_rules_help(db_session: AsyncSession, org_id: int):
    response, tool = await _process_with_rules("help", db_session, org_id)
    assert tool is None
    assert "What I Can Do" in response or "help" in response.lower()


@pytest.mark.asyncio
async def test_rules_greeting(db_session: AsyncSession, org_id: int):
    response, tool = await _process_with_rules("hello", db_session, org_id)
    assert tool is None
    assert "Hello" in response or "hello" in response.lower()


# --- Helper function tests ---


def test_extract_after():
    result = _extract_after("create task buy milk", ["create task"])
    assert result == "buy milk"


def test_extract_after_no_match():
    result = _extract_after("random text", ["create task"])
    assert result == ""


def test_extract_number():
    assert _extract_number("complete task 42") == 42


def test_extract_number_none():
    assert _extract_number("no numbers here") is None


def test_extract_dollar_amount():
    assert _extract_dollar_amount("expense $50.75 for lunch") == 50.75


def test_extract_dollar_amount_no_dollar_sign():
    assert _extract_dollar_amount("expense 100 for travel") == 100.0


def test_extract_dollar_amount_none():
    assert _extract_dollar_amount("no amount") is None


def test_extract_email_address():
    assert _extract_email_address("send to user@example.com please") == "user@example.com"


def test_extract_email_address_none():
    assert _extract_email_address("no email here") is None
