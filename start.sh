#!/bin/bash
# Gortex One-Click Entry Point

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 초기 설치 여부 확인
if [ ! -d "venv" ] || [ ! -f ".env" ]; then
    echo -e "${BLUE}🔨 초기 설정이 필요합니다. 설정을 시작합니다...${NC}"
    ./setup.sh
fi

# 2. 시스템 기동
echo -e "${GREEN}🚀 Gortex를 기동합니다...${NC}"
./run.sh "$@"
