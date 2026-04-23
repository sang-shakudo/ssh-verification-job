#!/bin/bash
set -e

SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "SSH Verification Job"
echo "Directory: $(pwd)"

export PYTHONUNBUFFERED=1

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package installer..." | tee -a process.log
    curl -LsSf https://astral.sh/uv/install.sh | sh | tee -a process.log
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv | tee -a process.log
fi


# Activate virtual environment
source .venv/bin/activate | tee -a process.log

# Install dependencies using uv
echo "Installing dependencies..."
uv sync | tee -a process.log

uv run python3 main.py