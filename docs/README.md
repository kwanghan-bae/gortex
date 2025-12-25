# 🍀 gortex API

gortex의 백엔드 API 서버입니다. 최신 Reactive 기술 스택을 기반으로 현대화되었으며, 고성능 비동기 처리를 지원합니다.

## 🚀 Tech Stack

- **Language**: Kotlin 1.9
- **Framework**: Spring Boot 3.2 (WebFlux)
- **Database**: PostgreSQL
- **Persistence**: Spring Data R2DBC (Reactive Relational Database Connectivity)
- **Concurrency**: Kotlin Coroutines (Suspend Functions, Flow)
- **Auth**: Supabase Auth Integration (JWT)
- **Build Tool**: Gradle (Kotlin DSL)

## 🏗 Architecture

기존의 멀티 모듈 구조를 **단일 모듈(`app:api`)**로 통합하여 복잡도를 낮추고 개발 생산성을 높였습니다.

- **Package Structure**: `com.wallet.clover.api.*`
- **Layers**:
  - `controller`: REST API 엔드포인트 (WebFlux)
  - `service`: 비즈니스 로직 (Coroutines)
  - `repository`: 데이터 액세스 (R2DBC CoroutineCrudRepository)
  - `entity`: 데이터베이스 테이블 매핑
  - `dto`: 데이터 전송 객체

## 🛠 Setup & Run

### Prerequisites
- JDK 21 이상
- Docker (선택 사항, 로컬 DB 실행 시 필요)

### 1. 환경 변수 설정
`application-prod.yml` 또는 환경 변수를 통해 데이터베이스 연결 정보를 설정해야 합니다.

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_URL` | R2DBC Connection URL | `r2dbc:postgresql://host:5432/db` |
| `DB_USERNAME` | Database Username | `postgres` |
| `DB_PASSWORD` | Database Password | `password` |
| `SUPABASE_JWT_SECRET` | Supabase JWT Secret | `your-secret` |

### 2. 실행 (Local)
```bash
# 의존성 설치 및 실행
./gradlew bootRun
```

### 3. 실행 (Docker)
```bash
# Docker 이미지 빌드
docker build -t backend-api .

# 컨테이너 실행
docker run -p 8080:8080 -e DB_URL=... -e DB_USERNAME=... backend-api
```

## ☁️ Deployment (Render)

이 프로젝트는 `Dockerfile`을 포함하고 있어 Render, Fly.io 등 컨테이너 기반 호스팅 서비스에 쉽게 배포할 수 있습니다.

**Render 배포 시 주의사항:**
1. **Environment Variables**: 대시보드에서 위의 환경 변수들을 반드시 설정해야 합니다.
2. **Health Check**: `/actuator/health` 엔드포인트를 사용할 수 있습니다.
3. **Database**: `schema.sql`이 시작 시 자동으로 실행되어 테이블을 생성합니다 (R2DBC 설정).

## 📝 API Endpoints

- **Auth**: `POST /api/v1/auth/login` (Google SSO)
- **User**: `GET /api/v1/users/{id}`
- **Lotto**:
  - `GET /api/v1/lotto/games` (내 게임 조회)
  - `POST /api/v1/lotto/games` (게임 저장)
  - `GET /api/v1/lotto-spots` (판매점 조회)
- **Ticket**:
  - `POST /api/v1/tickets` (티켓 스캔 및 저장)
  - `GET /api/v1/tickets/{id}`
- **Community**:
  - `GET /api/v1/community/posts`
  - `POST /api/v1/community/posts`

## 🔄 Recent Changes (Modernization)
- **JPA -> R2DBC**: 완전한 Non-blocking I/O 전환
- **Reactor -> Coroutines**: `Mono`/`Flux` 대신 `suspend`/`Flow` 사용하여 가독성 향상
- **Single Module**: 불필요한 레이어 제거 및 구조 단순화

## 🛠️ Data Initialization (Admin)
서버 초기 세팅을 위한 데이터 적재 API입니다. (인증 불필요 - 임시 개방)

**1. 당첨 번호 초기화 (JSON API 사용 - 고속)**
```bash
curl -X POST "https://backend-api.onrender.com/api/v1/admin/init/history"
```

**2. 명당 정보 초기화 (HTML 파싱 - 저속)**
```bash
curl -X POST "https://backend-api.onrender.com/api/v1/admin/init/spots"
```
