from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Email
from app.schemas import EmailCreate, EmailOut

router = APIRouter(prefix="/api/emails", tags=["emails"])


@router.get("", response_model=list[EmailOut])
async def list_emails(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Email).order_by(Email.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=EmailOut)
async def create_email(email: EmailCreate, db: AsyncSession = Depends(get_db)):
    db_email = Email(
        to_address=email.to_address,
        subject=email.subject,
        body=email.body,
        status=email.status,
    )
    db.add(db_email)
    await db.commit()
    await db.refresh(db_email)
    return db_email


@router.delete("/{email_id}")
async def delete_email(email_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Email).where(Email.id == email_id))
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    await db.delete(email)
    await db.commit()
    return {"message": "Email deleted"}
