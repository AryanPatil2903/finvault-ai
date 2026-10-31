"""
All SQLAlchemy ORM models for FinVault AI (SQLAlchemy 2.0 typed style).
Tables: User, Expense, Income, Loan, LoanPayment, Budget, AIConversation.
"""

import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.connection import Base


def gen_uuid() -> str:
    """Generate a new UUID4 string - used as default primary key."""
    return str(uuid.uuid4())


# -- User ---------------------------------------------------------------------
class User(Base):
    """Application user - owns all financial records."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    monthly_income: Mapped[float] = mapped_column(Float, default=0.0)  # For FOIR calculation
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # -- Relationships --
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense", back_populates="user", cascade="all, delete-orphan"
    )
    incomes: Mapped[List["Income"]] = relationship(
        "Income", back_populates="user", cascade="all, delete-orphan"
    )
    loans: Mapped[List["Loan"]] = relationship(
        "Loan", back_populates="user", cascade="all, delete-orphan"
    )
    budgets: Mapped[List["Budget"]] = relationship(
        "Budget", back_populates="user", cascade="all, delete-orphan"
    )
    ai_conversations: Mapped[List["AIConversation"]] = relationship(
        "AIConversation", back_populates="user", cascade="all, delete-orphan"
    )


# -- Expense ------------------------------------------------------------------
class Expense(Base):
    """Individual expense transaction."""

    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)  # e.g. ["weekend", "family"]
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="expenses")


# -- Income -------------------------------------------------------------------
class Income(Base):
    """Individual income transaction."""

    __tablename__ = "incomes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Employer, client
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_taxable: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="incomes")


# -- Loan ---------------------------------------------------------------------
class Loan(Base):
    """Full loan record with all details a customer needs to track."""

    __tablename__ = "loans"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # -- Core loan info --
    loan_name: Mapped[str] = mapped_column(String(255), nullable=False)
    loan_type: Mapped[str] = mapped_column(String(100), nullable=False)
    lender_name: Mapped[str] = mapped_column(String(255), nullable=False)
    loan_account_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    loan_reference_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # -- Financial terms --
    principal_amount: Mapped[float] = mapped_column(Float, nullable=False)
    annual_interest_rate: Mapped[float] = mapped_column(Float, nullable=False)  # e.g. 8.5
    tenure_months: Mapped[int] = mapped_column(Integer, nullable=False)
    emi_amount: Mapped[float] = mapped_column(Float, nullable=False)
    interest_method: Mapped[str] = mapped_column(String(50), default="Reducing Balance")
    payment_frequency: Mapped[str] = mapped_column(String(50), default="Monthly")

    # -- Dates --
    disbursement_date: Mapped[date] = mapped_column(Date, nullable=False)
    first_emi_date: Mapped[date] = mapped_column(Date, nullable=False)
    emi_due_day: Mapped[int] = mapped_column(Integer, default=1)  # Day of month (1-28)
    maturity_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # -- Charges & fees --
    processing_fee: Mapped[float] = mapped_column(Float, default=0.0)
    prepayment_penalty_percent: Mapped[float] = mapped_column(Float, default=0.0)
    late_payment_fee: Mapped[float] = mapped_column(Float, default=0.0)
    insurance_amount: Mapped[float] = mapped_column(Float, default=0.0)
    other_charges: Mapped[float] = mapped_column(Float, default=0.0)

    # -- Current status --
    outstanding_amount: Mapped[float] = mapped_column(Float, nullable=False)
    total_emis_paid: Mapped[int] = mapped_column(Integer, default=0)
    total_emis_remaining: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Active")  # Active/Closed/Overdue
    is_co_applicant: Mapped[bool] = mapped_column(Boolean, default=False)
    co_applicant_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # -- Contact --
    loan_manager_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    loan_manager_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    customer_care_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    branch_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # -- Notes --
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="loans")
    payments: Mapped[List["LoanPayment"]] = relationship(
        "LoanPayment",
        back_populates="loan",
        cascade="all, delete-orphan",
        order_by="LoanPayment.payment_date",
    )


# -- LoanPayment --------------------------------------------------------------
class LoanPayment(Base):
    """Individual EMI payment record - one row per EMI paid."""

    __tablename__ = "loan_payments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    loan_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("loans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    emi_number: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount_paid: Mapped[float] = mapped_column(Float, nullable=False)
    principal_component: Mapped[float] = mapped_column(Float, nullable=False)
    interest_component: Mapped[float] = mapped_column(Float, nullable=False)
    outstanding_after_payment: Mapped[float] = mapped_column(Float, nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    receipt_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_prepayment: Mapped[bool] = mapped_column(Boolean, default=False)
    prepayment_amount: Mapped[float] = mapped_column(Float, default=0.0)
    late_fee_paid: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    loan: Mapped["Loan"] = relationship("Loan", back_populates="payments")


# -- Budget -------------------------------------------------------------------
class Budget(Base):
    """Monthly budget limit per category per user."""

    __tablename__ = "budgets"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="budgets")


# -- AIConversation -----------------------------------------------------------
class AIConversation(Base):
    """Stores full AI chat history per user session."""

    __tablename__ = "ai_conversations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), default="New Conversation")
    messages: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)  # [{role, content, timestamp}]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="ai_conversations")