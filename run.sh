#!/usr/bin/env bash
set -euo pipefail

[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
[ -f .env ] || cp .env.example .env
mkdir -p logs models data/raw data/processed data/outputs

(cd ui && [ -d node_modules ] || npm install)

# Backend in background, frontend in foreground; Ctrl+C stops both
uvicorn api.app:app --reload --port 8000 &
BACK=$!
trap "kill $BACK" EXIT
(cd ui && npm run dev)