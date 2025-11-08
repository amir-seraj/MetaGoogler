.PHONY: help install dev-install run test clean lint format docs

help:
	@echo "🎵 Meta-Googler Project Commands"
	@echo "=================================="
	@echo ""
	@echo "Installation:"
	@echo "  make install       - Install project with dependencies"
	@echo "  make dev-install   - Install with dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run           - Launch the GUI application"
	@echo "  make test          - Run all tests"
	@echo "  make lint          - Run linting (flake8)"
	@echo "  make format        - Format code (black, isort)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         - Clean build artifacts and cache"
	@echo "  make docs          - Build documentation"
	@echo ""

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

run:
	python -m src.main

test:
	pytest tests/ -v --cov=src

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

docs:
	@echo "📚 Documentation available in docs/"
	@ls -lh docs/

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.py[cod]" -delete
	find . -type f -name "*~" -delete
	@echo "✓ Cleaned up build artifacts"
