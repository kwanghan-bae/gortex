#!/bin/bash
# Gortex Unified Startup Script

# 1. 환경 변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 2. 인자 처리
case "$1" in
    "worker")
        echo "🚀 Starting Distributed Worker..."
        python3 main.py worker
        ;;
    "api")
        echo "📡 Starting Web API Dashboard..."
        python3 main.py dashboard
        ;;
    "full")
        echo "🌀 Starting Full Gortex Cluster (Master + Worker + API)..."
        python3 main.py worker &
        python3 main.py dashboard &
        sleep 2
        python3 main.py start
        ;;
    *)
        echo "🍀 Starting Gortex Master System..."
        python3 main.py start
        ;;
esac