# MTG API Development Automation
# Run `just` to see available commands

default:
    @just --list

# Install all dependencies
install:
    uv sync

# Install dependencies with specific extras
install-tests:
    uv sync --extra tests

install-dev:
    uv sync --extra dev

install-app:
    uv sync --extra app

install-training:
    uv sync --extra training

install-all:
    uv sync --all-extras

# Development server commands
dev-api:
    uv run fastapi dev api/main.py --host 0.0.0.0

dev-app:
    uv run streamlit run app/app.py

dev-huey:
    uv run huey_consumer.py tasks.tasks.huey

dev-mcp:
    API_BASE_URL=http://localhost:8000 uv run python -m mcp_server.server

# Combined development workflows
dev: install-dev
    @echo "Starting development environment..."
    @echo "Run 'just docker-up' in another terminal for services"
    just dev-api

ci: format-check lint test
    @echo "✅ CI checks passed"

# Docker development
docker-up *services:
    docker-compose up {{services}}

docker-up-api:
    docker-compose up api

docker-up-app:
    docker-compose up app

docker-up-mcp:
    docker-compose up mcp

docker-up-web:
    docker-compose up web-app

# VPS development - web-app with hot reload connecting to VPS API
dev-web-vps:
    @echo "🚀 Starting web-app in VPS development mode..."
    @echo "📡 This will create an SSH tunnel to VPS and run web-app with hot reload"
    @echo "🔗 Web app will be available at: http://localhost:3000"
    @echo "🔗 VPS API will be tunneled at: http://localhost:8000"
    @echo ""
    @echo "⚙️  Using docker-compose.vps-dev.yml configuration"
    docker-compose -f docker-compose.vps-dev.yml up

# Stop VPS development environment
dev-web-vps-down:
    @echo "🛑 Stopping VPS development environment..."
    docker-compose -f docker-compose.vps-dev.yml down

docker-down:
    docker-compose down

docker-build *services:
    docker-compose build {{services}}

docker-logs service:
    docker-compose logs -f {{service}}

docker-restart service:
    docker-compose restart {{service}}

# Testing
test *args:
    uv run --extra tests pytest {{args}}

test-cov:
    uv run --extra tests pytest --cov --cov-report=html

test-watch:
    uv run --extra tests pytest --watch

test-file file:
    uv run --extra tests pytest {{file}} -v

# Code quality
lint:
    uv run --extra dev ruff check .

lint-fix:
    uv run --extra dev ruff check --fix .

format:
    uv run --extra dev ruff format .

format-check:
    uv run --extra dev ruff format --check .

pre-commit:
    uv run --extra dev pre-commit run --all-files

# Type checking (if mypy is added later)
types:
    @echo "Type checking not configured yet - add mypy to dev dependencies"

# Scripts
mtg-events *args:
    uv run python scripts/mtg_events.py {{args}}

# Common MTG events shortcuts
events:
    just mtg-events list-events

events-compact:
    just mtg-events list-events --format compact

events-whatsapp:
    just mtg-events list-events --format whatsapp

events-test:
    just mtg-events test-connection

# Database operations
db-connect:
    @echo "Connecting to MongoDB at localhost:27017 (root/root)"
    mongosh mongodb://root:root@localhost:27017/mtg

db-tunnel:
    @echo "Creating SSH tunnel to VPS MongoDB (localhost:27017 -> mtg-api-vps:27017)"
    @echo "Press Ctrl+C to close the tunnel"
    ssh -L 27017:localhost:27017 mtg-api-vps -N

# Clean build artifacts
clean:
    rm -rf dist/ build/ *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

# Update dependencies
update:
    uv update

update-lock:
    uv lock --upgrade

# Environment management
sync:
    uv sync --frozen

sync-dev:
    uv sync --frozen --extra dev --extra tests

# Show project info
info:
    @echo "MTG API Project Information"
    @echo "=========================="
    @echo "Python version: $(cat .python-version)"
    @echo "uv version: $(uv --version)"
    @echo ""
    @echo "Available services:"
    @echo "  - API (FastAPI): http://localhost:8000"
    @echo "  - App (Streamlit): http://localhost:8501"
    @echo "  - MCP Server: http://localhost:8002"
    @echo "  - MongoDB: mongodb://root:root@localhost:27017/mtg"
    @echo "  - Redis: redis://localhost:6379"
    @echo "  - Meilisearch: http://localhost:7700"
    @echo ""
    @echo "Run 'just' to see all available commands"

# Health checks
health:
    @echo "Checking service health..."
    @curl -s http://localhost:8000/ping && echo "✅ API is healthy" || echo "❌ API is down"
    @curl -s http://localhost:8501/_stcore/health && echo "✅ App is healthy" || echo "❌ App is down"
    @curl -s http://localhost:8002/health && echo "✅ MCP is healthy" || echo "❌ MCP is down"
    @curl -s http://localhost:7700/health && echo "✅ Meilisearch is healthy" || echo "❌ Meilisearch is down"

# Export requirements (for compatibility)
export-requirements:
    uv export --format requirements-txt > requirements.txt

export-dev-requirements:
    uv export --extra dev --extra tests --format requirements-txt > requirements-dev.txt
