# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Synaptic Search UI & Interaction Complete (v1.6.2)

## 🧠 Current Context
코드 검색 인터페이스가 완성되었습니다. 사용자와 에이전트 모두 프로젝트의 지식 베이스(인덱스)에 자유롭게 접근할 수 있으며, 이는 복잡한 대규모 프로젝트 작업 시의 인지 부하를 획기적으로 낮춰줍니다.

## 🎯 Next Objective
**Auto-Dependency Resolution**
1. **`Dependency Detection`**: 에이전트가 코드를 작성하거나 실행할 때 발생할 수 있는 `ModuleNotFoundError`를 감지합니다.
2. **`Auto-Install Node`**: `Optimizer` 또는 새로운 `Installer` 노드를 통해 `pip install` 명령어를 생성하고, `requirements.txt`를 자동으로 업데이트하는 자가 수복 워크플로우를 구축합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 코드 인덱스 검색 명령어 및 UI 구현 완료 (v1.6.2).
- 다음 목표: 누락된 의존성 자동 설치 엔진 구축.

작업 목표:
1. `agents/coder.py`의 오류 대응 매뉴얼에 `ModuleNotFoundError` 발생 시 의존성 설치 단계를 계획하도록 지침을 보강해줘.
2. `utils/tools.py`의 `execute_shell`에서 설치 명령어 실행 시 `requirements.txt`에 해당 패키지를 자동 추가하는 보조 기능을 검토해줘.
```