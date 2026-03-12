from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Report
from app.schemas import ReportCreate, ReportOut

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("", response_model=list[ReportOut])
async def list_reports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).order_by(Report.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=ReportOut)
async def create_report(report: ReportCreate, db: AsyncSession = Depends(get_db)):
    db_report = Report(
        title=report.title,
        content=report.content,
        report_type=report.report_type,
    )
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)
    return db_report
