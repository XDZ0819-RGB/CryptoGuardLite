.PHONY: help setup install test lint clean run-api train docker-build docker-run

help:
	@echo "CryptoGuardLite - Makefile Commands"
	@echo "===================================="
	@echo "make setup       - Set up development environment"
	@echo "make install     - Install dependencies"
	@echo "make test        - Run tests"
	@echo "make lint        - Run linters"
	@echo "make clean       - Clean temporary files"
	@echo "make run-api     - Run API server"
	@echo "make train       - Train model"
	@echo "make docker-build - Build Docker image"
	@echo "make docker-run  - Run Docker container"

setup:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	mkdir -p data/raw data/processed data/models logs

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	flake8 src/ --max-line-length=120
	black src/ --check

format:
	black src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/

run-api:
	PYTHONPATH=src python main.py api

train:
	PYTHONPATH=src python scripts/train.py --model hybrid --epochs 50

train-baseline:
	PYTHONPATH=src python scripts/train.py --model baseline --epochs 50

docker-build:
	docker build -t cryptoguardlite:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down
