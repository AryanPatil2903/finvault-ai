"""
Dashboard summary endpoint — aggregates all financial data in one call.
Feeds the main dashboard page on the frontend.
"""

from datetime import date
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user
from database.connection import get_db
from database.models import Budget, Expense, Income, Loan, User
from src.ai_advisor import advisor
from src.analytics import (
    compute_budget_utilisation,
    compute_income_vs_expense_chart,
    get_top_expenses,
)
from src.finance import calculate_foir
from src.notifications import get_budget_warnings, get_upcoming_emi_alerts

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    include_ai: bool = True,
) -> Dict[str, Any]:
    """
    Aggregate dashboard data in a single API call:
    - Monthly income/expense totals
    - Active loans and EMI burden
    - FOIR
    - Upcoming EMI alerts
    - Budget utilisation warnings
    - Top expense categories
    - Income vs expense trend (6 months)
    - Optional AI insight
    """
    today = date.today()
    month_start = today.replace(day=1)

    # ── Monthly Expenses ──────────────────────────────────────────────────
    exp_result = await db.execute(
        select(Expense).where(
            and_(
                Expense.user_id == current_user.id,
                Expense.transaction_date >= month_start,
                Expense.transaction_date <= today,
            )
        )
    )
    expenses_this_month = list(exp_result.scalars().all())
    total_expenses = sum(e.amount for e in expenses_this_month)

    # ── Monthly Income ────────────────────────────────────────────────────
    inc_result = await db.execute(
        select(Income).where(
            and_(
                Income.user_id == current_user.id,
                Income.transaction_date >= month_start,
                Income.transaction_date <= today,
            )
        )
    )
    incomes_this_month = list(inc_result.scalars().all())
    total_income = sum(i.amount for i in incomes_this_month)

    # ── Active Loans ──────────────────────────────────────────────────────
    loans_result = await db.execute(
        select(Loan).where(
            Loan.user_id == current_user.id, Loan.status == "Active"
        )
    )
    active_loans = list(loans_result.scalars().all())
    total_outstanding = sum(l.outstanding_amount for l in active_loans)
    total_monthly_emi = sum(l.emi_amount for l in active_loans)

    # ── FOIR ──────────────────────────────────────────────────────────────
    foir = calculate_foir(total_monthly_emi, current_user.monthly_income or total_income)

    # ── Budgets ───────────────────────────────────────────────────────────
    budgets_result = await db.execute(
        select(Budget).where(
            and_(
                Budget.user_id == current_user.id,
                Budget.month == today.month,
                Budget.year == today.year,
            )
        )
    )
    budgets = [{"category": b.category, "amount": b.amount} for b in budgets_result.scalars()]
    expenses_dicts = [{"category": e.category, "amount": e.amount, "transaction_date": e.transaction_date} for e in expenses_this_month]

    budget_util = compute_budget_utilisation(budgets, expenses_dicts, today.month, today.year)

    # ── 6-Month Trend ─────────────────────────────────────────────────────
    all_exp_result = await db.execute(
        select(Expense).where(Expense.user_id == current_user.id)
    )
    all_expenses = [{"amount": e.amount, "transaction_date": e.transaction_date, "category": e.category}
                    for e in all_exp_result.scalars()]

    all_inc_result = await db.execute(
        select(Income).where(Income.user_id == current_user.id)
    )
    all_incomes = [{"amount": i.amount, "transaction_date": i.transaction_date}
                   for i in all_inc_result.scalars()]

    trend = compute_income_vs_expense_chart(all_expenses, all_incomes)
    top_cats = get_top_expenses(expenses_dicts)

    # ── Alerts ────────────────────────────────────────────────────────────
    loans_dicts = [
        {"id": l.id, "loan_name": l.loan_name, "lender_name": l.lender_name,
         "emi_amount": l.emi_amount, "emi_due_day": l.emi_due_day, "status": l.status}
        for l in active_loans
    ]
    emi_alerts = get_upcoming_emi_alerts(loans_dicts)
    budget_warnings = get_budget_warnings(budget_util)

    # ── Optional AI Insight ───────────────────────────────────────────────
    ai_insight = None
    if include_ai:
        user_data = {
            "summary": {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net_savings": total_income - total_expenses,
                "savings_rate": round(((total_income - total_expenses) / total_income * 100) if total_income else 0, 2),
            },
            "loans": [{"loan_name": l.loan_name, "loan_type": l.loan_type,
                        "outstanding_amount": l.outstanding_amount, "emi_amount": l.emi_amount,
                        "annual_interest_rate": l.annual_interest_rate,
                        "total_emis_remaining": l.total_emis_remaining} for l in active_loans],
            "top_categories": {c["category"]: c["amount"] for c in top_cats},
            "foir": foir,
        }
        ai_insight = await advisor.generate_financial_insight(user_data)

    net_savings = round(total_income - total_expenses, 2)
    savings_rate = round((net_savings / total_income * 100) if total_income > 0 else 0, 2)

    return {
        "total_income_this_month": round(total_income, 2),
        "total_expenses_this_month": round(total_expenses, 2),
        "net_savings_this_month": net_savings,
        "savings_rate": savings_rate,
        "total_active_loans": len(active_loans),
        "total_outstanding_debt": round(total_outstanding, 2),
        "total_monthly_emi": round(total_monthly_emi, 2),
        "foir": foir,
        "upcoming_emi_alerts": emi_alerts,
        "budget_warnings": budget_warnings,
        "top_expense_categories": top_cats,
        "income_expense_trend": trend,
        "ai_insight": ai_insight,
    }