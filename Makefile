.PHONY: install migrate makemigrations run test clean docker-build docker-up docker-down docker-logs docker-restart docker-init docker-up-db docker-up-web

install:
	poetry install

migrate:
	poetry run python manage.py migrate

makemigrations:
	poetry run python manage.py makemigrations chatapp

run:
	poetry run python manage.py runserver
	
# Test
test:
	PYTHONPATH=. poetry run python manage.py test -v 2

test-all:
	PYTHONPATH=. poetry run pytest chatapp/tests -v

test-verbose:
	PYTHONPATH=. poetry run python manage.py test -v 2

test-coverage:
	PYTHONPATH=. poetry run coverage run -m pytest chatapp/tests -v
	poetry run coverage report

shell:
	poetry run python manage.py shell

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

setup: install migrate
	@echo "Setup completed!"

update: install makemigrations migrate
	@echo "Database updated"

load-documents:
	poetry run python manage.py load_documents $(DIR)

# Docker commands
ENV_FILE=./environments/.env.local

docker-up:
	docker-compose --env-file $(ENV_FILE) up -d

docker-down:
	docker-compose --env-file $(ENV_FILE) down -v

docker-build:
	docker-compose --env-file $(ENV_FILE) build

docker-init: docker-build docker-up docker-migrate

docker-makemigrations:
	docker-compose exec web poetry run python manage.py makemigrations chatapp

docker-migrate:
	docker-compose exec web poetry run python manage.py migrate

docker-logs:
	docker-compose logs -f web

docker-shell:
	docker-compose exec web bash

docker-db:
	docker-compose exec db psql -U $$(grep POSTGRES_USER $(ENV_FILE) | cut -d '=' -f2) -d $$(grep POSTGRES_DB $(ENV_FILE) | cut -d '=' -f2)