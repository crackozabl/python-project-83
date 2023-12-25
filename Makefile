install:
	poetry install

.PHONY = build start dev install

build:
	psql -a -d $$DATABASE_URL -f database.sql

dev: build
	poetry run flask --app page_analyzer:app run --debug

PORT ?= 8000
start: build
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

lint:
	flake8
