from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Meeting
from app.schemas import MeetingCreate, MeetingOut

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.get("", response_model=list[MeetingOut])
async def list_meetings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Meeting).order_by(Meeting.meeting_date.asc()))
    return result.scalars().all()


@router.post("", response_model=MeetingOut)
async def create_meeting(meeting: MeetingCreate, db: AsyncSession = Depends(get_db)):
    db_meeting = Meeting(
        title=meeting.title,
        description=meeting.description,
        attendees=meeting.attendees,
        meeting_date=meeting.meeting_date,
        meeting_time=meeting.meeting_time,
        duration_minutes=meeting.duration_minutes,
        location=meeting.location,
    )
    db.add(db_meeting)
    await db.commit()
    await db.refresh(db_meeting)
    return db_meeting


@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await db.delete(meeting)
    await db.commit()
    return {"message": "Meeting deleted"}
