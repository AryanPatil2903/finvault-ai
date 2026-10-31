"""
Import transactions from a CSV into the database.
Run:  python -m scripts.ingest data/raw/bank.csv you@example.com
CSV columns: date,amount,category,description,type   (type = expense|income)
"""

import asyncio
import sys

from sqlalchemy import select

from config.logging_config import get_logger, setup_logging
from data.loader import load_csv_transactions
from database.connection import AsyncSessionLocal
from database.models import Expense, Income, User

logger = get_logger("ingest")


async def main(csv_path: str, email: str) -> None:
    setup_logging()
    rows = load_csv_transactions(csv_path)
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == email.lower()))).scalar_one_or_none()
        if not user:
            logger.error("No user with email %s", email)
            return
        for r in rows:
            model = Income if r["type"] == "income" else Expense
            db.add(model(user_id=user.id, amount=r["amount"], category=r["category"],
                         description=r["description"], transaction_date=r["transaction_date"]))
        await db.commit()
        logger.info("Imported %d rows for %s", len(rows), email)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python -m scripts.ingest <file.csv> <user-email>")
    asyncio.run(main(sys.argv[1], sys.argv[2]))