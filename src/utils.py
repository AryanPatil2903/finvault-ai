"""
Shared utility functions: currency formatting, date helpers, Indian number formatting.
"""

import re
from datetime import date, datetime
from typing import Any, Optional


def format_inr(amount: float, show_symbol: bool = True) -> str:
    """
    Format amount in Indian numbering system (lakhs, crores).

    Examples:
        1500    → ₹1,500
        125000  → ₹1,25,000
        5000000 → ₹50,00,000
    """
    if amount < 0:
        return f"-{format_inr(-amount, show_symbol)}"

    # Split into integer and decimal parts
    integer_part = int(amount)
    decimal_part = round(amount - integer_part, 2)

    # Indian format: last 3 digits, then groups of 2
    s = str(integer_part)
    if len(s) <= 3:
        formatted = s
    else:
        # First group of 3 from right, then groups of 2
        result = s[-3:]
        s = s[:-3]
        while s:
            result = s[-2:] + "," + result
            s = s[:-2]
        formatted = result

    decimal_str = f".{int(decimal_part * 100):02d}" if decimal_part > 0 else ""
    symbol = "₹" if show_symbol else ""
    return f"{symbol}{formatted}{decimal_str}"


def months_between(start: date, end: date) -> int:
    """Return number of complete months between two dates."""
    return (end.year - start.year) * 12 + (end.month - start.month)


def add_months(source_date: date, months: int) -> date:
    """Add N months to a date, clamping to valid month-end if needed."""
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    import calendar
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def current_month_year() -> tuple[int, int]:
    """Return (month, year) for today."""
    today = date.today()
    return today.month, today.year


def parse_date_flexible(date_str: Any) -> Optional[date]:
    """
    Parse date from string in multiple formats: ISO, DD/MM/YYYY, DD-MM-YYYY.

    Returns:
        date object or None if parsing fails.
    """
    if isinstance(date_str, date):
        return date_str
    if isinstance(date_str, datetime):
        return date_str.date()
    if not isinstance(date_str, str):
        return None

    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def sanitise_string(value: str, max_length: int = 255) -> str:
    """Remove leading/trailing whitespace and truncate to max_length."""
    return value.strip()[:max_length] if value else ""


def mask_account_number(account_number: str) -> str:
    """
    Mask all but last 4 characters of an account/loan number.
    Example: "HDFC123456789" → "XXXXXXXXX6789"
    """
    if not account_number or len(account_number) <= 4:
        return account_number
    visible = account_number[-4:]
    masked = "X" * (len(account_number) - 4)
    return masked + visible