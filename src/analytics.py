"""
Analytics engine — spending trends, budget utilisation, income vs expense
comparisons, and monthly breakdowns for dashboard and reports.
"""

from collections import defaultdict
from datetime import date, timedelta
from typing import Any, Dict, List, Tuple

from config.finance_config import ANALYTICS_LOOKBACK_MONTHS, TOP_N_EXPENSE_CATEGORIES
from config.logging_config import get_logger

logger = get_logger("analytics")


def get_month_range(year: int, month: int) -> Tuple[date, date]:
    """Return (first_day, last_day) for a given year-month."""
    first = date(year, month, 1)
    # Find last day by going to first day of next month, minus 1
    if month == 12:
        last = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    return first, last


def compute_category_breakdown(
    transactions: List[Dict[str, Any]]
) -> Dict[str, float]:
    """
    Aggregate transaction amounts by category.

    Args:
        transactions: List of dicts with keys: category, amount.

    Returns:
        Dict mapping category → total amount, sorted descending.
    """
    totals: Dict[str, float] = defaultdict(float)
    for tx in transactions:
        totals[tx["category"]] += tx["amount"]

    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


def compute_monthly_trend(
    transactions: List[Dict[str, Any]],
    months: int = ANALYTICS_LOOKBACK_MONTHS,
) -> List[Dict[str, Any]]:
    """
    Compute per-month totals for the last N months.

    Args:
        transactions: List of dicts with keys: transaction_date (date), amount.
        months:       How many months back to include.

    Returns:
        List of {"month": "Jan 2025", "total": float} dicts, oldest-first.
    """
    today = date.today()
    monthly: Dict[Tuple[int, int], float] = defaultdict(float)

    cutoff = date(today.year, today.month, 1)
    for _ in range(months - 1):
        cutoff = (cutoff - timedelta(days=1)).replace(day=1)

    for tx in transactions:
        tx_date = tx["transaction_date"]
        if isinstance(tx_date, str):
            tx_date = date.fromisoformat(tx_date)
        key = (tx_date.year, tx_date.month)
        first, _ = get_month_range(*key)
        if first >= cutoff:
            monthly[key] += tx["amount"]

    # Build sorted list from oldest to newest
    import calendar
    result = []
    for (year, month) in sorted(monthly.keys()):
        result.append({
            "month": f"{calendar.month_abbr[month]} {year}",
            "year": year,
            "month_num": month,
            "total": round(monthly[(year, month)], 2),
        })
    return result


def compute_savings_rate(total_income: float, total_expenses: float) -> float:
    """Return savings rate as percentage. Returns 0.0 if income is zero."""
    if total_income <= 0:
        return 0.0
    savings = total_income - total_expenses
    return round((savings / total_income) * 100, 2)


def compute_budget_utilisation(
    budgets: List[Dict[str, Any]],
    expenses: List[Dict[str, Any]],
    month: int,
    year: int,
) -> List[Dict[str, Any]]:
    """
    For each budget in the given month, compute spent and remaining.

    Args:
        budgets:  Budget records for the month (category, amount).
        expenses: All expense records for the month.
        month, year: Target period.

    Returns:
        List of dicts: category, budgeted, spent, remaining, utilisation_pct.
    """
    # Filter expenses to the target month
    first, last = get_month_range(year, month)
    month_expenses: Dict[str, float] = defaultdict(float)

    for exp in expenses:
        tx_date = exp["transaction_date"]
        if isinstance(tx_date, str):
            tx_date = date.fromisoformat(tx_date)
        if first <= tx_date <= last:
            month_expenses[exp["category"]] += exp["amount"]

    result = []
    for budget in budgets:
        cat = budget["category"]
        budgeted = budget["amount"]
        spent = month_expenses.get(cat, 0.0)
        remaining = max(budgeted - spent, 0.0)
        utilisation = round((spent / budgeted) * 100, 2) if budgeted > 0 else 0.0

        result.append({
            "category": cat,
            "budgeted": round(budgeted, 2),
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "utilisation_pct": utilisation,
            "is_over_budget": spent > budgeted,
        })

    return sorted(result, key=lambda x: x["utilisation_pct"], reverse=True)


def compute_income_vs_expense_chart(
    expenses: List[Dict[str, Any]],
    incomes: List[Dict[str, Any]],
    months: int = ANALYTICS_LOOKBACK_MONTHS,
) -> List[Dict[str, Any]]:
    """
    Build month-by-month income vs expense comparison data for charts.

    Returns:
        List of {"month": str, "income": float, "expense": float, "savings": float}
    """
    expense_trend = {
        (r["year"], r["month_num"]): r["total"]
        for r in compute_monthly_trend(expenses, months)
    }
    income_trend = {
        (r["year"], r["month_num"]): r["total"]
        for r in compute_monthly_trend(incomes, months)
    }

    all_keys = sorted(set(list(expense_trend.keys()) + list(income_trend.keys())))
    import calendar

    result = []
    for year, month in all_keys:
        income = income_trend.get((year, month), 0.0)
        expense = expense_trend.get((year, month), 0.0)
        result.append({
            "month": f"{calendar.month_abbr[month]} {year}",
            "income": income,
            "expense": expense,
            "savings": round(income - expense, 2),
        })
    return result


def get_top_expenses(
    expenses: List[Dict[str, Any]], top_n: int = TOP_N_EXPENSE_CATEGORIES
) -> List[Dict[str, Any]]:
    """Return top N expense categories with amounts and share percentages."""
    breakdown = compute_category_breakdown(expenses)
    total = sum(breakdown.values()) or 1.0
    top = list(breakdown.items())[:top_n]

    return [
        {
            "category": cat,
            "amount": round(amount, 2),
            "percentage": round((amount / total) * 100, 2),
        }
        for cat, amount in top
    ]