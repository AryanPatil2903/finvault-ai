"""Integration tests for API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    resp = await client.post("/api/v1/auth/register", json={
        "full_name": "API Test",
        "email": "apitest@example.com",
        "password": "secure1234",
    })
    assert resp.status_code == 201
    assert resp.json()["email"] == "apitest@example.com"

    login = await client.post("/api/v1/auth/login", json={
        "email": "apitest@example.com",
        "password": "secure1234",
    })
    assert login.status_code == 200
    assert "access_token" in login.json()


@pytest.mark.asyncio
async def test_create_and_list_expense(client, auth_headers):
    create = await client.post("/api/v1/expenses", json={
        "amount": 1500,
        "category": "Food & Dining",
        "transaction_date": "2024-06-15",
    }, headers=auth_headers)
    assert create.status_code == 201
    assert create.json()["amount"] == 1500

    listing = await client.get("/api/v1/expenses", headers=auth_headers)
    assert listing.status_code == 200
    assert len(listing.json()) >= 1


@pytest.mark.asyncio
async def test_emi_calculator_no_auth(client):
    resp = await client.post("/api/v1/loans/calculator/emi", json={
        "principal": 1000000,
        "annual_interest_rate": 8.5,
        "tenure_months": 120,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["emi_amount"] > 0
    assert data["total_interest"] > 0


@pytest.mark.asyncio
async def test_create_loan(client, auth_headers):
    resp = await client.post("/api/v1/loans", json={
        "loan_name": "Home Loan HDFC",
        "loan_type": "Home Loan",
        "lender_name": "HDFC Bank",
        "principal_amount": 5000000,
        "annual_interest_rate": 8.5,
        "tenure_months": 240,
        "disbursement_date": "2023-01-01",
        "first_emi_date": "2023-02-01",
        "emi_due_day": 1,
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["loan_name"] == "Home Loan HDFC"
    assert resp.json()["emi_amount"] > 0