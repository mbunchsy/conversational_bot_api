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
test-all:
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=config.settings poetry run pytest chatapp/tests -v --ds=config.settings

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

# UI commands
install-ui:
	poetry install --with ui

run-ui:
	PYTHONPATH=$(PWD) poetry run streamlit run ui/main.py

# Docker commands
ENV_FILE=./environments/.env.docker

docker-up:
	docker-compose --env-file $(ENV_FILE) up -d

docker-down:
	docker-compose --env-file $(ENV_FILE) down -v

docker-build:
	poetry lock && docker-compose --env-file $(ENV_FILE) build

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

docker-load-documents:
	@echo "Copying documents to container..."
	@docker cp $(DIR) bot_api:/app/docs
	@echo "Loading documents into database..."
	@docker-compose exec web poetry run python manage.py load_documents /app/docs
	@echo "Documents loaded successfully"