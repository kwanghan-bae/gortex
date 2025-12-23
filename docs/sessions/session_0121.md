# Session 0121: Proactive Dependency Visualization & Impact Mapping

## 📅 Date
2025-12-23

## 🎯 Goal
- **Proactive Dependency Visualization & Impact Mapping**: 코드 수정의 파급 효과를 사전에 시각화하고 위험도를 분석하는 '영향력 지도 엔진' 및 대시보드 위젯 구축.

## 📝 Activities
### 1. Reverse Dependency Tracking
- `utils/indexer.py`: `find_reverse_dependencies` 구현.
- AST 분석을 통해 특정 심볼(함수/클래스)을 호출하거나 참조(상속, 임포트)하는 모든 위치를 파일명과 라인 번호 단위로 역추적.

### 2. Impact Diagram Generation
- `agents/analyst/base.py`: `generate_impact_map` 구현.
- 인덱싱된 데이터를 기반으로 Mermaid 다이어그램(`graph RL`)을 생성하여 변경 대상과 호출자 간의 관계를 도식화.

### 3. Dashboard Visualization
- `ui/dashboard.py`: '🌐 IMPACT MAP' 전용 패널 신설.
- 의존성 수에 따른 실시간 위험 등급(Critical/Moderate/Safe) 산출 및 상위 호출자 목록 렌더링 연동.

### 4. Verification
- `tests/test_dependency_viz.py`: `count_tokens` 등 실제 프로젝트 핵심 심볼의 역방향 의존성 추적 및 Mermaid 문법 정합성, UI 색상 적용 테스트 패스.

## 📈 Outcomes
- **Safe Refactoring**: 핵심 로직 수정 전 영향 범위를 즉각 시각화함으로써 사이드 이펙트 발생 가능성을 획기적으로 낮춤.
- **Improved Observability**: 시스템의 의존성 구조를 실시간으로 파악하여 아키텍처 건전성 유지에 기여.

## ⏭️ Next Steps
- **Session 0122**: Automated Regression Test Generation & Validation.
- 영향력 분석 결과, 위험도가 높은 지역에 대해 누락된 테스트 케이스를 시스템이 스스로 식별하고 자동 생성하여 검증하는 '자율 회귀 방어' 지능 구현.
