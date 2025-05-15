#!/bin/bash

if [ -d ".venv" ]; then
  VENV_DIR=".venv"
elif [ -d "venv" ]; then
  VENV_DIR="venv"
else
  echo "Virtual environment not found!"
  echo "Please create one using: python -m venv venv"
  exit 1
fi

# Try Unix-style activation first
if [ -f "$VENV_DIR/bin/activate" ]; then
  source "$VENV_DIR/bin/activate"
# Fallback to Windows-style activation
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
  source "$VENV_DIR/Scripts/activate"
else
  echo "Activation script not found in $VENV_DIR!"
  exit 1
fi

echo "Activated virtual environment."

echo "install the requirements library"
pip install -r requirements.txt

if [[ $# -ne 1 ]]; then
    echo "Usage: start [dev] dev-development or [prod] production-environment"
    exit 1
fi

ENV=$1

if [ "$ENV" == "prod" ]; then
    echo "Starting Flask in PRODUCTION mode..."
    export FLASK_ENV=production
    export ENV_FILE=".env.production"
else
    echo "Starting Flask in DEVELOPMENT mode..."
    export FLASK_ENV=development
    export ENV_FILE=".env.development"
fi

if [ -f "$ENV_FILE" ]; then
    export $(cat $ENV_FILE | xargs)
    echo "Loaded environment from $ENV_FILE"
else
    echo "Environment file $ENV_FILE not found!"
    exit 1
fi

export FLASK_APP=run.py

if [ ! -d "migrations" ] || [ -z "$(ls -A migrations)" ]; then
  echo "'migrations/' is missing or empty. Running 'flask db init'..."
  flask db init
fi

echo "Generating migration..."
flask db migrate -m "Auto migration"

echo "Applying migration..."
flask db upgrade

flask run

