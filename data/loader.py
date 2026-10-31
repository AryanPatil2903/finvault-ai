"""
Dataset loading utilities — useful for bulk import, sample data seeding,
and export pipelines. Not used in production request handling.
"""

import csv
import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.logging_config import get_logger

logger = get_logger("loader")

DATA_RAW_DIR = Path("data/raw")
DATA_PROCESSED_DIR = Path("data/processed")
DATA_OUTPUT_DIR = Path("data/outputs")


def load_csv_transactions(filepath: str) -> List[Dict[str, Any]]:
    """
    Load expense/income transactions from a CSV file.

    Expected columns: date, amount, category, description, type (expense/income)

    Returns:
        List of transaction dicts.
    """
    rows: List[Dict[str, Any]] = []
    path = Path(filepath)

    if not path.exists():
        logger.error("CSV file not found: %s", filepath)
        return rows

    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                try:
                    rows.append({
                        "transaction_date": date.fromisoformat(row["date"].strip()),
                        "amount": float(row["amount"]),
                        "category": row.get("category", "Miscellaneous").strip(),
                        "description": row.get("description", "").strip(),
                        "type": row.get("type", "expense").strip().lower(),
                    })
                except (KeyError, ValueError) as exc:
                    logger.warning("Skipping row %d — parse error: %s", i + 1, exc)

        logger.info("Loaded %d transactions from %s", len(rows), filepath)
    except Exception as exc:
        logger.error("Failed to read CSV: %s", exc)

    return rows


def export_transactions_to_json(
    transactions: List[Dict[str, Any]], output_filename: str
) -> str:
    """
    Export a list of transaction dicts to JSON in data/outputs/.

    Returns:
        Full path to the written file.
    """
    DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_OUTPUT_DIR / output_filename

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                transactions,
                f,
                indent=2,
                default=str,    # Serialize date objects as strings
            )
        logger.info("Exported %d records to %s", len(transactions), output_path)
    except Exception as exc:
        logger.error("Export failed: %s", exc)
        raise

    return str(output_path)