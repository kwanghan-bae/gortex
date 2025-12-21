# Next Session

## Session Goal
- 시스템 전역 텍스트 로컬라이징 엔진 구축 (System Localization v1)

## Context
- 현재 에이전트의 사고(`thought`), 도구 결과 메시지, 시스템 로그 등이 여러 언어로 혼재되어 출력됨.
- `state["ui_language"]` 설정에 따라 시스템이 사용하는 모든 표준 메시지(예: "작업 완료", "오류 발생")를 해당 언어로 자동 치환해주는 중앙 집중식 번역 엔진이 필요함.

## Scope
### Do
- `docs/i18n/` 디렉토리에 언어별 사전 파일(`ko.json`, `en.json` 등) 작성.
- `utils/translator.py`에 싱글톤 `SystemTranslator` 클래스 추가 및 템플릿 치환 로직 구현.
- `main.py`와 각 에이전트 노드에서 하드코딩된 한글/영어 메시지를 키값(Key) 기반의 호출로 교체.

### Do NOT
- 에이전트의 '자유로운 사고(LLM Output)' 자체를 강제 번역하지 말 것 (표준 시스템 메시지에 집중).

## Expected Outputs
- `docs/i18n/*.json`, `utils/translator.py`, `main.py` 수정.

## Completion Criteria
- `/language en` 명령어로 설정을 바꿨을 때, 시스템 표준 메시지들이 즉시 영어로 바뀌어 출력되는 것이 확인되어야 함.