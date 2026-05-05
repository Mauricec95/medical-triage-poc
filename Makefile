.PHONY: dev dev-backend dev-frontend install install-backend install-frontend \
       test lint demo docker-up docker-down clean

# ─── Local development ────────────────────────────────────────────────

dev: dev-backend dev-frontend

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

install: install-backend install-frontend

install-backend:
	cd backend && pip install -e ".[dev]"

install-frontend:
	cd frontend && npm install

# ─── Quality ──────────────────────────────────────────────────────────

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check app/ tests/
	cd frontend && npm run lint

# ─── Demo ─────────────────────────────────────────────────────────────

demo:
	@echo "🏥 Ingesting sample data..."
	cd backend && python -m app.demo_ingest
	@echo "🚀 Starting services..."
	$(MAKE) dev

# ─── Docker ───────────────────────────────────────────────────────────

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

# ─── Cleanup ──────────────────────────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -f backend/*.db data/*.db
	rm -rf frontend/.next
