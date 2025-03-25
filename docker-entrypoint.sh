#!/bin/bash

# Esperar a que la base de datos esté lista
echo "Esperando a que la base de datos esté lista..."
until poetry run python manage.py check --database default; do
  echo "Base de datos no disponible, esperando..."
  sleep 2
done
echo "Base de datos lista!"

# Aplicar migraciones
echo "Aplicando migraciones..."
poetry run python manage.py migrate

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
poetry run python manage.py collectstatic --noinput

# Ejecutar el comando que se pase como argumento
exec "$@"