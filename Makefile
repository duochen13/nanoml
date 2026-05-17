.PHONY: infra-up infra-down infra-status infra-test help

help:
	@echo "NanoRec Infrastructure Commands"
	@echo ""
	@echo "  make infra-up      - Start all infrastructure services"
	@echo "  make infra-down    - Stop all infrastructure services"
	@echo "  make infra-status  - Check service health"
	@echo "  make infra-test    - Run infrastructure integration tests"

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
