#!/usr/bin/env bash
# One-time setup: create virtual environment, install dependencies, and prepare .env

set -e

echo "Creating virtual environment in .venv ..."
python3 -m venv .venv

echo "Activating virtual environment ..."
source .venv/bin/activate

echo "Installing dependencies ..."
pip install --upgrade pip -q
pip install -r requirements.txt

if [ ! -f .env ]; then
    echo "Copying .env.example -> .env ..."
    cp .env.example .env
    echo ""
    echo "  Edit .env and add your API keys before running experiments:"
    echo "    OPENAI_API_KEY=sk-..."
    echo "    ANTHROPIC_API_KEY=sk-ant-..."
else
    echo ".env already exists, skipping."
fi

echo ""
echo "Setup complete."
echo ""
echo "To activate the environment in future sessions:"
echo "  source .venv/bin/activate"
echo ""
echo "Then run experiments, e.g.:"
echo "  python simulate.py --city chicago --model gpt-4o-2024-08-06 --mode ranked --rounds 10"
