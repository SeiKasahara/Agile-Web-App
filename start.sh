#!/bin/bash

VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment ($VENV_DIR) not found!"
    echo "Please create one using: python -m venv venv"
    exit 1
fi

source $VENV_DIR/Scripts/activate
echo "Activated virtual environment."

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

flask run