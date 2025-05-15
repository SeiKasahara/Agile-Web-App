#!/usr/bin/env bash

set -e 

if [ -f ".env.test" ]; then
  echo "loading .env.test"
  set -o allexport
  source .env.test
  set +o allexport
fi

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
export FLASK_APP=app
export FLASK_ENV=testing

if [ -f "requirements.txt" ]; then
    echo "install dependencies"
    pip install -r requirements.txt
fi

echo "Running the test"
python -m unittest discover -s tests -v

echo "Test finished"
