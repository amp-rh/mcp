.PHONY: help install dev test lint format check build run run-container clean install-claude uninstall-claude

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

dev: ## Install with dev dependencies
	uv sync --extra dev

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov=src --cov-report=term-missing

lint: ## Run linting
	uv run ruff check .

format: ## Format code
	uv run ruff format .
	uv run ruff check --fix .

check: lint test ## Run all checks (lint + test)

run: ## Run MCP server locally (HTTP/SSE on port 8000)
	uv run fastmcp run src/mcp_server/server.py:mcp --transport sse --port 8000

run-dev: ## Run MCP server with auto-reload
	uv run fastmcp dev src/mcp_server/server.py:mcp --transport sse --port 8000

build: ## Build container image
	podman build -t mcp-template:latest .

run-container: ## Run container
	podman run --rm -p 8000:8000 mcp-template:latest

clean: ## Clean up build artifacts
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

install-claude: install ## Install MCP server to Claude Code
	./install-to-claude.sh

uninstall-claude: ## Uninstall MCP server from Claude Code
	./uninstall-from-claude.sh

