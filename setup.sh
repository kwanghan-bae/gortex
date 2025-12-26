#!/bin/bash
# Gortex Setup Script
set -e

echo "🚀 Gortex Environment Setup"

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required."
    exit 1
fi

# 2. Virtual Env (Skip if in sandbox, but good practice)
if [ ! -d "venv" ]; then
    echo "📦 Creating venv..."
    python3 -m venv venv
fi

# 3. Install Deps
# source venv/bin/activate (Skipped as we are likely in an environment where we just want to run python)
# But for the script to be robust:
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo "📥 Installing requirements..."
pip install -r requirements.txt

# 4. Run Python Init
python3 main.py init

echo "✨ Setup Complete. Run ./start.sh"
