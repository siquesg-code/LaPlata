"""AI Agent that processes natural language requests and performs business operations."""

import json
import re
from datetime import date, datetime, timedelta, timezone
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import (
    ChatMessage,
    Document,
    Email,
    Expense,
    Meeting,
    Report,
    Task,
)

SYSTEM_PROMPT = """You are an AI business administration assistant. You help users manage their business operations efficiently.

You have access to these tools:
1. create_task - Create a new task (params: title, description, priority, due_date, assignee)
2. list_tasks - List all tasks (params: status filter optional)
3. update_task - Update a task (params: task_id, fields to update)
4. complete_task - Mark a task as done (params: task_id)
5. draft_email - Draft a professional email (params: to_address, subject, body)
6. add_expense - Log an expense (params: description, amount, category, vendor)
7. summarize_document - Summarize a document (params: title, content)
8. schedule_meeting - Schedule a meeting (params: title, description, attendees, meeting_date, meeting_time, duration_minutes, location)
9. generate_report - Generate a business report (params: title, report_type)
10. get_dashboard - Get business dashboard summary

When the user asks you to do something, determine which tool to use and call it with appropriate parameters. 
Always respond helpfully and professionally. If you need more information, ask for it.
Format your responses in a clear, organized way. Use markdown formatting when helpful."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                    "due_date": {"type": "string", "description": "Due date in YYYY-MM-DD format"},
                    "assignee": {"type": "string", "description": "Person assigned to the task"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks, optionally filtered by status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["todo", "in_progress", "done"]},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID of the task to update"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string", "enum": ["todo", "in_progress", "done"]},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                    "due_date": {"type": "string"},
                    "assignee": {"type": "string"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID of the task to complete"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_email",
            "description": "Draft a professional email",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_address": {"type": "string", "description": "Recipient email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"},
                },
                "required": ["to_address", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_expense",
            "description": "Log a new expense",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Expense description"},
                    "amount": {"type": "number", "description": "Amount in dollars"},
                    "category": {"type": "string", "enum": ["travel", "office", "software", "marketing", "salary", "utilities", "other"]},
                    "vendor": {"type": "string", "description": "Vendor or supplier name"},
                },
                "required": ["description", "amount"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_document",
            "description": "Save and summarize a document",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title"},
                    "content": {"type": "string", "description": "Document content to summarize"},
                    "doc_type": {"type": "string", "description": "Type of document"},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Schedule a new meeting",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Meeting title"},
                    "description": {"type": "string", "description": "Meeting description/agenda"},
                    "attendees": {"type": "string", "description": "Comma-separated list of attendees"},
                    "meeting_date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "meeting_time": {"type": "string", "description": "Time in HH:MM format"},
                    "duration_minutes": {"type": "integer", "description": "Duration in minutes"},
                    "location": {"type": "string", "description": "Meeting location or link"},
                },
                "required": ["title", "meeting_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_report",
            "description": "Generate a business report",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Report title"},
                    "report_type": {"type": "string", "enum": ["expense", "task", "meeting", "general"], "description": "Type of report"},
                },
                "required": ["title", "report_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dashboard",
            "description": "Get a summary of all business metrics and stats",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]


async def execute_tool(tool_name: str, args: dict[str, Any], db: AsyncSession, organization_id: int) -> str:
    """Execute a tool and return the result as a string."""
    if tool_name == "create_task":
        return await _create_task(db, args, organization_id)
    elif tool_name == "list_tasks":
        return await _list_tasks(db, args, organization_id)
    elif tool_name == "update_task":
        return await _update_task(db, args, organization_id)
    elif tool_name == "complete_task":
        return await _complete_task(db, args, organization_id)
    elif tool_name == "draft_email":
        return await _draft_email(db, args, organization_id)
    elif tool_name == "add_expense":
        return await _add_expense(db, args, organization_id)
    elif tool_name == "summarize_document":
        return await _summarize_document(db, args, organization_id)
    elif tool_name == "schedule_meeting":
        return await _schedule_meeting(db, args, organization_id)
    elif tool_name == "generate_report":
        return await _generate_report(db, args, organization_id)
    elif tool_name == "get_dashboard":
        return await _get_dashboard(db, organization_id)
    else:
        return f"Unknown tool: {tool_name}"


async def _create_task(db: AsyncSession, args: dict[str, Any], organization_id: int) -> str:
    due = None
    if args.get("due_date"):
        try:
            due = date.fromisoformat(args["due_date"])
        except ValueError:
            due = None
    task = Task(
        title=args["title"],
        description=args.get("description", ""),
        priority=args.get("priority", "medium"),
        due_date=due,
        assignee=args.get("assignee"),
        organization_id=organization_id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return json.dumps({
        "success": True,
        "task": {"id": task.id, "title": task.title, "priority": task.priority, "status": task.status},
    })


async def _list_tasks(db: AsyncSession, args: dict[str, Any], organization_id: int) -> str:
    query = select(Task).where(Task.organization_id == organization_id).order_by(Task.created_at.desc())
    status = args.get("status")
    if status:
        query = query.where(Task.status == status)
    result = await db.execute(query)
    tasks = result.scalars().all()
    task_list = [
        {
            "id": t.id, "title": t.title, "status": t.status,
            "priority": t.priority, "due_date": str(t.due_date) if t.due_date else None,
            "assignee": t.assignee,
        }
        for t in tasks
    ]
    return json.dumps({"tasks": task_list, "count": len(task_list)})


async def _update_task(db: AsyncSession, args: dict[str, Any], organization_id: int) -> str:
    task_id = args.pop("task_id")
    result = await db.execute(select(Task).where(Task.id == task_id, Task.organization_id == organization_id))
    task = result.scalar_one_or_none()
    if not task:
        return json.dumps({"success": False, "error": f"Task {task_id} not found"})
    for key, value in args.items():
        if key == "due_date" and value:
            try:
                value = date.fromisoformat(value)
            except ValueError:
                continue
        if hasattr(task, key):
            setattr(task, key, value)
    task.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return json.dumps({"success": True, "message": f"Task {task_id} updated"})


async def _complete_task(db: AsyncSession, args: dict[str, Any], organization_id: int) -> str:
    task_id = args["task_id"]
    result = await db.execute(select(Task).where(Task.id == task_id, Task.organization_id == organization_id))
    task = result.scalar_one_or_none()
    if not task:
        return json.dumps({"success": False, "error": f"Task {task_id} not found"})
    task.status = "done"
    task.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return json.dumps({"success": True, "message": f"Task '{task.title}' marked as completed"})


async def _draft_email(db: AsyncSession, args: dict[str, Any], organization_id: int) -> str:
    email = Email(
        to_address=args["to_address"],
        subject=args["subject"],
        body=args["body"],
        organization_id=organization_id,
    )
    db.add(email)
    await db.commit()
    await db.refresh(email)
    return json.dumps({
        "success": True,
        "email": {"id": email.id, "to": email.to_address, "subject": email.subject},
    })


async def _add_expense(db: AsyncSession, args: dict[str, Any], organization_id: int) -> str:
    exp_date = None
    if args.get("expense_date"):
        try:
            exp_date = date.fromisoformat(args["expense_date"])
        except ValueError:
            exp_date = date.today()
    else:
        exp_date = date.today()
    expense = Expense(
        description=args["description"],
        amount=args["amount"],
        category=args.get("category", "other"),
        expense_date=exp_date,
        vendor=args.get("vendor"),
        organization_id=organization_id,
    )
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return json.dumps({
        "success": True,
        "expense": {"id": expense.id, "description": expense.description, "amount": expense.amount, "category": expense.category},
    })


async def _summarize_document(db: AsyncSession, args: dict[str, Any], organization_id: int) -> str:
    content = args["content"]

    summary = ""
    if settings.openai_api_key:
        try:
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Summarize the following document concisely in 2-3 sentences."},
                    {"role": "user", "content": content},
                ],
            )
            summary = response.choices[0].message.content or ""
        except Exception:
            summary = ""

    if not summary:
        sentences = content.replace("\n", " ").split(".")
        sentences = [s.strip() for s in sentences if s.strip()]
        summary = ". ".join(sentences[:3]) + "." if sentences else "No content to summarize."

    doc = Document(
        title=args["title"],
        content=content,
        summary=summary,
        doc_type=args.get("doc_type", "general"),
        organization_id=organization_id,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return json.dumps({
        "success": True,
        "document": {"id": doc.id, "title": doc.title, "summary": doc.summary},
    })


async def _schedule_meeting(db: AsyncSession, args: dict[str, Any], organization_id: int) -> str:
    try:
        m_date = date.fromisoformat(args["meeting_date"])
    except ValueError:
        m_date = date.today() + timedelta(days=1)
    meeting = Meeting(
        title=args["title"],
        description=args.get("description", ""),
        attendees=args.get("attendees", ""),
        meeting_date=m_date,
        meeting_time=args.get("meeting_time", "10:00"),
        duration_minutes=args.get("duration_minutes", 60),
        location=args.get("location", ""),
        organization_id=organization_id,
    )
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    return json.dumps({
        "success": True,
        "meeting": {
            "id": meeting.id, "title": meeting.title,
            "date": str(meeting.meeting_date), "time": meeting.meeting_time,
        },
    })


async def _generate_report(db: AsyncSession, args: dict[str, Any], organization_id: int) -> str:
    report_type = args.get("report_type", "general")
    title = args["title"]
    content_parts: list[str] = [f"# {title}\n", f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"]

    if report_type == "expense":
        result = await db.execute(select(Expense).where(Expense.organization_id == organization_id))
        expenses = result.scalars().all()
        total = sum(e.amount for e in expenses)
        content_parts.append(f"## Expense Summary\n- **Total Expenses:** ${total:,.2f}\n- **Number of Entries:** {len(expenses)}\n")
        by_cat: dict[str, float] = {}
        for e in expenses:
            by_cat[e.category] = by_cat.get(e.category, 0) + e.amount
        if by_cat:
            content_parts.append("### By Category\n")
            for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
                content_parts.append(f"- **{cat.title()}:** ${amt:,.2f}\n")

    elif report_type == "task":
        result = await db.execute(select(Task).where(Task.organization_id == organization_id))
        tasks = result.scalars().all()
        total = len(tasks)
        done = sum(1 for t in tasks if t.status == "done")
        in_prog = sum(1 for t in tasks if t.status == "in_progress")
        todo = sum(1 for t in tasks if t.status == "todo")
        content_parts.append(f"## Task Summary\n- **Total Tasks:** {total}\n- **Completed:** {done}\n- **In Progress:** {in_prog}\n- **To Do:** {todo}\n")
        completion_rate = (done / total * 100) if total > 0 else 0
        content_parts.append(f"- **Completion Rate:** {completion_rate:.1f}%\n")

    elif report_type == "meeting":
        result = await db.execute(select(Meeting).where(Meeting.organization_id == organization_id).order_by(Meeting.meeting_date))
        meetings = result.scalars().all()
        content_parts.append(f"## Meeting Summary\n- **Total Meetings:** {len(meetings)}\n")
        upcoming = [m for m in meetings if m.meeting_date >= date.today()]
        content_parts.append(f"- **Upcoming:** {len(upcoming)}\n")
        if upcoming[:5]:
            content_parts.append("\n### Next Meetings\n")
            for m in upcoming[:5]:
                content_parts.append(f"- **{m.title}** — {m.meeting_date} at {m.meeting_time}\n")

    else:
        # General overview
        task_count = (await db.execute(select(func.count(Task.id)).where(Task.organization_id == organization_id))).scalar() or 0
        expense_total_result = await db.execute(select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.organization_id == organization_id))
        expense_total = expense_total_result.scalar() or 0
        email_count = (await db.execute(select(func.count(Email.id)).where(Email.organization_id == organization_id))).scalar() or 0
        meeting_count = (await db.execute(select(func.count(Meeting.id)).where(Meeting.organization_id == organization_id))).scalar() or 0
        content_parts.append(f"## Business Overview\n- **Tasks:** {task_count}\n- **Total Expenses:** ${expense_total:,.2f}\n- **Emails Drafted:** {email_count}\n- **Meetings Scheduled:** {meeting_count}\n")

    report_content = "\n".join(content_parts)
    report = Report(title=title, content=report_content, report_type=report_type, organization_id=organization_id)
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return json.dumps({
        "success": True,
        "report": {"id": report.id, "title": report.title, "content": report_content},
    })


async def _get_dashboard(db: AsyncSession, organization_id: int) -> str:
    task_total = (await db.execute(select(func.count(Task.id)).where(Task.organization_id == organization_id))).scalar() or 0
    task_done = (await db.execute(select(func.count(Task.id)).where(Task.status == "done", Task.organization_id == organization_id))).scalar() or 0
    task_pending = task_total - task_done
    expense_total_result = await db.execute(select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.organization_id == organization_id))
    expense_total = expense_total_result.scalar() or 0
    email_count = (await db.execute(select(func.count(Email.id)).where(Email.organization_id == organization_id))).scalar() or 0
    meeting_count = (await db.execute(
        select(func.count(Meeting.id)).where(Meeting.meeting_date >= date.today(), Meeting.organization_id == organization_id)
    )).scalar() or 0
    doc_count = (await db.execute(select(func.count(Document.id)).where(Document.organization_id == organization_id))).scalar() or 0
    report_count = (await db.execute(select(func.count(Report.id)).where(Report.organization_id == organization_id))).scalar() or 0

    return json.dumps({
        "total_tasks": task_total,
        "completed_tasks": task_done,
        "pending_tasks": task_pending,
        "total_expenses": expense_total,
        "total_emails": email_count,
        "upcoming_meetings": meeting_count,
        "total_documents": doc_count,
        "total_reports": report_count,
    })


async def process_message(user_message: str, db: AsyncSession, organization_id: int) -> tuple[str, str | None]:
    """Process a user message and return (response_text, tool_used_or_none)."""
    # Save user message
    user_msg = ChatMessage(role="user", content=user_message, organization_id=organization_id)
    db.add(user_msg)
    await db.commit()

    tool_used = None
    response_text = ""

    if settings.openai_api_key:
        response_text, tool_used = await _process_with_openai(user_message, db, organization_id)
    else:
        response_text, tool_used = await _process_with_rules(user_message, db, organization_id)

    # Save assistant message
    assistant_msg = ChatMessage(role="assistant", content=response_text, tool_used=tool_used, organization_id=organization_id)
    db.add(assistant_msg)
    await db.commit()

    return response_text, tool_used


async def _process_with_openai(user_message: str, db: AsyncSession, organization_id: int) -> tuple[str, str | None]:
    """Use OpenAI function calling to process the message."""
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # Get recent chat history for context
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.organization_id == organization_id)
        .order_by(ChatMessage.created_at.desc()).limit(20)
    )
    history = list(reversed(result.scalars().all()))

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_message})

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if message.tool_calls:
            tool_call = message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            tool_result = await execute_tool(tool_name, tool_args, db, organization_id)

            # Get final response from OpenAI with tool result
            messages.append(message.model_dump())
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            })

            final_response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            return final_response.choices[0].message.content or "Done!", tool_name
        else:
            return message.content or "I'm here to help with your business tasks!", None

    except Exception as e:
        # Fallback to rules if OpenAI fails
        return await _process_with_rules(user_message, db, organization_id)


async def _process_with_rules(user_message: str, db: AsyncSession, organization_id: int) -> tuple[str, str | None]:
    """Rule-based fallback when no OpenAI key is available."""
    msg = user_message.lower().strip()

    # Dashboard / overview
    if any(kw in msg for kw in ["dashboard", "overview", "summary", "stats", "status"]):
        result = await execute_tool("get_dashboard", {}, db, organization_id)
        data = json.loads(result)
        response = (
            f"## Business Dashboard\n\n"
            f"- **Tasks:** {data['total_tasks']} total ({data['completed_tasks']} completed, {data['pending_tasks']} pending)\n"
            f"- **Expenses:** ${data['total_expenses']:,.2f}\n"
            f"- **Emails:** {data['total_emails']} drafted\n"
            f"- **Upcoming Meetings:** {data['upcoming_meetings']}\n"
            f"- **Documents:** {data['total_documents']}\n"
            f"- **Reports:** {data['total_reports']}\n"
        )
        return response, "get_dashboard"

    # Create task
    if any(kw in msg for kw in ["create task", "add task", "new task", "todo"]):
        title = _extract_after(msg, ["create task", "add task", "new task", "todo"])
        if not title or len(title) < 3:
            title = "New Task"
        # Detect priority
        priority = "medium"
        for p in ["urgent", "high", "low"]:
            if p in msg:
                priority = p
                break
        result = await execute_tool("create_task", {"title": title.strip().title(), "priority": priority}, db, organization_id)
        data = json.loads(result)
        if data["success"]:
            t = data["task"]
            return f"Task created successfully!\n\n- **ID:** {t['id']}\n- **Title:** {t['title']}\n- **Priority:** {t['priority']}\n- **Status:** {t['status']}", "create_task"
        return "Failed to create task.", "create_task"

    # List tasks
    if any(kw in msg for kw in ["list task", "show task", "my task", "all task", "tasks"]):
        status_filter = None
        if "done" in msg or "completed" in msg:
            status_filter = "done"
        elif "progress" in msg:
            status_filter = "in_progress"
        elif "todo" in msg or "pending" in msg:
            status_filter = "todo"
        args: dict[str, Any] = {}
        if status_filter:
            args["status"] = status_filter
        result = await execute_tool("list_tasks", args, db, organization_id)
        data = json.loads(result)
        if not data["tasks"]:
            return "No tasks found. Try creating one!", "list_tasks"
        lines = [f"## Tasks ({data['count']})\n"]
        for t in data["tasks"]:
            status_icon = {"todo": "⬜", "in_progress": "🔄", "done": "✅"}.get(t["status"], "⬜")
            lines.append(f"{status_icon} **{t['title']}** (ID: {t['id']}) — {t['priority']} priority")
            if t.get("due_date"):
                lines.append(f"   Due: {t['due_date']}")
        return "\n".join(lines), "list_tasks"

    # Complete task
    if any(kw in msg for kw in ["complete task", "finish task", "done task", "mark done", "mark complete"]):
        task_id = _extract_number(msg)
        if task_id:
            result = await execute_tool("complete_task", {"task_id": task_id}, db, organization_id)
            data = json.loads(result)
            return data.get("message", "Task updated!"), "complete_task"
        return "Please specify the task ID to complete. Example: 'Complete task 1'", "complete_task"

    # Draft email
    if any(kw in msg for kw in ["email", "draft email", "write email", "compose email", "send email"]):
        # Try to parse email details
        to_addr = _extract_email_address(msg) or "recipient@example.com"
        subject = _extract_after(msg, ["subject:", "about", "regarding"]) or "Follow-up"
        body = _extract_after(msg, ["body:", "saying", "content:"]) or "Thank you for your time. I wanted to follow up on our recent conversation."
        result = await execute_tool("draft_email", {
            "to_address": to_addr,
            "subject": subject.strip().title() if len(subject) < 100 else subject[:100],
            "body": body.strip(),
        }, db, organization_id)
        data = json.loads(result)
        if data["success"]:
            e = data["email"]
            return f"Email drafted successfully!\n\n- **To:** {e['to']}\n- **Subject:** {e['subject']}\n- **ID:** {e['id']}\n\nYou can view and edit it in the Emails section.", "draft_email"
        return "Failed to draft email.", "draft_email"

    # Add expense
    if any(kw in msg for kw in ["expense", "cost", "spent", "payment", "paid"]):
        amount = _extract_dollar_amount(msg) or 0
        desc = _extract_after(msg, ["expense", "for", "on"]) or "Business expense"
        category = "other"
        for cat in ["travel", "office", "software", "marketing", "salary", "utilities"]:
            if cat in msg:
                category = cat
                break
        if amount > 0:
            result = await execute_tool("add_expense", {
                "description": desc.strip().title(),
                "amount": amount,
                "category": category,
            }, db, organization_id)
            data = json.loads(result)
            if data["success"]:
                exp = data["expense"]
                return f"Expense logged!\n\n- **Description:** {exp['description']}\n- **Amount:** ${exp['amount']:,.2f}\n- **Category:** {exp['category'].title()}", "add_expense"
        return "Please specify the amount. Example: 'Add expense $50 for office supplies'", "add_expense"

    # Schedule meeting
    if any(kw in msg for kw in ["meeting", "schedule", "appointment", "call"]):
        title = _extract_after(msg, ["meeting", "schedule", "appointment", "call"]) or "Team Meeting"
        meeting_date = str(date.today() + timedelta(days=1))
        # Try to find a date mention
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", msg)
        if date_match:
            meeting_date = date_match.group(1)
        elif "tomorrow" in msg:
            meeting_date = str(date.today() + timedelta(days=1))
        elif "next week" in msg:
            meeting_date = str(date.today() + timedelta(days=7))

        result = await execute_tool("schedule_meeting", {
            "title": title.strip().title(),
            "meeting_date": meeting_date,
            "meeting_time": "10:00",
        }, db, organization_id)
        data = json.loads(result)
        if data["success"]:
            m = data["meeting"]
            return f"Meeting scheduled!\n\n- **Title:** {m['title']}\n- **Date:** {m['date']}\n- **Time:** {m['time']}\n- **ID:** {m['id']}", "schedule_meeting"
        return "Failed to schedule meeting.", "schedule_meeting"

    # Generate report
    if any(kw in msg for kw in ["report", "generate report", "create report"]):
        report_type = "general"
        for rt in ["expense", "task", "meeting"]:
            if rt in msg:
                report_type = rt
                break
        title = f"{report_type.title()} Report — {date.today().strftime('%B %Y')}"
        result = await execute_tool("generate_report", {
            "title": title,
            "report_type": report_type,
        }, db, organization_id)
        data = json.loads(result)
        if data["success"]:
            return data["report"]["content"], "generate_report"
        return "Failed to generate report.", "generate_report"

    # Summarize document
    if any(kw in msg for kw in ["summarize", "document", "summary of"]):
        content = _extract_after(msg, ["summarize", "document"]) or msg
        result = await execute_tool("summarize_document", {
            "title": f"Document — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            "content": content,
        }, db, organization_id)
        data = json.loads(result)
        if data["success"]:
            return f"**Document saved and summarized!**\n\n**Summary:** {data['document']['summary']}", "summarize_document"
        return "Failed to summarize document.", "summarize_document"

    # Help / default
    if any(kw in msg for kw in ["help", "what can you", "commands", "features"]):
        return (
            "## What I Can Do\n\n"
            "I'm your AI business administration assistant! Here's what I can help with:\n\n"
            "- **Task Management** — Create, list, update, and complete tasks\n"
            "- **Email Drafting** — Compose professional emails\n"
            "- **Expense Tracking** — Log and categorize business expenses\n"
            "- **Meeting Scheduling** — Schedule and manage meetings\n"
            "- **Document Summarization** — Summarize documents and text\n"
            "- **Report Generation** — Generate expense, task, or meeting reports\n"
            "- **Dashboard** — View a business overview\n\n"
            "Try saying things like:\n"
            '- "Create task Review Q1 budget"\n'
            '- "Add expense $150 for office supplies"\n'
            '- "Schedule meeting with team tomorrow"\n'
            '- "Show me my dashboard"\n'
            '- "Generate expense report"\n'
        ), None

    # Greeting
    if any(kw in msg for kw in ["hello", "hi", "hey", "good morning", "good afternoon"]):
        return (
            "Hello! I'm your AI Business Admin Assistant. I can help you manage tasks, "
            "draft emails, track expenses, schedule meetings, and more. "
            "Type **help** to see everything I can do, or just tell me what you need!"
        ), None

    # Default
    return (
        "I'd be happy to help! Here are some things I can do:\n\n"
        "- **Create/manage tasks** — 'Create task ...'\n"
        "- **Draft emails** — 'Draft email to ...'\n"
        "- **Track expenses** — 'Add expense $100 for ...'\n"
        "- **Schedule meetings** — 'Schedule meeting ...'\n"
        "- **View dashboard** — 'Show dashboard'\n"
        "- **Generate reports** — 'Generate expense report'\n\n"
        "What would you like to do?"
    ), None


def _extract_after(text: str, keywords: list[str]) -> str:
    """Extract text after the first matching keyword."""
    for kw in keywords:
        idx = text.find(kw)
        if idx >= 0:
            return text[idx + len(kw):].strip().strip('"').strip("'")
    return ""


def _extract_number(text: str) -> int | None:
    """Extract the first number from text."""
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


def _extract_dollar_amount(text: str) -> float | None:
    """Extract dollar amount from text."""
    match = re.search(r"\$?([\d,]+\.?\d*)", text)
    if match:
        try:
            return float(match.group(1).replace(",", ""))
        except ValueError:
            return None
    return None


def _extract_email_address(text: str) -> str | None:
    """Extract email address from text."""
    match = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
    return match.group() if match else None
