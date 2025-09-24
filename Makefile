
.PHONY: format lint test run

format:
	black . && isort .

lint:
	flake8 .

test:
	pytest -q

run:
	streamlit run app.py
