#!/usr/bin/env bash
set -e

echo "Starting infrastructure..."
docker compose up -d postgres redis

echo "Waiting for services..."
sleep 5

echo "Initializing database..."
python -m app.db.init_db

echo "Done."
