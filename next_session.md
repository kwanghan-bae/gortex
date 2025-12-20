# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Git Auto-Deploy & Synchronization Complete (v1.6.8)

## 🧠 Current Context
작업 결과물을 원격 저장소에 자동으로 배포하는 `/deploy` 기능이 성공적으로 통합되었습니다. 이제 Gortex는 로컬 개발을 넘어 원격 협업 및 버전 관리 파이프라인까지 스스로 제어할 수 있게 되었습니다.

## 🎯 Next Objective
**Multi-Channel Notifications**
1. **`Slack/Discord Integration`**: 작업이 완료되거나 중요한 오류(예: 배포 실패, 보안 취약점 발견)가 발생했을 때 지정된 슬랙 또는 디스코드 채널로 알림을 보내는 기능을 구현합니다.
2. **`Status Reporting`**: `/notify` 명령어를 통해 현재 시스템 상태, 토큰 사용량, 최근 성과 요약을 외부 채널로 브로드캐스팅합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- Git 자동 배포 명령어 구현 완료 (v1.6.8).
- 다음 목표: 외부 채널 알림 시스템 구축.

작업 목표:
1. `utils/notifier.py`를 신설하여 Webhook 기반의 슬랙/디스코드 알림 기능을 구현해줘.
2. `main.py`에 `/notify` 명령어를 추가하고, 중요한 마일스톤(작업 완료 등) 달성 시 자동으로 알림을 트리거하는 로직을 검토해줘.
```