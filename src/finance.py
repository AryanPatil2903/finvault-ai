"""
Core financial calculation engine.
Handles EMI computation, full amortization schedules, loan analytics,
flat-rate vs reducing-balance methods, and prepayment projections.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Tuple

from config.finance_config import INTEREST_METHODS
from config.logging_config import get_logger

logger = get_logger("finance")


# ── Data Structures ───────────────────────────────────────────────────────────

@dataclass
class AmortizationRow:
    """Single row in an amortization schedule (one EMI period)."""

    emi_number: int
    due_date: date
    emi_amount: float
    principal_component: float
    interest_component: float
    outstanding_after: float
    total_interest_paid_so_far: float
    total_principal_paid_so_far: float


@dataclass
class LoanSummary:
    """High-level loan analytics computed from full amortization."""

    principal: float
    annual_rate: float
    tenure_months: int
    emi_amount: float
    total_payment: float
    total_interest: float
    interest_to_principal_ratio: float
    effective_cost: float            # Total cost including fees
    break_even_month: int            # Month where principal > interest in EMI


@dataclass
class PrepaymentScenario:
    """Impact analysis when user makes a lump-sum prepayment."""

    original_emis_remaining: int
    new_emis_remaining: int
    emis_saved: int
    interest_saved: float
    new_outstanding: float


# ── EMI Calculation ───────────────────────────────────────────────────────────

def calculate_emi(
    principal: float,
    annual_interest_rate: float,
    tenure_months: int,
    method: str = "Reducing Balance",
) -> float:
    """
    Calculate Equated Monthly Instalment (EMI).

    Args:
        principal:            Original loan amount in rupees.
        annual_interest_rate: Annual rate as percentage (e.g., 8.5 for 8.5%).
        tenure_months:        Total number of monthly instalments.
        method:               "Reducing Balance" or "Flat Rate".

    Returns:
        Monthly EMI amount rounded to 2 decimal places.

    Raises:
        ValueError: If inputs violate business rules.
    """
    if principal <= 0:
        raise ValueError("Principal must be positive.")
    if annual_interest_rate < 0:
        raise ValueError("Interest rate cannot be negative.")
    if tenure_months <= 0:
        raise ValueError("Tenure must be at least 1 month.")

    # ── Zero interest edge case ───────────────────────────────────────────
    if annual_interest_rate == 0.0:
        return round(principal / tenure_months, 2)

    monthly_rate: float = annual_interest_rate / 12 / 100

    if method == "Flat Rate":
        # Flat rate: total interest = P × r × n; divided equally each month
        total_interest = principal * monthly_rate * tenure_months
        return round((principal + total_interest) / tenure_months, 2)

    # ── Standard reducing balance formula: EMI = P·r·(1+r)^n / ((1+r)^n - 1)
    compound_factor: float = (1 + monthly_rate) ** tenure_months
    emi: float = principal * monthly_rate * compound_factor / (compound_factor - 1)

    return round(emi, 2)


def generate_amortization_schedule(
    principal: float,
    annual_interest_rate: float,
    tenure_months: int,
    first_emi_date: date,
    emi_amount: float | None = None,
    method: str = "Reducing Balance",
) -> List[AmortizationRow]:
    """
    Generate full month-by-month amortization schedule.

    Args:
        principal:            Original loan amount.
        annual_interest_rate: Annual rate as percentage.
        tenure_months:        Total EMI count.
        first_emi_date:       Date of first EMI payment.
        emi_amount:           Override computed EMI (e.g. bank-set value).
        method:               Interest calculation method.

    Returns:
        List of AmortizationRow objects, one per EMI period.
    """
    if emi_amount is None:
        emi_amount = calculate_emi(principal, annual_interest_rate, tenure_months, method)

    monthly_rate: float = annual_interest_rate / 12 / 100
    outstanding: float = principal
    schedule: List[AmortizationRow] = []
    cumulative_interest: float = 0.0
    cumulative_principal: float = 0.0

    # Advance EMI date by one month per iteration
    current_date: date = first_emi_date

    for emi_num in range(1, tenure_months + 1):
        if method == "Flat Rate":
            # Flat: interest is fixed each month on original principal
            interest = round(principal * monthly_rate, 2)
        else:
            # Reducing balance: interest on current outstanding
            interest = round(outstanding * monthly_rate, 2)

        # Final EMI — pay exact remaining outstanding to avoid rounding drift
        if emi_num == tenure_months:
            principal_paid = outstanding
            actual_emi = round(outstanding + interest, 2)
        else:
            principal_paid = round(emi_amount - interest, 2)
            actual_emi = emi_amount

        outstanding = round(max(outstanding - principal_paid, 0.0), 2)
        cumulative_interest += interest
        cumulative_principal += principal_paid

        row = AmortizationRow(
            emi_number=emi_num,
            due_date=current_date,
            emi_amount=actual_emi,
            principal_component=principal_paid,
            interest_component=interest,
            outstanding_after=outstanding,
            total_interest_paid_so_far=round(cumulative_interest, 2),
            total_principal_paid_so_far=round(cumulative_principal, 2),
        )
        schedule.append(row)

        # ── Advance to next EMI date (same day, next month) ───────────────
        month = current_date.month
        year = current_date.year
        if month == 12:
            month, year = 1, year + 1
        else:
            month += 1
        # Clamp to last valid day of month (e.g. 31 → 28 in Feb)
        try:
            current_date = current_date.replace(year=year, month=month)
        except ValueError:
            current_date = date(year, month, 1) - timedelta(days=1)

    logger.debug("Amortization schedule generated: %d rows", len(schedule))
    return schedule


def get_loan_summary(
    principal: float,
    annual_interest_rate: float,
    tenure_months: int,
    first_emi_date: date,
    processing_fee: float = 0.0,
    insurance_amount: float = 0.0,
    method: str = "Reducing Balance",
) -> LoanSummary:
    """
    Compute high-level loan analytics from the full amortization schedule.

    Returns LoanSummary with total interest, effective cost, and break-even month.
    """
    emi = calculate_emi(principal, annual_interest_rate, tenure_months, method)
    schedule = generate_amortization_schedule(
        principal, annual_interest_rate, tenure_months, first_emi_date, emi, method
    )

    total_payment = sum(row.emi_amount for row in schedule)
    total_interest = total_payment - principal

    # Break-even: first month where principal component exceeds interest component
    break_even = next(
        (row.emi_number for row in schedule if row.principal_component >= row.interest_component),
        tenure_months,
    )

    return LoanSummary(
        principal=principal,
        annual_rate=annual_interest_rate,
        tenure_months=tenure_months,
        emi_amount=emi,
        total_payment=round(total_payment, 2),
        total_interest=round(total_interest, 2),
        interest_to_principal_ratio=round(total_interest / principal, 4),
        effective_cost=round(total_payment + processing_fee + insurance_amount, 2),
        break_even_month=break_even,
    )


def calculate_prepayment_impact(
    current_outstanding: float,
    annual_interest_rate: float,
    emis_remaining: int,
    prepayment_amount: float,
    first_remaining_emi_date: date,
    method: str = "Reducing Balance",
) -> PrepaymentScenario:
    """
    Calculate interest savings and tenure reduction from a prepayment.

    Args:
        current_outstanding:  Current loan balance before prepayment.
        annual_interest_rate: Annual rate as percentage.
        emis_remaining:       EMIs left in original schedule.
        prepayment_amount:    Lump-sum amount being paid extra.
        first_remaining_emi_date: Date of next upcoming EMI.
        method:               Interest method.

    Returns:
        PrepaymentScenario showing EMIs saved and interest saved.
    """
    new_outstanding = max(current_outstanding - prepayment_amount, 0.0)

    # Original remaining interest
    original_schedule = generate_amortization_schedule(
        current_outstanding, annual_interest_rate, emis_remaining,
        first_remaining_emi_date, method=method
    )
    original_interest = sum(r.interest_component for r in original_schedule)

    if new_outstanding == 0:
        return PrepaymentScenario(
            original_emis_remaining=emis_remaining,
            new_emis_remaining=0,
            emis_saved=emis_remaining,
            interest_saved=round(original_interest, 2),
            new_outstanding=0.0,
        )

    # Recalculate new EMI count with same original EMI amount
    original_emi = calculate_emi(
        current_outstanding, annual_interest_rate, emis_remaining, method
    )

    # Find new tenure by simulating until balance is zero
    monthly_rate = annual_interest_rate / 12 / 100
    balance = new_outstanding
    new_months = 0
    new_total_interest = 0.0

    while balance > 0 and new_months < emis_remaining:
        interest = round(balance * monthly_rate, 2)
        principal_paid = round(original_emi - interest, 2)
        balance = round(max(balance - principal_paid, 0.0), 2)
        new_total_interest += interest
        new_months += 1

    return PrepaymentScenario(
        original_emis_remaining=emis_remaining,
        new_emis_remaining=new_months,
        emis_saved=emis_remaining - new_months,
        interest_saved=round(original_interest - new_total_interest, 2),
        new_outstanding=round(new_outstanding, 2),
    )


def calculate_foir(total_emi_obligations: float, gross_monthly_income: float) -> float:
    """
    Fixed Obligation to Income Ratio — key metric banks use for loan eligibility.

    Args:
        total_emi_obligations: Sum of all active EMIs per month.
        gross_monthly_income:  Monthly gross income.

    Returns:
        FOIR as percentage (e.g. 42.5 for 42.5%).
    """
    if gross_monthly_income <= 0:
        return 0.0
    return round((total_emi_obligations / gross_monthly_income) * 100, 2)