"""
Notification and alert logic for upcoming EMIs, overdue loans, and budget warnings.
In production, connect send_* functions to email/SMS/push services.
"""

from datetime import date, timedelta
from typing import Any, Dict, List

from config.finance_config import (
    BUDGET_CRITICAL_PERCENT,
    BUDGET_WARNING_PERCENT,
    EMI_DUE_ALERT_DAYS,
)
from config.logging_config import get_logger

logger = get_logger("notifications")


def get_upcoming_emi_alerts(
    loans: List[Dict[str, Any]],
    reference_date: date | None = None,
) -> List[Dict[str, Any]]:
    """
    Return list of EMI alerts for loans due within EMI_DUE_ALERT_DAYS.

    Args:
        loans:          Active loan records with emi_due_day field.
        reference_date: Date to check against (defaults to today).

    Returns:
        List of alert dicts: loan_name, due_date, emi_amount, days_remaining.
    """
    today = reference_date or date.today()
    alerts: List[Dict[str, Any]] = []

    for loan in loans:
        if loan.get("status") != "Active":
            continue

        # Build due date for current month
        try:
            due_date = today.replace(day=int(loan["emi_due_day"]))
        except ValueError:
            # Day doesn't exist in month (e.g. day 31 in April) → last day
            import calendar
            last_day = calendar.monthrange(today.year, today.month)[1]
            due_date = today.replace(day=last_day)

        # If due date already passed this month, check next month
        if due_date < today:
            if today.month == 12:
                due_date = due_date.replace(year=today.year + 1, month=1)
            else:
                due_date = due_date.replace(month=today.month + 1)

        days_remaining = (due_date - today).days

        if 0 <= days_remaining <= EMI_DUE_ALERT_DAYS:
            alerts.append({
                "loan_id": loan["id"],
                "loan_name": loan["loan_name"],
                "lender_name": loan["lender_name"],
                "emi_amount": loan["emi_amount"],
                "due_date": due_date.isoformat(),
                "days_remaining": days_remaining,
                "severity": "critical" if days_remaining <= 1 else "warning",
            })

    return sorted(alerts, key=lambda x: x["days_remaining"])


def get_budget_warnings(
    budget_utilisation: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Return budget warnings for categories exceeding threshold.

    Args:
        budget_utilisation: Output from analytics.compute_budget_utilisation().

    Returns:
        List of warning dicts with severity: warning or critical.
    """
    warnings: List[Dict[str, Any]] = []

    for item in budget_utilisation:
        pct = item["utilisation_pct"]
        if pct >= BUDGET_CRITICAL_PERCENT:
            severity = "critical"
        elif pct >= BUDGET_WARNING_PERCENT:
            severity = "warning"
        else:
            continue

        warnings.append({
            "category": item["category"],
            "budgeted": item["budgeted"],
            "spent": item["spent"],
            "utilisation_pct": pct,
            "is_over_budget": item["is_over_budget"],
            "severity": severity,
        })

    return warnings


def get_overdue_loans(loans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return loans marked as Overdue or with outstanding > 0 and status Closed."""
    return [
        loan for loan in loans
        if loan.get("status") == "Overdue"
        or (loan.get("status") == "Closed" and loan.get("outstanding_amount", 0) > 0)
    ]