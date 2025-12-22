# Next Session

## Session Goal
- **Local LLM Fine-Tuning Pipeline**: 구축된 진화 데이터(`evolution.jsonl`)를 기반으로 로컬 모델(Ollama/Llama-3 등)을 미세 조정(Fine-tuning)하기 위한 **전처리 및 설정 자동화 파이프라인**을 구축한다.

## Context
- `logs/datasets/evolution.jsonl`에 양질의 자가 교정 데이터가 쌓이고 있음.
- 이를 실제 모델 학습에 활용하려면 '데이터 검증 -> 포맷 변환(Alpaca/ShareGPT) -> LoRA 설정 -> 학습 잡 패키징'의 과정이 자동화되어야 함.
- 직접적인 GPU 학습은 환경에 따라 불가능할 수 있으므로, **"Ready-to-Train"** 상태로 패키징하는 것이 목표임.

## Scope
### Do
- `agents/evolution_node.py`: `prepare_fine_tuning_job` 메서드 구현.
    - 데이터 유효성 검사 (JSONL 파싱 확인).
    - 학습용 프롬프트 포맷 변환 (System/User/Assistant).
    - `training_jobs/job_{TIMESTAMP}/` 디렉토리 생성 및 데이터 이동.
- `config/training.yaml`: LoRA Rank, Epoch, Learning Rate 등 학습 하이퍼파라미터 템플릿 정의.
- `scripts/prepare_training.sh`: 파이썬 스크립트를 호출하여 가장 최신 데이터를 패키징하는 셸 유틸리티.

### Do NOT
- 실제 GPU 학습(Train Loop)을 이 세션에서 강제로 실행하지 않는다. (리소스 과부하 방지)
- 외부 클라우드(Colab 등) 연동까지 고려하지 않는다. (로컬 우선)

## Expected Outputs
- `agents/evolution_node.py` (Update)
- `config/training.yaml` (New)
- `scripts/prepare_training.sh` (New)
- `training_jobs/` (New Directory Structure)

## Completion Criteria
- `evolution.jsonl` 파일이 존재할 때, `scripts/prepare_training.sh`를 실행하면 `training_jobs/` 하위에 설정 파일(`config.yaml`)과 데이터(`dataset.json`)가 생성되어야 한다.
- `docs/sessions/session_0080.md` 기록.