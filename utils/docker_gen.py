import os
import logging

logger = logging.getLogger("GortexDockerGen")

class DockerGenerator:
    """
    프로젝트 환경을 분석하여 Dockerfile 및 docker-compose.yml을 생성하는 엔진.
    """
    def __init__(self, project_dir: str = "."):
        self.project_dir = project_dir

    def generate_dockerfile(self) -> str:
        """기본 Python 환경의 Dockerfile 생성"""
        python_version = "3.14-slim" # 최신 버전 기준
        
        dockerfile_content = f"""# Gortex Auto-Generated Dockerfile
FROM python:{python_version}

# 필수 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# 실행 권한 부여
RUN chmod +x run.sh || true

# 기본 실행 명령어 (Gortex 메인 진입점)
CMD ["python", "main.py"]
"""
        try:
            with open(os.path.join(self.project_dir, "Dockerfile"), "w") as f:
                f.write(dockerfile_content)
            return "✅ Dockerfile has been generated successfully."
        except Exception as e:
            return f"❌ Failed to generate Dockerfile: {e}"

    def generate_compose(self) -> str:
        """기본 docker-compose.yml 생성"""
        compose_content = """version: '3.8'

services:
  gortex:
    build: .
    volumes:
      - .:/app
    env_file:
      - .env
    stdin_open: true
    tty: true
    restart: always
"""
        try:
            with open(os.path.join(self.project_dir, "docker-compose.yml"), "w") as f:
                f.write(compose_content)
            return "✅ docker-compose.yml has been generated successfully."
        except Exception as e:
            return f"❌ Failed to generate docker-compose.yml: {e}"

if __name__ == "__main__":
    gen = DockerGenerator()
    print(gen.generate_dockerfile())
    print(gen.generate_compose())
