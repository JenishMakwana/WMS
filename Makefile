.PHONY: help dev prod down logs migrate seed test lint

help:
	@echo "CoreInventory — available commands"
	@echo ""
	@echo "  make dev       Start development stack (hot reload)"
	@echo "  make prod      Start production stack"
	@echo "  make down      Stop all containers"
	@echo "  make logs      Tail all container logs"
	@echo "  make migrate   Run Alembic migrations"
	@echo "  make seed      Seed database with demo data"
	@echo "  make test      Run backend tests"
	@echo "  make lint      Type-check frontend"
	@echo "  make secret    Generate a random secret key"

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

prod:
	docker-compose up --build -d

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	docker-compose exec backend alembic upgrade head

revision:
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

seed:
	docker-compose exec backend python -m app.seed

test:
	cd backend && pytest -v --tb=short

lint:
	cd frontend && npx tsc --noEmit

secret:
	python3 -c "import secrets; print(secrets.token_hex(32))"
