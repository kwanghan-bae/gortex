# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Synaptic Map Visualization Complete (v1.6.4)

## 🧠 Current Context
프로젝트의 아키텍처를 시각화하는 `/map` 명령어가 완성되었습니다. 이를 통해 복잡한 모듈 간의 의존 관계와 클래스 계층 구조를 한눈에 파악할 수 있으며, 새로운 프로젝트에 투입되었을 때 빠른 온보딩이 가능해졌습니다.

## 🎯 Next Objective
**Dockerized Environment & Deployment**
1. **`Dockerfile Generation`**: 프로젝트의 `requirements.txt`와 인덱싱된 정보를 바탕으로 최적화된 `Dockerfile`과 `docker-compose.yml`을 자동으로 생성하는 기능을 구현합니다.
2. **`Containerized Execution`**: 에이전트가 코드를 실행할 때 로컬 환경을 오염시키지 않도록 격리된 컨테이너 환경에서 실행하고 결과를 가져오는 선택적 샌드박스 기능을 검토합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 프로젝트 아키텍처 맵 시각화 완료 (v1.6.4).
- 다음 목표: Docker 환경 자동 구성 및 컨테이너화 지원.

작업 목표:
1. `setup.sh` 또는 새로운 `utils/docker_gen.py`를 통해 프로젝트 환경에 맞는 `Dockerfile`을 자동 생성하는 기능을 추가해줘.
2. `main.py`에 `/dockerize` 명령어를 추가하여 컨테이너 빌드 및 실행 기초 환경을 마련해줘.
```