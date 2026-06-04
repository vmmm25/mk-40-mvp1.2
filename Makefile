.PHONY: install test lint clean security docker format pre-commit

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	python -m pytest tests/ -v --tb=short --cov=. --cov-report=html

lint:
	flake8 . --max-line-length=120 --exclude=.venv,__pycache__
	black --check --line-length=120 .

format:
	black --line-length=120 .

security:
	bandit -r . -x .venv,__pycache__,tests
	safety check -r requirements.txt

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

docker:
	docker-compose build

docker-run:
	docker-compose up

pre-commit:
	pre-commit run --all-files
