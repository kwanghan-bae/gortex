#!/bin/bash
# Gortex Execution Wrapper
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}❌ 가상환경이 없습니다. ./setup.sh를 먼저 실행해주세요.${NC}"
    exit 1
fi

# 실행
python3 main.py "$@"

# 실패 시 처리
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo -e "\n${RED}⚠️  Gortex가 비정상 종료되었습니다 (Exit Code: $EXIT_CODE).${NC}"
    echo -e "패키지 누락이 의심된다면 './setup.sh'를 다시 실행하거나 'requirements.txt'를 확인하세요."
fi

exit $EXIT_CODE
