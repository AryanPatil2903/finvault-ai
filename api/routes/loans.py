"""
Loan CRUD, EMI recording, amortization schedule, and prepayment calculator endpoints.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user
from api.schemas import (
    EMICalculateRequest, LoanCreateRequest, LoanPaymentCreateRequest,
    LoanPaymentResponse, LoanResponse, LoanUpdateRequest,
)
from config.logging_config import get_logger
from database.connection import get_db
from database.models import Loan, LoanPayment, User
from src.finance import (
    calculate_emi, calculate_prepayment_impact, generate_amortization_schedule,
    get_loan_summary,
)

router = APIRouter(prefix="/loans", tags=["Loans & EMI"])
logger = get_logger("loans")


async def _get_user_loan(db: AsyncSession, loan_id: str, user: User) -> Loan:
    """Fetch a loan owned by the user or raise 404."""
    result = await db.execute(
        select(Loan).where(Loan.id == loan_id, Loan.user_id == user.id)
    )
    loan = result.scalar_one_or_none()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found.")
    return loan


@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(
    body: LoanCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Loan:
    """
    Create a new loan record. If emi_amount not provided, it's auto-calculated
    using the reducing balance formula.
    """
    # Auto-calculate EMI if not provided by user
    emi = body.emi_amount or calculate_emi(
        body.principal_amount,
        body.annual_interest_rate,
        body.tenure_months,
        body.interest_method,
    )

    tenure_remaining = body.tenure_months  # Initially all EMIs remain

    loan = Loan(
        user_id=current_user.id,
        loan_name=body.loan_name,
        loan_type=body.loan_type,
        lender_name=body.lender_name,
        loan_account_number=body.loan_account_number,
        loan_reference_number=body.loan_reference_number,
        principal_amount=body.principal_amount,
        annual_interest_rate=body.annual_interest_rate,
        tenure_months=body.tenure_months,
        emi_amount=emi,
        interest_method=body.interest_method,
        payment_frequency=body.payment_frequency,
        disbursement_date=body.disbursement_date,
        first_emi_date=body.first_emi_date,
        emi_due_day=body.emi_due_day,
        processing_fee=body.processing_fee,
        prepayment_penalty_percent=body.prepayment_penalty_percent,
        late_payment_fee=body.late_payment_fee,
        insurance_amount=body.insurance_amount,
        other_charges=body.other_charges,
        outstanding_amount=body.principal_amount,
        total_emis_paid=0,
        total_emis_remaining=tenure_remaining,
        is_co_applicant=body.is_co_applicant,
        co_applicant_name=body.co_applicant_name,
        loan_manager_name=body.loan_manager_name,
        loan_manager_phone=body.loan_manager_phone,
        customer_care_number=body.customer_care_number,
        branch_name=body.branch_name,
        notes=body.notes,
    )
    db.add(loan)
    await db.flush()
    logger.info("Loan created: %s for user %s", loan.loan_name, current_user.id)
    return loan


@router.get("", response_model=List[LoanResponse])
async def list_loans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = None,
) -> List[Loan]:
    """List all loans for the current user, optionally filtered by status."""
    query = select(Loan).where(Loan.user_id == current_user.id)
    if status_filter:
        query = query.where(Loan.status == status_filter)
    result = await db.execute(query.order_by(Loan.disbursement_date.desc()))
    return list(result.scalars().all())


@router.get("/{loan_id}", response_model=LoanResponse)
async def get_loan(
    loan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Loan:
    """Get a single loan record with full details."""
    return await _get_user_loan(db, loan_id, current_user)


@router.patch("/{loan_id}", response_model=LoanResponse)
async def update_loan(
    loan_id: str,
    body: LoanUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Loan:
    """Update loan details (status, outstanding, rate, etc.)."""
    loan = await _get_user_loan(db, loan_id, current_user)

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(loan, field, value)

    await db.flush()
    return loan


@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan(
    loan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a loan and all its payment records."""
    loan = await _get_user_loan(db, loan_id, current_user)
    await db.delete(loan)


# -- Amortization Schedule ----------------------------------------------------
@router.get("/{loan_id}/amortization")
async def get_amortization(
    loan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Generate full amortization schedule for a loan.
    Returns EMI breakdown per month: principal, interest, outstanding.
    """
    loan = await _get_user_loan(db, loan_id, current_user)

    schedule = generate_amortization_schedule(
        principal=loan.principal_amount,
        annual_interest_rate=loan.annual_interest_rate,
        tenure_months=loan.tenure_months,
        first_emi_date=loan.first_emi_date,
        emi_amount=loan.emi_amount,
        method=loan.interest_method,
    )

    summary = get_loan_summary(
        loan.principal_amount,
        loan.annual_interest_rate,
        loan.tenure_months,
        loan.first_emi_date,
        loan.processing_fee,
        loan.insurance_amount,
        loan.interest_method,
    )

    return {
        "loan_id": loan_id,
        "summary": {
            "principal": summary.principal,
            "emi_amount": summary.emi_amount,
            "total_payment": summary.total_payment,
            "total_interest": summary.total_interest,
            "interest_to_principal_ratio": summary.interest_to_principal_ratio,
            "effective_cost": summary.effective_cost,
            "break_even_month": summary.break_even_month,
        },
        "schedule": [
            {
                "emi_number": row.emi_number,
                "due_date": row.due_date.isoformat(),
                "emi_amount": row.emi_amount,
                "principal_component": row.principal_component,
                "interest_component": row.interest_component,
                "outstanding_after": row.outstanding_after,
                "total_interest_paid": row.total_interest_paid_so_far,
                "total_principal_paid": row.total_principal_paid_so_far,
            }
            for row in schedule
        ],
    }


# -- EMI Payment Recording ----------------------------------------------------
@router.post("/{loan_id}/payments", response_model=LoanPaymentResponse, status_code=201)
async def record_emi_payment(
    loan_id: str,
    body: LoanPaymentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LoanPayment:
    """
    Record an EMI payment against a loan.
    Automatically updates loan outstanding balance and EMI counters.
    """
    loan = await _get_user_loan(db, loan_id, current_user)

    payment = LoanPayment(
        loan_id=loan_id,
        emi_number=body.emi_number,
        payment_date=body.payment_date,
        due_date=body.due_date,
        amount_paid=body.amount_paid,
        principal_component=body.principal_component,
        interest_component=body.interest_component,
        outstanding_after_payment=body.outstanding_after_payment,
        payment_method=body.payment_method,
        transaction_id=body.transaction_id,
        receipt_number=body.receipt_number,
        is_prepayment=body.is_prepayment,
        prepayment_amount=body.prepayment_amount,
        late_fee_paid=body.late_fee_paid,
        notes=body.notes,
    )
    db.add(payment)

    # Update loan counters
    loan.outstanding_amount = body.outstanding_after_payment
    loan.total_emis_paid += 1
    loan.total_emis_remaining = loan.tenure_months - loan.total_emis_paid
    if loan.outstanding_amount <= 0:
        loan.status = "Closed"

    await db.flush()
    return payment


@router.get("/{loan_id}/payments", response_model=List[LoanPaymentResponse])
async def list_payments(
    loan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[LoanPayment]:
    """Retrieve full payment history for a loan."""
    await _get_user_loan(db, loan_id, current_user)

    payments_result = await db.execute(
        select(LoanPayment)
        .where(LoanPayment.loan_id == loan_id)
        .order_by(LoanPayment.emi_number)
    )
    return list(payments_result.scalars().all())


@router.post("/{loan_id}/pay-next", response_model=LoanPaymentResponse, status_code=201)
async def pay_next_emi(
    loan_id: str,
    payment_method: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LoanPayment:
    """
    Mark the next scheduled EMI as paid, using the amortization schedule
    for the principal/interest split and the new outstanding balance.
    """
    loan = await _get_user_loan(db, loan_id, current_user)
    if loan.total_emis_paid >= loan.tenure_months:
        raise HTTPException(status_code=400, detail="All EMIs are already paid.")

    schedule = generate_amortization_schedule(
        loan.principal_amount, loan.annual_interest_rate, loan.tenure_months,
        loan.first_emi_date, loan.emi_amount, loan.interest_method,
    )
    if loan.total_emis_paid >= len(schedule):
        raise HTTPException(status_code=400, detail="No further EMIs in schedule.")
    row = schedule[loan.total_emis_paid]  # Next unpaid EMI

    payment = LoanPayment(
        loan_id=loan_id,
        emi_number=row.emi_number,
        payment_date=date.today(),
        due_date=row.due_date,
        amount_paid=row.emi_amount,
        principal_component=row.principal_component,
        interest_component=row.interest_component,
        outstanding_after_payment=row.outstanding_after,
        payment_method=payment_method,
    )
    db.add(payment)

    loan.outstanding_amount = row.outstanding_after
    loan.total_emis_paid += 1
    loan.total_emis_remaining = loan.tenure_months - loan.total_emis_paid
    if loan.outstanding_amount <= 0:
        loan.status = "Closed"

    await db.flush()
    return payment


# -- Prepayment Calculator ----------------------------------------------------
@router.post("/{loan_id}/prepayment-impact")
async def prepayment_impact(
    loan_id: str,
    prepayment_amount: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Calculate the impact of making a lump-sum prepayment on this loan.
    Returns: EMIs saved, interest saved, new tenure.
    """
    loan = await _get_user_loan(db, loan_id, current_user)

    if prepayment_amount <= 0:
        raise HTTPException(status_code=400, detail="Prepayment amount must be positive.")

    scenario = calculate_prepayment_impact(
        current_outstanding=loan.outstanding_amount,
        annual_interest_rate=loan.annual_interest_rate,
        emis_remaining=loan.total_emis_remaining or loan.tenure_months,
        prepayment_amount=prepayment_amount,
        first_remaining_emi_date=date.today(),
        method=loan.interest_method,
    )

    prepayment_penalty = round(
        prepayment_amount * (loan.prepayment_penalty_percent / 100), 2
    )

    return {
        "loan_id": loan_id,
        "prepayment_amount": prepayment_amount,
        "prepayment_penalty": prepayment_penalty,
        "net_prepayment": prepayment_amount + prepayment_penalty,
        "original_emis_remaining": scenario.original_emis_remaining,
        "new_emis_remaining": scenario.new_emis_remaining,
        "emis_saved": scenario.emis_saved,
        "interest_saved": scenario.interest_saved,
        "new_outstanding": scenario.new_outstanding,
        "is_worth_it": scenario.interest_saved > prepayment_penalty,
    }


# -- Standalone EMI Calculator (no auth required) -----------------------------
@router.post("/calculator/emi")
async def emi_calculator(body: EMICalculateRequest) -> Dict[str, Any]:
    """
    Public EMI calculator endpoint - no authentication required.
    Returns EMI, total payment, and summary figures.
    """
    emi = calculate_emi(
        body.principal, body.annual_interest_rate, body.tenure_months, body.method
    )
    summary = get_loan_summary(
        body.principal, body.annual_interest_rate, body.tenure_months,
        body.first_emi_date, body.processing_fee, body.insurance_amount, body.method,
    )

    return {
        "emi_amount": emi,
        "total_payment": summary.total_payment,
        "total_interest": summary.total_interest,
        "effective_cost": summary.effective_cost,
        "interest_to_principal_ratio": summary.interest_to_principal_ratio,
        "break_even_month": summary.break_even_month,
    }