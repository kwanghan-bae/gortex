# 🗺️ GORTEX DEVELOPMENT ROADMAP (v3.4+)

## 📊 현재 개발 현황 (Current Status)

| 기능 분류 | 세부 기능 | 상태 | 비고 |
| :--- | :--- | :---: | :--- |
| **Core** | tyepr 기반 CLI 아키텍처 | ✅ | v3.0 |
| **Stability** | 비동기 노드 래퍼 및 Blocking 방지 | ✅ | v3.1 |
| **LLM** | Gemini / Ollama / LM Studio 하이브리드 | ✅ | v3.2 |
| **Memory** | 주제별 샤딩 및 Super Rule 통합 | ✅ | v3.3 |
| **Intelligence** | Swarm 기반 자율 장애 복구 루프 | ✅ | v3.4 |
| **Economy** | Dynamic Skill Tree & Matrix UI | ✅ | v3.4 |
| **Persistence** | 실시간 복제 지원 Distributed Saver | ✅ | v3.0 |

---

## 🎯 주요 과제 (Critical Gaps)

### 🔴 High Priority (지능 고도화)
- [ ] **Multi-modal Interaction**: 이미지 분석(스크린샷 기반 디버깅) 및 음성 명령 처리 강화.
- [ ] **Distributed Swarm**: 서로 다른 머신에 있는 에이전트 간의 통신 및 협업 (Redis MQ 기반).
- [ ] **Proactive Optimization**: 에러가 발생하기 전, 정적 분석을 통해 잠재적 결함을 선제적으로 수정하는 'Pre-emptive Healing'.

### 🟡 Medium Priority (플랫폼 확장)
- [ ] **Web Dashboard**: Rich UI를 넘어서는 실시간 그래프 기반 웹 관제소 구축.
- [ ] **Plugin Marketplace**: 외부 개발자가 새로운 에이전트와 도구를 등록하고 공유할 수 있는 시스템.
- [ ] **Autonomous Training**: 작업 이력을 바탕으로 에이전트 전용 소형 모델(SLM)을 스스로 미세 조정(Fine-tuning).

### 🟢 Low Priority (사용자 경험)
- [ ] **Natural Language Config**: 시스템 설정을 자연어로 명령하여 변경 (예: "/config 이제부터 모든 코드는 구글 스타일로 짜줘").
- [ ] **Multi-language Support**: 완전한 다국어 지원 (현재 한국어/영어 중심).

---

## 🏛️ Legacy Milestone: Clover Wallet Integration
*(이전 Clover Wallet 앱 개발 이력)*
- ✅ 하단 네비게이션 및 기본 구조 (v1.0)
- ✅ 랜덤 번호 생성 및 당첨 확인 API 연동
- ✅ OCR 영수증 스캔 및 명당 데이터 조회 API
- ✅ 여행 플랜 목록 조회 및 뱃지 시스템 구축

---

## 📅 업데이트 기록
*   **2025-12-26**: v3.4.2 업데이트 반영 (자율 복구 루프 및 기술 트리 완료).
*   **2025-12-23**: v3.0 마이그레이션 및 하이브리드 LLM 아키텍처 도입.