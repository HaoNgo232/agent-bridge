.PHONY: help install lint format check clean setup

help:
	@echo "Available commands:"
	@echo "  make setup        - Quick setup: check env + install deps + lint"
	@echo "  make install      - Install package with dev dependencies"
	@echo "  make lint         - Run Ruff linter"
	@echo "  make format       - Format code with Ruff"
	@echo "  make check        - Run lint check"
	@echo "  make clean        - Remove cache files"

setup:
	@./scripts/quick-check.sh

install:
	pip install -e ".[dev]"

lint:
	@echo "🔍 Running Ruff linter..."
	ruff check src/

format:
	@echo "✨ Formatting code with Ruff..."
	ruff check --fix src/
	ruff format src/

check: lint
	@echo "✅ All checks passed!"

clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete!"
