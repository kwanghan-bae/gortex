#!/bin/bash
# Gortex Setup Script (Personal Edition)
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}🚀 Gortex 환경 설정을 시작합니다...${NC}"

# 1. 파이썬 버전 체크
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3가 설치되어 있지 않습니다. 설치 후 다시 시도해주세요.${NC}"
    exit 1
fi

# 2. 가상환경 생성
if [ ! -d "venv" ]; then
    echo -e "${GREEN}📦 가상환경(venv) 생성 중...${NC}"
    python3 -m venv venv
fi

# 3. 의존성 설치
source venv/bin/activate
echo -e "${GREEN}📥 필수 패키지 설치 중 (requirements.txt)...${NC}"
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # 기본 패키지 설치
    pip install google-genai langgraph langchain-core rich playwright beautifulsoup4 python-dotenv pandas
    pip freeze > requirements.txt
fi

# 4. Playwright 브라우저 설치
echo -e "${GREEN}🌐 브라우저 엔진 설치 중...${NC}"
playwright install chromium

# 5. .env 파일 체크 및 생성
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 .env 설정이 필요합니다.${NC}"
    echo -e "${YELLOW}💡 Gemini Key가 없으면 'Ollama Only' 모드로 동작합니다.${NC}"
    echo -n "첫 번째 Gemini API 키를 입력하세요 (선택, 엔터로 스킵): "
    read -r API_KEY_1
    API_KEY_1=$(echo "$API_KEY_1" | xargs) # 공백 제거
    
    if [ -z "$API_KEY_1" ]; then
        echo -e "${BLUE}ℹ️ Gemini Key를 건너뜁니다. 로컬 Ollama를 사용합니다.${NC}"
    else
        echo -n "두 번째 Gemini API 키를 입력하세요 (선택, 엔터로 스킵): "
        read -r API_KEY_2
        API_KEY_2=$(echo "$API_KEY_2" | xargs) # 공백 제거
    fi
    
    cat <<EOF > .env
GEMINI_API_KEY_1=$API_KEY_1
GEMINI_API_KEY_2=$API_KEY_2
WORKING_DIR=./workspace
LOG_LEVEL=INFO
MAX_CODER_ITERATIONS=30
TREND_SCAN_INTERVAL_HOURS=24
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
EOF
    echo -e "${GREEN}✅ .env 파일이 생성되었습니다.${NC}"
fi

# 6. 실행 권한 부여 및 바로가기 생성
chmod +x run.sh scripts/pre_commit.sh
if [ ! -f "start.sh" ]; then
    cat <<EOF > start.sh
#!/bin/bash
./run.sh
EOF
    chmod +x start.sh
fi

echo -e "${BLUE}✨ 모든 준비가 끝났습니다!${NC}"
echo -e "${GREEN}👉 './start.sh'를 실행하여 Gortex를 시작하세요.${NC}"
