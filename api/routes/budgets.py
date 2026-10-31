"""
Monthly budget endpoints (one budget per category per month).
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user
from api.schemas import BudgetCreateRequest, BudgetResponse
from database.connection import get_db
from database.models import Budget, User

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    body: BudgetCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Budget:
    """Create a budget; rejects duplicates for the same category and month."""
    existing = await db.execute(
        select(Budget).where(
            Budget.user_id == current_user.id,
            Budget.category == body.category,
            Budget.month == body.month,
            Budget.year == body.year,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Budget already exists for this category and month.")

    budget = Budget(user_id=current_user.id, **body.model_dump())
    db.add(budget)
    await db.flush()
    return budget


@router.get("", response_model=List[BudgetResponse])
async def list_budgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Budget]:
    """List all budgets for the current user."""
    result = await db.execute(
        select(Budget).where(Budget.user_id == current_user.id)
        .order_by(Budget.year.desc(), Budget.month.desc())
    )
    return list(result.scalars().all())


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a budget."""
    result = await db.execute(
        select(Budget).where(Budget.id == budget_id, Budget.user_id == current_user.id)
    )
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found.")
    await db.delete(budget)