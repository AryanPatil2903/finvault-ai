.PHONY: install run run-ui test lint docker clean seed

install:
	pip install -r requirements.txt
	cd ui && npm install

run:
	uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

run-ui:
	cd ui && npm run dev

test:
	pytest tests/ -v --cov=src --cov=api --cov-report=term-missing

lint:
	flake8 src api config database --max-line-length=100
	black --check src api config database

format:
	black src api config database

seed:
	python -m scripts.seed_db

docker:
	cd ui && npm ci && npm run build
	docker compose -f infra/docker-compose.yml up --build

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache .coverage logs/*.log test_finvault.db