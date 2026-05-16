# Variables
API_DIR = apps/api
WEB_DIR = apps/web

# Phony targets tell Make these are actions, not actual files
.PHONY: api-install api-dev api-test api-migrate api-lint chmod-scripts stop start capture-infra

# Installs editable package with development dependencies
api-install:
	pip install -e $(API_DIR)/.[dev]

# Launches the Uvicorn development server
api-dev:
	uvicorn app.main:app --app-dir $(API_DIR)/src --reload

# Runs the test suite using Pytest
api-test:
	python3 -m pytest $(API_DIR)

# Runs database migrations using Alembic (uses -c to point to config file)
api-migrate:
	alembic -c $(API_DIR)/alembic.ini upgrade head

# Lints the codebase using Ruff
api-lint:
	ruff check $(API_DIR)/src $(API_DIR)/tests

# Makes all shell scripts executable
chmod-scripts:
	chmod +x infra/scripts/*.sh

# AWS ECS — stop all services (saves compute cost)
stop:
	./infra/scripts/stop.sh

# AWS ECS — start all services
start:
	./infra/scripts/start.sh

# Capture current AWS infrastructure state to infra/backups/
capture-infra:
	./infra/scripts/capture-infra.sh