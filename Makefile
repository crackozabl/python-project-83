install:
	poetry install

install-uv:
	uv sync

.PHONY = build start dev install

build:
	psql -a -d $$DATABASE_URL -f database.sql

dev: build
	poetry run flask --app page_analyzer:app run --debug

PORT ?= 8000
start: 
	curl -LsSf https://astral.sh/uv/install.sh | sh
	/opt/render/.local/bin/uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

lint:
	flake8
