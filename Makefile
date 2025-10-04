
.PHONY: format lint test run install clean check all help

# Install dependencies
install:
	pip install -r requirements.txt

# Format code
format:
	black . && isort .

# Lint code
lint:
	flake8 .

# Run tests
test:
	pytest -q

# Run the Streamlit application
run:
	streamlit run app.py

# Clean cache and temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

# Run all quality checks (format, lint, test)
check: format lint test

# Run everything (install, check, then start app)
all: install check run

# Show help
help:
	@echo "Available commands:"
	@echo "  install  - Install project dependencies"
	@echo "  format   - Format code with black and isort"
	@echo "  lint     - Run flake8 linting"
	@echo "  test     - Run pytest tests"
	@echo "  run      - Start Streamlit application"
	@echo "  clean    - Remove cache files and temporary data"
	@echo "  check    - Run format, lint, and test"
	@echo "  all      - Install deps, run checks, start app"
	@echo "  help     - Show this help message"
