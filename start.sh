#!/bin/bash
# Gortex One-Click Entry Point

# Ensure dependencies
if [ ! -d "venv" ] || [ ! -f ".env" ]; then
    echo "🔨 Setup required..."
    ./setup.sh
fi

# Run via Python CLI
python3 main.py start "$@"
