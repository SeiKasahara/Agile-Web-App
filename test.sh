#!/usr/bin/env bash

set -e 

if [ -f ".env.development" ]; then
  echo "loading .env.development"
  set -o allexport
  source .env.development
  set +o allexport
fi


if [ -f "./venv/Scripts/activate" ]; then
    source "./venv/Scripts/activate"
elif [ -f "./.venv/Scripts/activate" ]; then
    source "./.venv/Scripts/activate"
else
    echo "didn't install the venv file!"
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
