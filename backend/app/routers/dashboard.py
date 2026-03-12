from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Document, Email, Expense, Meeting, Report, Task, User
from app.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    org_id = current_user.organization_id

    task_total = (await db.execute(
        select(func.count(Task.id)).where(Task.organization_id == org_id)
    )).scalar() or 0
    task_done = (await db.execute(
        select(func.count(Task.id)).where(Task.status == "done", Task.organization_id == org_id)
    )).scalar() or 0

    expense_result = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.organization_id == org_id)
    )
    expense_total = expense_result.scalar() or 0

    email_count = (await db.execute(
        select(func.count(Email.id)).where(Email.organization_id == org_id)
    )).scalar() or 0
    meeting_count = (await db.execute(
        select(func.count(Meeting.id)).where(
            Meeting.meeting_date >= date.today(), Meeting.organization_id == org_id
        )
    )).scalar() or 0
    doc_count = (await db.execute(
        select(func.count(Document.id)).where(Document.organization_id == org_id)
    )).scalar() or 0
    report_count = (await db.execute(
        select(func.count(Report.id)).where(Report.organization_id == org_id)
    )).scalar() or 0

    return DashboardStats(
        total_tasks=task_total,
        completed_tasks=task_done,
        pending_tasks=task_total - task_done,
        total_expenses=expense_total,
        total_emails=email_count,
        upcoming_meetings=meeting_count,
        total_documents=doc_count,
        total_reports=report_count,
    )
