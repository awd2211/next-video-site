# Makefile for VideoSite development

.PHONY: help infra-up infra-down backend-install backend-run frontend-install frontend-run admin-install admin-run db-migrate db-init all-install dev clean format format-backend format-check

help:
	@echo "VideoSite Development Commands"
	@echo ""
	@echo "Infrastructure:"
	@echo "  make infra-up          - Start PostgreSQL, Redis, MinIO"
	@echo "  make infra-down        - Stop infrastructure services"
	@echo ""
	@echo "Backend:"
	@echo "  make backend-install   - Install Python dependencies"
	@echo "  make backend-run       - Run backend server"
	@echo "  make db-migrate        - Create database migration"
	@echo "  make db-upgrade        - Run database migrations"
	@echo "  make db-init           - Initialize database with migrations"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format            - Format all code (backend)"
	@echo "  make format-backend    - Format Python code with Black and isort"
	@echo "  make format-check      - Check code formatting without changes"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend-install  - Install frontend dependencies"
	@echo "  make frontend-run      - Run frontend dev server"
	@echo ""
	@echo "Admin:"
	@echo "  make admin-install     - Install admin frontend dependencies"
	@echo "  make admin-run         - Run admin frontend dev server"
	@echo ""
	@echo "Combined:"
	@echo "  make all-install       - Install all dependencies"
	@echo "  make dev               - Start everything for development"
	@echo "  make clean             - Clean all containers and volumes"

# Infrastructure
infra-up:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Waiting for services to be ready..."
	@sleep 3
	@echo "Infrastructure is ready!"
	@echo "PostgreSQL: localhost:5432 (postgres/postgres)"
	@echo "Redis: localhost:6379"
	@echo "MinIO: localhost:9000 (console: localhost:9001)"

infra-down:
	docker-compose -f docker-compose.dev.yml down

# Backend
backend-install:
	cd backend && \
	python3 -m venv venv && \
	. venv/bin/activate && \
	pip install -r requirements.txt

backend-run:
	cd backend && \
	. venv/bin/activate && \
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

db-migrate:
	cd backend && \
	. venv/bin/activate && \
	alembic revision --autogenerate -m "$(MSG)"

db-upgrade:
	cd backend && \
	. venv/bin/activate && \
	alembic upgrade head

db-init:
	cd backend && \
	. venv/bin/activate && \
	alembic revision --autogenerate -m "Initial migration" && \
	alembic upgrade head

# Frontend
frontend-install:
	cd frontend && pnpm install

frontend-run:
	cd frontend && pnpm run dev

# Admin Frontend
admin-install:
	cd admin-frontend && pnpm install

admin-run:
	cd admin-frontend && pnpm run dev

# Combined commands
all-install: backend-install frontend-install admin-install
	@echo "All dependencies installed!"

dev: infra-up
	@echo "Infrastructure started. Now run in separate terminals:"
	@echo "  1. make backend-run"
	@echo "  2. make frontend-run"
	@echo "  3. make admin-run"

# Code Quality
format: format-backend
	@echo "Code formatting complete!"

format-backend:
	cd backend && \
	. venv/bin/activate && \
	pip install -q black isort && \
	black app/ --line-length 88 --exclude "venv|alembic" && \
	isort app/ --profile black --skip venv --skip alembic

format-check:
	cd backend && \
	. venv/bin/activate && \
	pip install -q black isort && \
	black app/ --check --line-length 88 --exclude "venv|alembic" && \
	isort app/ --check --profile black --skip venv --skip alembic

# Clean
clean:
	docker-compose -f docker-compose.dev.yml down -v
	@echo "All services and volumes removed"
