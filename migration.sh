#!/bin/bash
set -e

export FLASK_APP=run.py
export FLASK_ENV=development

VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment ($VENV_DIR) not found!"
    echo "Please create one using: python -m venv venv"
    exit 1
fi

source $VENV_DIR/Scripts/activate
echo "Activated virtual environment."

if [ ! -d "migrations" ] || [ -z "$(ls -A migrations)" ]; then
  echo "Initializing migrations..."
  flask db init
fi

flask db migrate -m "Auto migrate model changes"
flask db upgrade

echo "Database is up to date!"
