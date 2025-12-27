# Next Session

## Session Goal
- **Advanced CLI UX**: 안전 모드에서 파일 변경 사항을 직관적으로 보여주는 **Rich Diff View** 구현.
- **Dynamic Agent Loader**: `agents.yaml` 설정을 통해 사용자 정의 에이전트를 로드하는 **Agent DSL** 프로토타이핑.

## Context
- `gortex chat`이 기본적으로 동작하지만, 파일 수정 시 검토가 불편함.
- 사용자는 자유로운 에이전트 빌딩을 원하므로, 코드 수정 없이 YAML로 에이전트를 정의하는 구조가 필요함.

## Scope
### Do
- [ ] **Rich Diff View**: `core/cli/safety.py` 개선. `difflib`와 `rich`를 사용하여 변경 전/후 차이를 시각화.
- [ ] **Agent DSL**: `agents.yaml` 정의 및 로더(`core/loader.py`) 구현.
- [ ] **CLI Extension**: `/reload` 명령어로 런타임에 에이전트 설정 다시 불러오기.
- [ ] **Context Logic**: `/add` 명령어 개선 (와일드카드 지원, 예: `/add core/*.py`).

### Do NOT
- 복잡한 Web Dashboard 연동.
- 아직은 멀티 에이전트 간의 복잡한 그래프 로직(순차적 실행 정도만).

## 🏁 Documentation Sync Checklist
- [ ] `SPEC_CATALOG.md` (Agent DSL 명세 추가)
- [ ] `TECHNICAL_SPEC.md` (Diff View 구현 상세 추가)

## Completion Criteria
- 파일 수정 도구 실행 시, 터미널에 컬러풀한 Diff가 출력되고 승인 여부를 물어봐야 함.
- `agents.yaml`에 새로운 에이전트를 정의하고 `/reload` 하면, 해당 에이전트와 대화할 수 있어야 함.
