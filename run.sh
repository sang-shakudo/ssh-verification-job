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

# refresh PATH
echo "refresh PATH .. " | tee -a process.log
echo $HOME | tee -a process.log 
find /root/.local/bin | tee -a process.log

source $HOME/.local/bin/env | tee -a process.log
echo $PATH | tee -a process.log

export PATH="/root/.local/bin:$PATH" | tee -a process.log
echo $PATH | tee -a process.log
# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    /root/.local/bin/uv venv | tee -a process.log
fi


# Activate virtual environment
source .venv/bin/activate | tee -a process.log

# Install dependencies using uv
echo "Installing dependencies..."
/root/.local/bin/uv sync | tee -a process.log

echo "Change permissions for SSH key" | tee -a process.log
chmod 400 rbac-policies-rbac-manager-key-for-gitea 

ssh-keyscan -t ed25519,rsa gitea-ssh.hyperplane-gitea.svc.cluster.local | tee -a process.log

/root/.local/bin/uv run python3 main.py