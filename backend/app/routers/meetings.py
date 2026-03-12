from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Meeting, User
from app.schemas import MeetingCreate, MeetingOut

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.get("", response_model=list[MeetingOut])
async def list_meetings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Meeting).where(Meeting.organization_id == current_user.organization_id)
        .order_by(Meeting.meeting_date.asc())
    )
    return result.scalars().all()


@router.post("", response_model=MeetingOut)
async def create_meeting(
    meeting: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_meeting = Meeting(
        title=meeting.title,
        description=meeting.description,
        attendees=meeting.attendees,
        meeting_date=meeting.meeting_date,
        meeting_time=meeting.meeting_time,
        duration_minutes=meeting.duration_minutes,
        location=meeting.location,
        organization_id=current_user.organization_id,
    )
    db.add(db_meeting)
    await db.commit()
    await db.refresh(db_meeting)
    return db_meeting


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.organization_id == current_user.organization_id)
    )
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await db.delete(meeting)
    await db.commit()
    return {"message": "Meeting deleted"}
