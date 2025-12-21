# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Agent Economy & Gamified Collaboration Complete (v2.1.4)

## 🧠 Current Context
에이전트 경제 시스템(Agent Economy)이 도입되어 이제 에이전트들은 자신의 작업 품질에 따라 평판 포인트를 획득하고 레벨업할 수 있습니다. 이는 시스템 내부의 협업 품질을 게임화된 방식으로 유도하며, 에이전트 간의 상호 작용을 더 역동적으로 만듭니다.

## 🎯 Next Objective
**Event-Driven Swarm (Message Queue Integration)**
1. **`Event Pipeline`**: 현재의 인메모리 병렬 처리(`asyncio.gather`)를 넘어, Redis나 RabbitMQ와 같은 외부 메시지 큐를 활용한 이벤트 기반 스웜(Swarm) 아키텍처를 설계합니다.
2. **`Asynchronous Tasking`**: 에이전트가 시간이 오래 걸리는 작업(대규모 크롤링, 빌드 등)을 큐에 던지고 다른 작업을 계속 수행하다가, 완료 이벤트가 발생하면 결과를 병합하는 비동기 워크플로우를 구축합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 에이전트 경제 및 평판 시스템 완료 (v2.1.4).
- 다음 목표: 이벤트 기반 분산 스웜(Event-Driven Swarm) 기초 설계.

작업 목표:
1. `utils/cache.py` 또는 신규 `utils/message_queue.py`를 통해 Redis 기반의 메시지 큐 인터페이스를 작성해줘.
2. `agents/swarm.py`를 수정하여 큐를 통해 작업을 발행(Publish)하고 결과를 구독(Subscribe)하는 비동기 처리 로직을 구상해줘.
```