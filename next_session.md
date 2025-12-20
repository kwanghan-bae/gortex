# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Multi-Channel Notifications Complete (v1.6.9)

## 🧠 Current Context
외부 채널 알림 시스템이 성공적으로 안착되었습니다. 이제 사용자는 터미널 앞에 앉아 있지 않아도 Slack이나 Discord를 통해 Gortex의 작업 완료 보고를 실시간으로 받을 수 있습니다.

## 🎯 Next Objective
**Gortex Web Dashboard (Lite)**
1. **`Web Streaming`**: 현재의 `rich` 기반 터미널 출력을 브라우저에서도 동일하게 스트리밍할 수 있는 기초 인프라(FastAPI + WebSockets)를 구축합니다.
2. **`Real-time UI`**: 터미널의 레이아웃(Chat, Thought, Stats)을 웹에서도 재현하여 원격지에서 모바일이나 PC 브라우저로 Gortex의 지능적 활동을 관찰할 수 있게 합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 외부 알림 시스템 구축 완료 (v1.6.9).
- 다음 목표: 웹 기반 실시간 모니터링 대시보드 구축.

작업 목표:
1. `ui/web_server.py`를 신설하여 FastAPI 기반의 웹 서버를 구현하고, WebSocket을 통해 `DashboardUI`의 데이터를 브라우저로 전송하는 로직을 작성해줘.
2. `ui/dashboard.py`를 수정하여 터미널과 웹 서버 양쪽으로 데이터를 브로드캐스팅하는 구조로 변경해줘.
```
