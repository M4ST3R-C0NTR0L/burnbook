.PHONY: install test lint format clean help

help:
	@echo "BurnBook Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install    Install BurnBook in editable mode"
	@echo "  test       Run all tests"
	@echo "  lint       Run linting with ruff"
	@echo "  format     Format code with black"
	@echo "  clean      Clean build artifacts"
	@echo "  roast      Roast the BurnBook codebase itself"

install:
	pip install -e ".[dev]"

test:
	pytest -v

test-cov:
	pytest --cov=burnbook --cov-report=html --cov-report=term

lint:
	ruff check burnbook tests

format:
	black burnbook tests
	ruff check burnbook tests --fix

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

roast:
	burnbook roast . --offline

roast-nuclear:
	burnbook roast . --offline --severity nuclear

report:
	burnbook report . --offline --output burnbook-report.html

publish: clean
	pip install build twine
	python -m build
	twine upload dist/*

.DEFAULT_GOAL := help
