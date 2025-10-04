.PHONY: setup test lint format docker-build docker-run run

setup:
poetry install

run:
poetry run python scripts/run_spider.py

lint:
poetry run ruff check app tests

format:
poetry run black app tests

test:
poetry run pytest

docker-build:
docker build -f infra/Dockerfile -t gpt-builder-scraper .

docker-run:
docker run --rm gpt-builder-scraper
