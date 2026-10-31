"""
All Pydantic v2 request/response models for the API layer.
Strict validation on every incoming payload — no raw dicts reach business logic.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ════════════════════════════════════════════════════════════
# AUTH
# ════════════════════════════════════════════════════════════

class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = Field(None, max_length=20)
    monthly_income: float = Field(0.0, ge=0)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int   # seconds


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    monthly_income: float
    currency: str
    created_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# EXPENSE
# ════════════════════════════════════════════════════════════

class ExpenseCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, le=100_000_000)
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    transaction_date: date
    payment_method: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_recurring: bool = False


class ExpenseUpdateRequest(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = None
    transaction_date: Optional[date] = None
    payment_method: Optional[str] = None
    tags: Optional[List[str]] = None
    is_recurring: Optional[bool] = None


class ExpenseResponse(BaseModel):
    id: str
    amount: float
    category: str
    description: Optional[str]
    transaction_date: date
    payment_method: Optional[str]
    tags: List[str]
    is_recurring: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# INCOME
# ════════════════════════════════════════════════════════════

class IncomeCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, le=100_000_000)
    category: str = Field(..., min_length=1, max_length=100)
    source: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    transaction_date: date
    is_taxable: bool = True


class IncomeResponse(BaseModel):
    id: str
    amount: float
    category: str
    source: Optional[str]
    description: Optional[str]
    transaction_date: date
    is_taxable: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# LOAN
# ════════════════════════════════════════════════════════════

class LoanCreateRequest(BaseModel):
    loan_name: str = Field(..., min_length=2, max_length=255)
    loan_type: str
    lender_name: str = Field(..., min_length=2, max_length=255)
    loan_account_number: Optional[str] = None
    loan_reference_number: Optional[str] = None
    principal_amount: float = Field(..., gt=0)
    annual_interest_rate: float = Field(..., gt=0, le=60)
    tenure_months: int = Field(..., ge=1, le=360)
    emi_amount: Optional[float] = Field(None, gt=0)   # If None, auto-calculated
    interest_method: str = "Reducing Balance"
    payment_frequency: str = "Monthly"
    disbursement_date: date
    first_emi_date: date
    emi_due_day: int = Field(1, ge=1, le=28)
    processing_fee: float = Field(0.0, ge=0)
    prepayment_penalty_percent: float = Field(0.0, ge=0)
    late_payment_fee: float = Field(0.0, ge=0)
    insurance_amount: float = Field(0.0, ge=0)
    other_charges: float = Field(0.0, ge=0)
    is_co_applicant: bool = False
    co_applicant_name: Optional[str] = None
    loan_manager_name: Optional[str] = None
    loan_manager_phone: Optional[str] = None
    customer_care_number: Optional[str] = None
    branch_name: Optional[str] = None
    notes: Optional[str] = None


class LoanUpdateRequest(BaseModel):
    loan_name: Optional[str] = None
    outstanding_amount: Optional[float] = Field(None, ge=0)
    total_emis_paid: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None
    annual_interest_rate: Optional[float] = Field(None, gt=0, le=60)
    notes: Optional[str] = None
    loan_manager_name: Optional[str] = None
    loan_manager_phone: Optional[str] = None


class LoanResponse(BaseModel):
    id: str
    loan_name: str
    loan_type: str
    lender_name: str
    loan_account_number: Optional[str]
    principal_amount: float
    annual_interest_rate: float
    tenure_months: int
    emi_amount: float
    interest_method: str
    disbursement_date: date
    first_emi_date: date
    emi_due_day: int
    processing_fee: float
    prepayment_penalty_percent: float
    insurance_amount: float
    outstanding_amount: float
    total_emis_paid: int
    total_emis_remaining: Optional[int]
    status: str
    is_co_applicant: bool
    co_applicant_name: Optional[str]
    loan_manager_name: Optional[str]
    loan_manager_phone: Optional[str]
    customer_care_number: Optional[str]
    branch_name: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# LOAN PAYMENT (EMI Recording)
# ════════════════════════════════════════════════════════════

class LoanPaymentCreateRequest(BaseModel):
    emi_number: int = Field(..., ge=1)
    payment_date: date
    due_date: date
    amount_paid: float = Field(..., gt=0)
    principal_component: float = Field(..., ge=0)
    interest_component: float = Field(..., ge=0)
    outstanding_after_payment: float = Field(..., ge=0)
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    receipt_number: Optional[str] = None
    is_prepayment: bool = False
    prepayment_amount: float = Field(0.0, ge=0)
    late_fee_paid: float = Field(0.0, ge=0)
    notes: Optional[str] = None


class LoanPaymentResponse(BaseModel):
    id: str
    loan_id: str
    emi_number: int
    payment_date: date
    due_date: date
    amount_paid: float
    principal_component: float
    interest_component: float
    outstanding_after_payment: float
    payment_method: Optional[str]
    transaction_id: Optional[str]
    receipt_number: Optional[str]
    is_prepayment: bool
    prepayment_amount: float
    late_fee_paid: float
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# BUDGET
# ════════════════════════════════════════════════════════════

class BudgetCreateRequest(BaseModel):
    category: str
    amount: float = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)


class BudgetResponse(BaseModel):
    id: str
    category: str
    amount: float
    month: int
    year: int
    created_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# EMI CALCULATOR (no-auth utility endpoint)
# ════════════════════════════════════════════════════════════

class EMICalculateRequest(BaseModel):
    principal: float = Field(..., gt=0)
    annual_interest_rate: float = Field(..., gt=0, le=60)
    tenure_months: int = Field(..., ge=1, le=360)
    method: str = "Reducing Balance"
    first_emi_date: date = Field(default_factory=date.today)
    processing_fee: float = Field(0.0, ge=0)
    insurance_amount: float = Field(0.0, ge=0)


# ════════════════════════════════════════════════════════════
# AI CHAT
# ════════════════════════════════════════════════════════════

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=4000)


class AIChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=4000)
    include_financial_context: bool = True


class AIChatResponse(BaseModel):
    conversation_id: str
    reply: str
    messages: List[ChatMessage]


# ════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════

class DashboardResponse(BaseModel):
    total_income_this_month: float
    total_expenses_this_month: float
    net_savings_this_month: float
    savings_rate: float
    total_active_loans: int
    total_outstanding_debt: float
    total_monthly_emi: float
    foir: float
    upcoming_emi_alerts: List[Dict[str, Any]]
    budget_warnings: List[Dict[str, Any]]
    top_expense_categories: List[Dict[str, Any]]
    income_expense_trend: List[Dict[str, Any]]
    ai_insight: Optional[Dict[str, Any]] = None