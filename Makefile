.PHONY: setup run test demo demo-restore dashboard lineage-api dev infra-up infra-down infra-status infra-test help

help:
	@echo "NanoML Framework Commands"
	@echo ""
	@echo "Quick Start (No Docker Required):"
	@echo "  make setup         - Install NanoML and dependencies (includes dashboard)"
	@echo "  make run           - Run example (shows placeholders by default)"
	@echo "  make demo          - Activate demo mode (fills skeleton with working code)"
	@echo "  make demo-restore  - Restore skeleton code"
	@echo "  make dev           - Start dashboard + lineage API for development"
	@echo "  make dashboard     - Start frontend dashboard (http://localhost:3001)"
	@echo "  make lineage-api   - Start lineage API server (http://localhost:9000)"
	@echo "  make test          - Run tests"
	@echo ""
	@echo "Full Infrastructure (Requires Docker):"
	@echo "  make infra-up      - Start all infrastructure services (Docker)"
	@echo "  make infra-down    - Stop all infrastructure services"
	@echo "  make infra-status  - Check service health"
	@echo "  make infra-test    - Run infrastructure integration tests"

setup:
	@echo "Installing NanoML framework and dependencies..."
	pip3 install -e ".[dev]"
	@echo "✅ NanoML framework installed"
	@echo ""
	@echo "Installing lineage API dependencies..."
	pip3 install -r infrastructure/lineage/requirements.txt
	@echo "✅ Lineage API dependencies installed"
	@echo ""
	@echo "Installing dashboard dependencies..."
	cd infrastructure/dashboard && npm install
	@echo "✅ Dashboard dependencies installed"
	@echo ""
	@echo "Next steps:"
	@echo "  • Quick start (no Docker): make run"
	@echo "  • Start dev environment: make dev"
	@echo "  • Full infrastructure: make infra-up"

run:
	@echo "Running movie recommendations example (local mode, no Docker)..."
	@echo ""
	cd examples/movie_recommendations && python3 pipeline.py
	@echo ""
	@echo "✅ Example completed!"
	@echo ""
	@echo "To run with full infrastructure (Kafka, MLflow, etc.):"
	@echo "  1. make infra-up"
	@echo "  2. cd examples/movie_recommendations && python3 pipeline.py"

test:
	@echo "Running tests..."
	python3 -m pytest tests/ -v --cov=nanoml
	@echo "✅ Tests passed"

dashboard:
	@echo "Starting NanoML dashboard..."
	@echo "Dashboard will be available at http://localhost:3001"
	@echo ""
	cd infrastructure/dashboard && npm start

lineage-api:
	@echo "Starting lineage API server..."
	@echo "API will be available at http://localhost:9000"
	@echo "API docs: http://localhost:9000/docs"
	@echo ""
	cd infrastructure/lineage && uvicorn api:app --host 0.0.0.0 --port 9000 --reload

dev:
	@echo "Starting development environment..."
	@echo ""
	@echo "Starting lineage API in background..."
	@cd infrastructure/lineage && uvicorn api:app --host 0.0.0.0 --port 9000 --reload &
	@sleep 2
	@echo "✅ Lineage API running at http://localhost:9000"
	@echo ""
	@echo "Starting dashboard..."
	@echo "Dashboard will be available at http://localhost:3001"
	@echo ""
	@cd infrastructure/dashboard && npm start

demo:
	@echo "Activating demo mode..."
	@python3 skills/demo-fill/activate.py

demo-restore:
	@echo "Restoring skeleton code..."
	@python3 skills/demo-fill/restore.py

infra-up:
	@echo "Starting NanoRec infrastructure..."
	docker-compose -f deployment/docker-compose.yaml up -d
	@echo "Waiting for services to be ready..."
	sleep 10
	@python3 -c "from core.health import HealthChecker; hc = HealthChecker(); print('✅ All services healthy' if hc.wait_for_services() else '❌ Some services unhealthy')"

infra-down:
	@echo "Stopping NanoRec infrastructure..."
	docker-compose -f deployment/docker-compose.yaml down -v
	@echo "✅ All services stopped"

infra-status:
	@python3 -c "from core.health import HealthChecker; hc = HealthChecker(); results = hc.check_all_services(); [print(f'{name}: {h.status.value} - {h.message}') for name, h in results.items()]"

infra-test:
	@echo "Running infrastructure integration tests..."
	python3 -m pytest tests/integration/test_infrastructure.py -v
