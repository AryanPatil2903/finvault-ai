"""
Export a user's expenses to JSON in data/outputs/.
Run:  python -m scripts.export you@example.com
"""

import asyncio
import sys

from sqlalchemy import select

from data.loader import export_transactions_to_json
from database.connection import AsyncSessionLocal
from database.models import Expense, User


async def main(email: str) -> None:
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == email.lower()))).scalar_one_or_none()
        if not user:
            sys.exit("User not found.")
        result = await db.execute(select(Expense).where(Expense.user_id == user.id))
        rows = [{"date": e.transaction_date, "amount": e.amount, "category": e.category,
                 "description": e.description} for e in result.scalars()]
        print("Written:", export_transactions_to_json(rows, "expenses_export.json"))


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))