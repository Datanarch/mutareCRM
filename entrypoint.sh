#!/bin/sh
echo "Aplicando migraciones..."
poetry run alembic upgrade head
echo "Iniciando servidor..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
