# Next Session

## Session Goal
- 에이전트 출력 및 문서의 실시간 다국어 번역 (Omni-Translator v1)

## Context
- Gortex는 글로벌 협업을 지향하지만, 현재 에이전트 출력과 문서는 한글과 영어 위주로 작성되고 있음.
- 사용자가 웹 대시보드에서 원하는 언어를 선택하면, 에이전트의 사고 과정과 결과물, 그리고 `docs/` 하위의 가이드라인들을 실시간으로 번역하여 표시해야 함.

## Scope
### Do
- `utils/translator.py`를 확장하여 웹 스트리밍용 번역 브리지 구현.
- 웹 대시보드 클라이언트로부터 언어 선택(`lang_preference`) 요청을 수신하는 로직 추가.
- `DashboardUI`의 모든 출력 데이터를 전송 전 타겟 언어로 실시간 변환하여 스트리밍.

### Do NOT
- 모든 문서를 파일로 다시 쓰지 말 것 (UI 표시 단계에서의 가상 번역 위주).

## Expected Outputs
- `utils/translator.py`, `ui/web_server.py`, `ui/dashboard.py` 수정.

## Completion Criteria
- 웹 대시보드에서 언어 설정을 변경했을 때, 실시간으로 들어오는 에이전트의 사고와 메시지가 해당 언어로 번역되어 표시되는 것이 확인되어야 함.
