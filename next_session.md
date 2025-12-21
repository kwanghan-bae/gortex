# ⏭️ Gortex Next Session Context

**Date:** 2024-12-21
**Status:** Automated Test Generation Complete (v2.2.17)

## 🧠 Current Context
시스템은 품질(테스트), 효율(에너지), 진화(리팩토링)의 3박자를 갖추었습니다. 이제 사용자가 자신만의 워크플로우를 시스템에 가르칠 수 있는 '자연어 매크로(Natural Language Macro)' 기능을 도입하여 개인화된 경험을 극대화해야 합니다.

## 🎯 Next Objective
**Natural Language Macro (Skill Learning v1)**
1. **`Macro Recognition`**: `agents/manager.py`가 "앞으로 X라고 하면 Y, Z를 수행해"와 같은 사용자의 가르침(Teaching) 의도를 인식합니다.
2. **`Skill Memory`**: `core/evolutionary_memory.py`에 새로운 스킬(매크로)을 저장하고, 이후 `planner`가 이를 참조하여 복합적인 작업을 단일 명령어로 수행할 수 있도록 확장합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 테스트 자동 생성 로직 완료 (v2.2.17).
- 다음 목표: 자연어 매크로 학습 기능 구현.

작업 목표:
1. `agents/manager.py`의 시스템 프롬프트에 "사용자가 새로운 작업 패턴을 가르치려 할 때(If user teaches a new macro...)"에 대한 처리 지침을 추가해줘.
2. `core/evolutionary_memory.py`에 매크로(Macro) 형태의 지식을 별도로 저장하고 관리하는 `save_macro` 및 `get_macro` 메서드를 구현해줘.
```
