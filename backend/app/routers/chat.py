from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ChatMessage
from app.schemas import ChatRequest, ChatResponse
from app.agent import process_message

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    response_text, tool_used = await process_message(request.message, db)
    return ChatResponse(role="assistant", content=response_text, tool_used=tool_used)


@router.get("/history", response_model=list[ChatResponse])
async def get_history(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage).order_by(ChatMessage.created_at.asc()).limit(limit)
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
async def clear_history(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatMessage))
    messages = result.scalars().all()
    for m in messages:
        await db.delete(m)
    await db.commit()
    return {"message": "Chat history cleared"}
