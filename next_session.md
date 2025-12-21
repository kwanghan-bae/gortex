# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Dataset Generator & Learning Loop Complete (v1.9.9)

## 🧠 Current Context
지능형 학습 데이터 생성기가 가동되었습니다. 이제 Gortex는 스스로의 성공적인 경험을 데이터셋으로 축적하며, 이는 향후 Gortex만의 고유한 추론 스타일을 가진 전용 모델을 학습시키는 핵심 자산이 될 것입니다.

## 🎯 Next Objective
**Virtual Cursor (Precision Editing)**
1. **`Contextual Anchoring`**: 파일을 수정할 때 전체를 덮어쓰는 대신, 특정 줄 번호나 키워드를 기준으로 '앵커(Anchor)'를 설정하여 필요한 부분만 정밀하게 수정하는 기능을 구현합니다.
2. **`Delta Apply`**: 에이전트가 생성한 코드 차분(Diff)을 기존 파일에 정확히 병합하여 대규모 파일 수정 시 발생할 수 있는 실수와 토큰 낭비를 최소화합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 자가 학습용 데이터셋 생성 시스템 완료 (v1.9.9).
- 다음 목표: 정밀 편집을 위한 가상 커서(Virtual Cursor) 구축.

작업 목표:
1. `utils/tools.py`에 특정 줄 번호를 기준으로 코드를 삽입/삭제/수정하는 `apply_patch` 메서드를 추가해줘.
2. `coder` 노드에서 대규모 파일 수정 시 `write_file` 대신 `apply_patch`를 활용하도록 지침을 보강해줘.
```
