import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_active_user
from app.config import settings
from app.database import get_db
from app.models import Email, User
from app.schemas import EmailCreate, EmailOut

router = APIRouter(prefix="/api/emails", tags=["emails"])


@router.get("", response_model=list[EmailOut])
async def list_emails(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Email).where(Email.organization_id == current_user.organization_id)
        .order_by(Email.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=EmailOut)
async def create_email(
    email: EmailCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_email = Email(
        to_address=email.to_address,
        subject=email.subject,
        body=email.body,
        status=email.status,
        organization_id=current_user.organization_id,
    )
    db.add(db_email)
    await db.commit()
    await db.refresh(db_email)
    return db_email


@router.post("/{email_id}/send", response_model=EmailOut)
async def send_email(
    email_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Email).where(Email.id == email_id, Email.organization_id == current_user.organization_id)
    )
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    if not settings.smtp_host or not settings.smtp_from_address:
        raise HTTPException(
            status_code=400,
            detail="SMTP is not configured. Set SMTP_HOST, SMTP_FROM_ADDRESS, and other SMTP env vars.",
        )

    msg = MIMEMultipart()
    msg["From"] = settings.smtp_from_address
    msg["To"] = email.to_address
    msg["Subject"] = email.subject
    msg.attach(MIMEText(email.body, "plain"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_address, email.to_address, msg.as_string())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to send email: {exc}")

    email.status = "sent"
    await db.commit()
    await db.refresh(email)
    return email


@router.delete("/{email_id}")
async def delete_email(
    email_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Email).where(Email.id == email_id, Email.organization_id == current_user.organization_id)
    )
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    await db.delete(email)
    await db.commit()
    return {"message": "Email deleted"}
