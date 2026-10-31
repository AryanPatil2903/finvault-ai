"""Tests for utility functions."""

from src.utils import format_inr, mask_account_number, months_between
from datetime import date


def test_format_inr_lakhs():
    assert format_inr(125000) == "₹1,25,000"

def test_format_inr_crores():
    assert format_inr(5000000) == "₹50,00,000"

def test_format_inr_small():
    assert format_inr(999) == "₹999"

def test_mask_account_number():
    assert mask_account_number("HDFC123456789") == "XXXXXXXXX6789"

def test_mask_short_number():
    assert mask_account_number("1234") == "1234"

def test_months_between():
    assert months_between(date(2023, 1, 1), date(2024, 1, 1)) == 12
    assert months_between(date(2023, 1, 1), date(2023, 6, 1)) == 5