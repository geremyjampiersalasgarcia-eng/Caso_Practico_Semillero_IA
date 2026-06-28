# Makefile
# Atajos de comandos para agilizar el desarrollo

.PHONY: up down test ingest lint

up:
	docker-compose up --build

down:
	docker-compose down

test:
	cd backend && pytest -v --cov=app

ingest:
	cd backend && python scripts/ingest.py

lint:
	cd backend && flake8 app && black app
