from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Document
from app.schemas import DocumentCreate, DocumentOut

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=list[DocumentOut])
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=DocumentOut)
async def create_document(doc: DocumentCreate, db: AsyncSession = Depends(get_db)):
    db_doc = Document(
        title=doc.title,
        content=doc.content,
        summary=doc.summary,
        doc_type=doc.doc_type,
    )
    db.add(db_doc)
    await db.commit()
    await db.refresh(db_doc)
    return db_doc


@router.delete("/{doc_id}")
async def delete_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)
    await db.commit()
    return {"message": "Document deleted"}
