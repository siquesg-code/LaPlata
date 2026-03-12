from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent import process_message
from app.auth import get_current_active_user
from app.database import get_db
from app.models import ChatMessage, User
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    response_text, tool_used = await process_message(
        request.message, db, current_user.organization_id
    )
    return ChatResponse(role="assistant", content=response_text, tool_used=tool_used)


@router.get("/history", response_model=list[ChatResponse])
async def get_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.organization_id == current_user.organization_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [
        ChatResponse(
            role=m.role,
            content=m.content,
            tool_used=m.tool_used,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.delete("/history")
async def clear_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.organization_id == current_user.organization_id)
    )
    messages = result.scalars().all()
    for m in messages:
        await db.delete(m)
    await db.commit()
    return {"message": "Chat history cleared"}
