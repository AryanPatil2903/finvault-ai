"""
Expense CRUD endpoints with filtering, pagination, and category aggregation.
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user
from api.schemas import ExpenseCreateRequest, ExpenseResponse, ExpenseUpdateRequest
from database.connection import get_db
from database.models import Expense, User

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    body: ExpenseCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Expense:
    """Add a new expense transaction for the authenticated user."""
    expense = Expense(
        user_id=current_user.id,
        amount=body.amount,
        category=body.category,
        description=body.description,
        transaction_date=body.transaction_date,
        payment_method=body.payment_method,
        tags=body.tags,
        is_recurring=body.is_recurring,
    )
    db.add(expense)
    await db.flush()
    return expense


@router.get("", response_model=List[ExpenseResponse])
async def list_expenses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> List[Expense]:
    """
    List expenses with optional filtering by category and date range.
    Defaults to most recent 50 records.
    """
    filters = [Expense.user_id == current_user.id]

    if category:
        filters.append(Expense.category == category)
    if start_date:
        filters.append(Expense.transaction_date >= start_date)
    if end_date:
        filters.append(Expense.transaction_date <= end_date)

    result = await db.execute(
        select(Expense)
        .where(and_(*filters))
        .order_by(Expense.transaction_date.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Expense:
    """Fetch a single expense by ID (must belong to current user)."""
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id, Expense.user_id == current_user.id
        )
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found.")
    return expense


@router.patch("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    body: ExpenseUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Expense:
    """Partially update an expense record."""
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id, Expense.user_id == current_user.id
        )
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found.")

    # Apply only provided fields
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(expense, field, value)

    await db.flush()
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an expense record permanently."""
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id, Expense.user_id == current_user.id
        )
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found.")
    await db.delete(expense)