"""
Seed a demo user with income, expenses, and two loans.
Run:  python -m scripts.seed_db     (login: demo@finvault.com / demo12345)
"""

import asyncio
import random
from datetime import date, timedelta

from sqlalchemy import select

from api.routes.auth import hash_password
from config.logging_config import get_logger, setup_logging
from database.connection import AsyncSessionLocal, init_db
from database.models import Expense, Income, Loan, User
from src.finance import calculate_emi

logger = get_logger("seed")
CATEGORIES = ["Food & Dining", "Transportation", "Shopping", "Utilities", "Entertainment"]


def _loan(user_id: str, name: str, ltype: str, lender: str, principal: float,
          rate: float, months: int, due_day: int) -> Loan:
    """Build a Loan row with an auto-calculated EMI."""
    start = date.today().replace(day=due_day)
    return Loan(
        user_id=user_id, loan_name=name, loan_type=ltype, lender_name=lender,
        principal_amount=principal, annual_interest_rate=rate, tenure_months=months,
        emi_amount=calculate_emi(principal, rate, months),
        disbursement_date=start, first_emi_date=start, emi_due_day=due_day,
        outstanding_amount=principal, total_emis_remaining=months,
    )


async def main() -> None:
    setup_logging()
    await init_db()
    async with AsyncSessionLocal() as db:
        if (await db.execute(select(User).where(User.email == "demo@finvault.com"))).scalar_one_or_none():
            logger.info("Demo user already exists.")
            return
        user = User(email="demo@finvault.com", password_hash=hash_password("demo12345"),
                    full_name="Demo User", monthly_income=95000)
        db.add(user)
        await db.flush()

        today = date.today()
        for m in range(6):  # six months of history for the trend chart
            d = (today.replace(day=1) - timedelta(days=30 * m)).replace(day=1)
            db.add(Income(user_id=user.id, amount=95000, category="Salary",
                          source="Acme Corp", transaction_date=d))
            for _ in range(12):
                db.add(Expense(user_id=user.id, amount=random.randint(150, 4500),
                               category=random.choice(CATEGORIES),
                               transaction_date=d + timedelta(days=random.randint(0, 27))))

        db.add(_loan(user.id, "Home Loan", "Home Loan", "HDFC Bank", 4500000, 8.5, 240, 5))
        db.add(_loan(user.id, "Car Loan", "Car / Auto Loan", "ICICI Bank", 800000, 9.2, 60, 12))
        await db.commit()
        logger.info("Seeded demo data.")


if __name__ == "__main__":
    asyncio.run(main())