# Session 0021

## Goal
- 에이전트 출력 및 문서의 실시간 다국어 번역 (Omni-Translator v1)

## What Was Done
- **core/state.py 수정**: 사용자의 언어 설정을 관리하는 `ui_language` 필드 추가.
- **utils/translator.py 수정**: 여러 텍스트 항목을 효율적으로 일괄 번역하는 `translate_batch` 메서드 구현.
- **ui/web_server.py 수정**: 클라이언트로부터 언어 변경 메시지(`set_lang`)를 수신하여 시스템 큐에 전달하는 로직 추가.
- **ui/dashboard.py 수정**: 데이터를 웹으로 전송하기 직전, `ui_language`에 맞춰 사고(Thought)와 단계(Step) 정보를 실시간 번역하여 스트리밍하도록 개선.

## Decisions
- 번역 엔진은 성능과 비용을 고려하여 Gemini 1.5 Flash 모델을 사용하며, 기술 용어 보존을 위해 전문 번역 프롬프트를 적용함.
- 터미널 UI는 원문을 유지하고 웹 대시보드에서만 선택된 언어로 실시간 변환하여 보여줌으로써 개발 맥락의 무결성을 유지함.

## Problems / Blockers
- 대규모 텍스트 번역 시 LLM 호출 지연이 발생할 수 있음. 향후 자주 사용되는 문구에 대한 번역 캐시(Translation Cache) 기능 도입 필요.

## Notes for Next Session
- 시스템의 '물리적 최적화'를 위해, 대규모 프로젝트에서 특정 파일 수정 시 영향을 받는 범위를 시각적으로 강조하고 리스크를 예측하는 'Visual Impact Highlighter' 기능을 고도화해야 함.
