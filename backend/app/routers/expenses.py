from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Expense, User
from app.schemas import ExpenseCreate, ExpenseOut, ExpenseSummary

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.get("", response_model=list[ExpenseOut])
async def list_expenses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Expense).where(Expense.organization_id == current_user.organization_id)
        .order_by(Expense.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ExpenseOut)
async def create_expense(
    expense: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_expense = Expense(
        description=expense.description,
        amount=expense.amount,
        category=expense.category,
        expense_date=expense.expense_date or date.today(),
        vendor=expense.vendor,
        organization_id=current_user.organization_id,
    )
    db.add(db_expense)
    await db.commit()
    await db.refresh(db_expense)
    return db_expense


@router.get("/summary", response_model=ExpenseSummary)
async def expense_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Expense).where(Expense.organization_id == current_user.organization_id)
    )
    expenses = result.scalars().all()
    total = sum(e.amount for e in expenses)
    by_category: dict[str, float] = {}
    for e in expenses:
        by_category[e.category] = by_category.get(e.category, 0) + e.amount
    return ExpenseSummary(total=total, by_category=by_category, count=len(expenses))


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id, Expense.organization_id == current_user.organization_id)
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    await db.delete(expense)
    await db.commit()
    return {"message": "Expense deleted"}
