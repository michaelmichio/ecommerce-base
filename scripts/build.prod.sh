#!/bin/bash

set -e

echo "⚙️  Building Docker images..."
docker compose --profile prod --build

echo "🚀 Starting containers in background..."
docker compose --profile prod up -d

echo "🐍 Running Alembic migrations inside backend container..."
docker compose run --rm backend bash -c "
    echo '🔄 Removing old migration files...';
    rm -rf app/alembic/versions/*;

    echo '📦 Generating new Alembic revision...';
    alembic -c app/alembic.ini revision --autogenerate -m \"init\";

    echo '⬆️ Upgrading database to head...';
    alembic -c app/alembic.ini upgrade head;

    echo '✅ Alembic init completed successfully.';
"
