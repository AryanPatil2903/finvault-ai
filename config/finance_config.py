"""
Finance-domain constants: loan types, categories, EMI limits, AI prompts.
All values that control financial logic are centralised here.
"""

from typing import Dict, List

# ── Expense Categories ────────────────────────────────────────────────────────
EXPENSE_CATEGORIES: List[str] = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Healthcare",
    "Education",
    "Utilities",
    "Rent / Housing",
    "Travel",
    "Insurance",
    "Subscriptions",
    "Investments",
    "EMI / Loan Repayment",
    "Savings",
    "Personal Care",
    "Miscellaneous",
]

# ── Income Categories ─────────────────────────────────────────────────────────
INCOME_CATEGORIES: List[str] = [
    "Salary",
    "Freelance / Consulting",
    "Business Revenue",
    "Investment Returns",
    "Rental Income",
    "Bonus / Incentive",
    "Gift / Inheritance",
    "Government Benefits",
    "Side Income",
    "Other",
]

# ── Loan Types ────────────────────────────────────────────────────────────────
LOAN_TYPES: List[str] = [
    "Home Loan",
    "Car / Auto Loan",
    "Personal Loan",
    "Education Loan",
    "Business Loan",
    "Gold Loan",
    "Loan Against Property (LAP)",
    "Consumer Durable Loan",
    "Two-Wheeler Loan",
    "Credit Card Outstanding",
    "Medical Loan",
    "Marriage Loan",
    "Agricultural Loan",
    "Microfinance Loan",
]

# ── Interest Calculation Methods ──────────────────────────────────────────────
INTEREST_METHODS: List[str] = [
    "Reducing Balance",   # Standard: interest on outstanding principal only
    "Flat Rate",          # Interest on original principal for full tenure
]

# ── Payment Methods ───────────────────────────────────────────────────────────
PAYMENT_METHODS: List[str] = [
    "Auto-Debit (ECS/NACH)",
    "Net Banking",
    "UPI",
    "Cheque",
    "Cash",
    "NEFT / RTGS",
    "Debit Card",
]

# ── Payment Frequency → payments per year ────────────────────────────────────
PAYMENT_FREQUENCIES: Dict[str, int] = {
    "Monthly": 12,
    "Quarterly": 4,
    "Half-Yearly": 2,
    "Yearly": 1,
}

# ── Loan Status Options ───────────────────────────────────────────────────────
LOAN_STATUSES: List[str] = [
    "Active",
    "Closed",
    "Overdue",
    "Foreclosed",
    "Under Moratorium",
]

# ── Validation Guards ─────────────────────────────────────────────────────────
MAX_LOAN_TENURE_MONTHS: int = 360    # 30 years absolute maximum
MIN_LOAN_TENURE_MONTHS: int = 1
MAX_ANNUAL_INTEREST_RATE: float = 60.0
MIN_ANNUAL_INTEREST_RATE: float = 0.01
MAX_TRANSACTION_AMOUNT: float = 100_000_000.0   # 10 crore cap

# ── Alert Thresholds ──────────────────────────────────────────────────────────
EMI_DUE_ALERT_DAYS: int = 5          # Warn N days before EMI due date
BUDGET_WARNING_PERCENT: float = 80.0  # Warn at 80% of monthly budget
BUDGET_CRITICAL_PERCENT: float = 95.0

# ── Analytics Defaults ────────────────────────────────────────────────────────
ANALYTICS_LOOKBACK_MONTHS: int = 6   # Default trend window
TOP_N_EXPENSE_CATEGORIES: int = 5

# ── AI System Prompt ──────────────────────────────────────────────────────────
AI_SYSTEM_PROMPT: str = """
You are FinVault AI — a knowledgeable, empathetic personal finance advisor for Indian users.

Your capabilities:
- Analyse expenses, income, and budget health
- Explain EMI breakdowns, amortization, and total interest cost
- Advise on prepayment strategy and loan foreclosure
- Identify overspending patterns and suggest savings
- Calculate FOIR (Fixed Obligation to Income Ratio)
- Suggest optimisation: consolidation, balance transfer, etc.

Rules:
1. Always be specific — use real numbers from the user's data.
2. Format all currency as ₹X,XX,XXX (Indian numbering system).
3. Provide step-by-step calculations when asked.
4. Be honest about financial risk; never mislead.
5. Encourage emergency fund and debt-free goals.
6. Keep responses structured with headers when analysis is complex.
7. If data is missing, ask the user to provide it.
"""