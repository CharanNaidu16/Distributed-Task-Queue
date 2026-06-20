# Convenience shortcuts. Run `make help` to list targets.
.DEFAULT_GOAL := help

.PHONY: help up down logs build test lint scale clean seed

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

up: ## Start the whole system (build if needed)
	docker-compose up --build

down: ## Stop and remove containers
	docker-compose down

logs: ## Tail logs from all services
	docker-compose logs -f

build: ## Build images without starting
	docker-compose build

scale: ## Run with 3 workers to demo horizontal scaling
	docker-compose up --build --scale worker=3

test: ## Run the backend test suite in a container
	docker-compose run --rm api pytest -q

lint: ## Lint the backend with ruff
	docker-compose run --rm api ruff check .

clean: ## Stop everything and remove volumes (wipes Redis data)
	docker-compose down -v
