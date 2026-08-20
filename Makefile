.PHONY: test lint format all install clean

install:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest --cov=dqlite --cov-report=term-missing -v

lint:
	black --check dqlite tests
	ruff check dqlite tests
	mypy dqlite

format:
	black dqlite tests
	ruff check --fix dqlite tests

all: format test lint

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
