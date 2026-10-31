"""
Income CRUD endpoints with date-range filtering.
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user
from api.schemas import IncomeCreateRequest, IncomeResponse
from database.connection import get_db
from database.models import Income, User

router = APIRouter(prefix="/incomes", tags=["Incomes"])


@router.post("", response_model=IncomeResponse, status_code=status.HTTP_201_CREATED)
async def create_income(
    body: IncomeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Income:
    """Record a new income transaction."""
    income = Income(user_id=current_user.id, **body.model_dump())
    db.add(income)
    await db.flush()
    return income


@router.get("", response_model=List[IncomeResponse])
async def list_incomes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=500),
) -> List[Income]:
    """List incomes, newest first, optionally filtered by date range."""
    filters = [Income.user_id == current_user.id]
    if start_date:
        filters.append(Income.transaction_date >= start_date)
    if end_date:
        filters.append(Income.transaction_date <= end_date)

    result = await db.execute(
        select(Income)
        .where(and_(*filters))
        .order_by(Income.transaction_date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income(
    income_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an income record (must belong to the current user)."""
    result = await db.execute(
        select(Income).where(Income.id == income_id, Income.user_id == current_user.id)
    )
    income = result.scalar_one_or_none()
    if not income:
        raise HTTPException(status_code=404, detail="Income not found.")
    await db.delete(income)