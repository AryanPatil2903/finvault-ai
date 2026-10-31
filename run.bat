@echo off
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -q -r requirements.txt
if not exist .env copy .env.example .env
if not exist logs mkdir logs
if not exist ui\node_modules (cd ui && npm install && cd ..)

start "FinVault API" cmd /k "call .venv\Scripts\activate && uvicorn api.app:app --reload --port 8000"
cd ui && npm run dev