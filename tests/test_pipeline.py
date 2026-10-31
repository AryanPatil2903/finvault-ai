"""Tests for core financial calculation engine."""

import pytest
from datetime import date
from src.finance import (
    calculate_emi, generate_amortization_schedule,
    get_loan_summary, calculate_prepayment_impact, calculate_foir
)


class TestEMICalculation:
    def test_standard_reducing_balance(self):
        emi = calculate_emi(500000, 10.0, 60)
        assert 10500 < emi < 10700  # Expected ~10,624

    def test_zero_interest(self):
        emi = calculate_emi(120000, 0.0, 12)
        assert emi == 10000.0

    def test_flat_rate_higher_than_reducing(self):
        rb = calculate_emi(100000, 12.0, 24, "Reducing Balance")
        flat = calculate_emi(100000, 12.0, 24, "Flat Rate")
        assert flat > rb

    def test_invalid_principal(self):
        with pytest.raises(ValueError):
            calculate_emi(-100, 10.0, 12)

    def test_invalid_tenure(self):
        with pytest.raises(ValueError):
            calculate_emi(100000, 10.0, 0)


class TestAmortization:
    def test_schedule_length_matches_tenure(self):
        schedule = generate_amortization_schedule(500000, 10.0, 24, date(2024, 1, 1))
        assert len(schedule) == 24

    def test_outstanding_reaches_zero(self):
        schedule = generate_amortization_schedule(300000, 9.5, 36, date(2024, 1, 1))
        assert schedule[-1].outstanding_after == 0.0

    def test_interest_decreasing_over_time(self):
        schedule = generate_amortization_schedule(1000000, 8.5, 120, date(2024, 1, 1))
        # Interest component should generally decrease (reducing balance)
        assert schedule[0].interest_component > schedule[-1].interest_component


class TestFOIR:
    def test_normal_foir(self):
        foir = calculate_foir(30000, 100000)
        assert foir == 30.0

    def test_zero_income_returns_zero(self):
        assert calculate_foir(10000, 0) == 0.0


class TestPrepayment:
    def test_prepayment_saves_interest(self):
        scenario = calculate_prepayment_impact(
            current_outstanding=400000,
            annual_interest_rate=10.0,
            emis_remaining=48,
            prepayment_amount=50000,
            first_remaining_emi_date=date(2024, 1, 1),
        )
        assert scenario.interest_saved > 0
        assert scenario.emis_saved > 0
        assert scenario.new_emis_remaining < scenario.original_emis_remaining