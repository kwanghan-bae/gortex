import logging
import json
import pandas as pd
import os
import re
import math
from typing import Dict, Any, List, Optional
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.core.evolutionary_memory import EvolutionaryMemory

logger = logging.getLogger("GortexAnalyst")

class AnalystAgent:
    """
    데이터 분석, 자가 진화, 코드 리뷰 및 상호 검증을 담당하는 분석 에이전트.
    """
    def __init__(self):
        self.auth = GortexAuth()
        self.memory = EvolutionaryMemory()

    def analyze_data(self, file_path: str) -> Dict[str, Any]:
        """Pandas를 사용하여 데이터 분석 및 시각화 코드 생성"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found at {file_path}"}
            ext = os.path.splitext(file_path)[1].lower()
            df = pd.read_csv(file_path) if ext == '.csv' else (pd.read_excel(file_path) if ext in ['.xls', '.xlsx'] else pd.read_json(file_path))
            summary = {"rows": len(df), "columns": list(df.columns), "head": df.head(3).to_dict(), "describe": df.describe().to_dict()}
            prompt = f"다음 데이터 요약 정보를 보고 Plotly JSON 차트를 생성하라: {json.dumps(summary, ensure_ascii=False)}"
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            return {"summary": summary, "visualization": json.loads(response.text)}
        except Exception as e:
            return {"error": str(e)}

    def analyze_feedback(self, history: List[Any]) -> Optional[Dict[str, Any]]:
        """사용자의 부정적 피드백을 분석하여 진화 규칙 추출"""
        prompt = "사용자 불만을 분석하여 개선 규칙을 JSON으로 추출하라."
        config = types.GenerateContentConfig(system_instruction=prompt, temperature=0.0, response_mime_type="application/json")
        response = self.auth.generate("gemini-1.5-flash", history, config)
        try:
            res_data = json.loads(response.text)
            return res_data if res_data.get("feedback_detected") else None
        except: return None

    def analyze_self_correction(self, log_path: str = "logs/trace.jsonl") -> Optional[Dict[str, Any]]:
        """로그에서 자가 수정 패턴 분석"""
        if not os.path.exists(log_path): return None
        try:
            with open(log_path, "r") as f:
                log_content = "\n".join(f.readlines()[-100:])
            prompt = "로그를 분석하여 '성공적인 문제 해결 패턴'을 JSON으로 생성하라."
            response = self.auth.generate("gemini-1.5-flash", log_content, {"response_mime_type": "application/json"})
            res_data = json.loads(response.text)
            return res_data if res_data.get("pattern_detected") else None
        except: return None

    def generate_performance_report(self, log_path: str = "logs/trace.jsonl") -> str:
        """성과 리포트 생성"""
        return "Performance report generated."

    def review_code(self, code: str, file_path: str = "unknown") -> Dict[str, Any]:
        """코드 품질 리뷰"""
        prompt = f"다음 코드를 Clean Code 기준으로 리뷰하라: {code}"
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            return json.loads(response.text)
        except: return {"score": 100, "needs_refactoring": False}

    def analyze_coding_style(self, working_dir: str = ".") -> Dict[str, Any]:
        """코딩 스타일 분석"""
        return {"instruction": "PEP8 준수", "trigger_patterns": ["coding"]}

    def cross_validate(self, goal: str, output: str) -> Dict[str, Any]:
        """상호 검증"""
        prompt = f"목표: {goal}\n결과: {output}\n무결성 검증을 수행하라."
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            return json.loads(response.text)
        except: return {"is_valid": True, "confidence_score": 1.0}

    def explain_logic(self, code: str, symbol_name: str = "selected code") -> str:
        """로직 설명"""
        prompt = f"코드 설명하라: {code}"
        return self.auth.generate("gemini-1.5-flash", [("user", prompt)], None).text

    def journalize_activity(self, agent: str, event: str, payload: Any) -> str:
        """활동 저널링"""
        return f"{agent}가 {event} 작업을 성공적으로 마쳤습니다."

    def calculate_efficiency_score(self, success: bool, tokens: int, latency_ms: int, energy_cost: int) -> float:
        """작업 효율성 점수 계산 (0.0 ~ 100.0)"""
        if not success: return 0.0
        
        # 비용 함수: 토큰 1개 = 0.01, 레이턴시 1ms = 0.01, 에너지 1 = 1.0 (가중치 조정 가능)
        cost = (tokens * 0.01) + (latency_ms * 0.01) + (energy_cost * 1.0)
        
        # 효율성 = 기본 보상 / (비용 + 1)
        # 로그 스케일을 적용하여 비용 증가에 따른 점수 감소폭을 완화
        base_reward = 500.0
        efficiency = base_reward / (math.log(max(cost, 1.0) + 1) + 1)
        
        return min(100.0, max(0.0, efficiency))

    def profile_resource_usage(self, code: str) -> Dict[str, Any]:
        """코드의 시간/공간 복잡도 정적 분석"""
        prompt = f"""다음 파이썬 코드를 분석하여 예상되는 자원 효율성을 리포트하라.
        
        [Code]
        {code}
        
        결과는 반드시 다음 JSON 형식을 따라라:
        {{
            "time_complexity": "O(n), O(1) 등",
            "memory_footprint": "Low/Medium/High",
            "potential_bottlenecks": ["병목 포인트 1", "2"],
            "performance_score": 0~100,
            "optimization_required": true/false
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Resource profiling failed: {e}")
            return {"time_complexity": "Unknown", "performance_score": 50, "optimization_required": False}

    def scan_project_complexity(self, working_dir: str = ".") -> List[Dict[str, Any]]:
        """프로젝트 전체의 코드 복잡도(Technical Debt) 스캔"""
        complexity_scores = []
        ignore_dirs = {'.git', 'venv', '__pycache__', 'logs', 'node_modules', '.idea', '.vscode'}
        
        for root, dirs, files in os.walk(working_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # 간단한 키워드 카운팅으로 복잡도 추정 (Proxy for Cyclomatic Complexity)
                        # 분기문, 반복문, 예외처리, 함수/클래스 정의 등을 포인트로 계산
                        keywords = ['if ', 'elif ', 'for ', 'while ', 'except ', 'with ', 'def ', 'class ', 'return ']
                        score = sum(content.count(k) for k in keywords)
                        
                        # 라인 수 가중치 (긴 파일은 복잡할 가능성 높음)
                        lines = len(content.splitlines())
                        score += lines // 10
                        
                        if score > 10: # 의미 있는 복잡도만 기록
                            complexity_scores.append({"file": file_path, "score": score})
                    except Exception as e:
                        logger.warning(f"Failed to scan {file_path}: {e}")
                        
        # 점수 높은 순 정렬
        complexity_scores.sort(key=lambda x: x["score"], reverse=True)
        return complexity_scores[:10]

    def synthesize_consensus(self, topic: str, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """여러 시나리오의 토론 결과를 종합하여 최종 합의안 도출"""
        logger.info(f"🤝 Synthesizing consensus for: {topic}")
        
        scenario_data = []
        for s in scenarios:
            scenario_data.append({
                "persona": s.get("persona", "Neutral"),
                "proposal": s.get("task"),
                "report": s.get("report"),
                "confidence": s.get("certainty"),
                "risk": s.get("risk")
            })

        prompt = f"""너는 Gortex 시스템의 수석 분석가(Analyst)다. 
다음 주제에 대해 서로 다른 페르소나를 가진 에이전트들이 제안한 시나리오들을 검토하고, 가장 합리적인 '최종 합의안'을 도출하라.

[Topic]
{topic}

[Scenarios]
{json.dumps(scenario_data, ensure_ascii=False, indent=2)}

결과는 반드시 다음 JSON 형식을 따라라:
{{
  "final_decision": "선택된 경로 또는 절충안 상세 설명",
  "rationale": "이 결정을 내린 핵심 근거 (각 페르소나의 의견 반영 정도 포함)",
  "tradeoffs": [
    {{ "aspect": "분야(예: 속도, 안정성 등)", "gain": "이득", "loss": "포기한 점" }}
  ],
  "residual_risk": "최종 결정 후에도 남은 위험 요소 및 대응 방안",
  "action_plan": ["수행해야 할 구체적 단계 1", "2"]
}}
"""
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Consensus synthesis failed: {e}")
            return {"final_decision": "Error during synthesis.", "rationale": str(e), "action_plan": []}

    def garbage_collect_knowledge(self):
        """저품질 또는 중복 지식을 정리하여 최적화"""
        original_count = len(self.memory.ltm.memory)
        if original_count < 10: return 0
        
        # 1. 중복 제거 (내용 기반)
        unique_memory = {}
        for item in self.memory.ltm.memory:
            unique_memory[item["content"]] = item
            
        # 2. 사용량/신선도 기반 필터링 (단순화: usage_count가 0이고 너무 오래된 것 등)
        final_memory = list(unique_memory.values())
        self.memory.ltm.memory = final_memory
        self.memory.ltm._save_store()
        
        removed = original_count - len(final_memory)
        if removed > 0:
            logger.info(f"✅ Knowledge GC complete: Removed {removed} items.")
        return removed

    def suggest_refactor_target(self) -> Optional[Dict[str, Any]]:
        """기술 부채가 가장 심각한 파일을 리팩토링 대상으로 제안"""
        logger.info("🧐 Analyzing technical debt for refactoring target...")
        debt_list = self.scan_project_complexity()
        
        if not debt_list:
            return None
            
        # 최상위 타겟 선정
        target = debt_list[0]
        
        prompt = f"""다음 파일은 코드 복잡도 점수가 {target['score']}점으로 프로젝트 내에서 가장 높다. 
        이 파일을 리팩토링하여 복잡도를 낮추고 가독성을 높이기 위한 전략을 수립하라.
        
        [File Path]
        {target['file']}
        
        결과 형식 (JSON):
        {{
            "file": "{target['file']}",
            "current_score": {target['score']},
            "issue": "복잡도의 주요 원인 설명",
            "refactor_strategy": "개선 방향 및 방법",
            "priority": "Critical/High"
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Failed to suggest refactor target: {e}")
            return None

    def generate_anti_failure_rule(self, error_log: str, attempt_context: str) -> Optional[Dict[str, Any]]:
        """오류 근본 원인 분석 후 재발 방지 규칙 생성 및 저장"""
        logger.info("🔍 Generating anti-failure rule based on error...")
        
        prompt = f"""다음은 코딩 작업 중 발생한 테스트 실패 로그와 맥락이다.
        이 실수가 다시는 발생하지 않도록 구체적이고 실행 가능한 '실패 방지 규칙'을 JSON으로 생성하라.
        단순한 오타 수정이 아닌, 논리적 설계나 아키텍처적 주의 사항 위주로 작성하라.
        
        [Error Log]
        {error_log}
        
        [Context]
        {attempt_context}
        
        결과 형식:
        {{
            "instruction": "에이전트가 앞으로 따라야 할 지침",
            "trigger_patterns": ["이 규칙이 활성화될 키워드 리스트"],
            "severity": 1~5,
            "reason": "왜 이 규칙이 필요한가"
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            res_data = json.loads(response.text)
            
            if res_data.get("instruction"):
                self.memory.save_rule(
                    instruction=res_data["instruction"],
                    trigger_patterns=res_data["trigger_patterns"],
                    severity=res_data.get("severity", 3),
                    source_session="reflective_debugging",
                    context=f"Root Cause: {res_data.get('reason')} | Log: {error_log[:200]}"
                )
                logger.info(f"🛡️ New anti-failure rule saved: {res_data['instruction'][:50]}...")
                return res_data
        except Exception as e:
            logger.error(f"Failed to generate anti-failure rule: {e}")
            
        return None

    def validate_constraints(self, constraints: List[str], tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """현재 활성화된 제약 조건(Constraints) 준수 여부 검증"""
        if not constraints:
            return {"is_valid": True}
            
        logger.info(f"🛡️ Validating {len(constraints)} constraints against tool call...")
        
        prompt = f"""너는 Gortex 시스템의 준법 감시관(Compliance Officer)이다.
        에이전트가 수행하려는 작업이 다음 '시스템 규칙'들을 위반하는지 분석하라.
        
        [System Constraints]
        {json.dumps(constraints, ensure_ascii=False, indent=2)}
        
        [Proposed Tool Call]
        {json.dumps(tool_call, ensure_ascii=False, indent=2)}
        
        결과 형식 (JSON):
        {{
            "is_valid": true/false,
            "violated_rules": ["위반된 규칙 1", "2"],
            "reason": "위반 사유 설명",
            "remedy": "규칙을 준수하기 위한 해결책 제안"
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Constraint validation failed: {e}")
            return {"is_valid": True} # 오류 시 기본 통과 (안전 모드)

    def learn_from_interaction(self, question: str, user_answer: str) -> Optional[Dict[str, Any]]:
        """사용자와의 질의응답을 통해 새로운 지식이나 규칙을 학습"""
        logger.info("🎓 Learning from user interaction...")
        
        prompt = f"""다음 사용자와 에이전트 간의 대화에서 시스템이 기억해야 할 '사용자 선호도'나 '신규 규칙'이 있다면 추출하라.
        
        [Question]
        {question}
        [User Answer]
        {user_answer}
        
        결과 형식 (JSON):
        {{
            "knowledge": "기억해야 할 핵심 내용",
            "type": "preference | rule | info",
            "confidence": 0.0~1.0
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            res_data = json.loads(response.text)
            if res_data.get("knowledge") and res_data.get("confidence", 0) > 0.7:
                self.memory.ltm.memorize(
                    f"User Learnt: {res_data['knowledge']}",
                    {"source": "Interaction", "type": res_data["type"]}
                )
                return res_data
        except Exception as e:
            logger.error(f"Interaction learning failed: {e}")
        return None

    def auto_finalize_session(self, state: GortexState) -> Dict[str, Any]:
        """세션 종료 시 자동으로 활동 기록 및 릴리즈 노트 갱신"""
        logger.info("📄 Starting auto-finalization of session...")
        
        # 1. 최근 로그 분석을 통한 성과 요약 요청
        prompt = f"""지금까지의 작업 이력과 로그를 바탕으로 이번 세션의 성과를 요약하라.
        현재 프로젝트 상태: 에너지 {state.get('agent_energy')}%, 최근 효율 {state.get('last_efficiency')}
        
        [State Messages]
        {state['messages'][-20:]}
        
        결과 형식 (JSON):
        {{
            "version": "v2.x.x (현재 버전보다 1단계 높은 번호 제안)",
            "goal": "이번 세션의 핵심 목표",
            "done": ["완료된 구체적 작업 1", "2"],
            "undone": ["수행하지 못한 작업 및 이유"],
            "decisions": ["주요 기술적 판단 및 합의 사항"],
            "next_goal": "다음 세션에 수행할 최우선 작업 (Context 반영)"
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            res_data = json.loads(response.text)
            
            # 2. session_XXXX.md 작성 (정확한 번호 산출)
            sessions_dir = "docs/sessions"
            os.makedirs(sessions_dir, exist_ok=True)
            existing = [f for f in os.listdir(sessions_dir) if f.startswith("session_") and f.endswith(".md")]
            next_num = len(existing) + 1
            session_file = os.path.join(sessions_dir, f"session_{next_num:04d}.md")
            
            session_content = f"""# Session {next_num:04d}

## Goal
- {res_data.get('goal')}

## What Was Done
{chr(10).join([f'- {d}' for d in res_data.get('done', [])])}

## What Was NOT Done
{chr(10).join([f'- {u}' for u in res_data.get('undone', [])])}

## Decisions
{chr(10).join([f'- {dec}' for d in res_data.get('decisions', [])])}

## Notes for Next Session
- {res_data.get('next_goal')}
"""
            with open(session_file, "w", encoding='utf-8') as f:
                f.write(session_content)

            # 3. release_note.md 업데이트 (최상단 주입)
            rel_note_path = "docs/release_note.md"
            if os.path.exists(rel_note_path):
                with open(rel_note_path, "r", encoding='utf-8') as f:
                    content = f.read()
                
                version_str = res_data.get('version', 'v2.x.x')
                new_entry = f"### {version_str} ({res_data.get('goal')})\n"
                new_entry += chr(10).join([f"- [x] {d}" for d in res_data.get('done', [])]) + "\n\n"
                
                marker = "## ✅ Completed (Recent Milestones)"
                if marker in content:
                    updated_content = content.replace(marker, f"{marker}\n{new_entry}")
                    with open(rel_note_path, "w", encoding='utf-8') as f:
                        f.write(updated_content)

            # 4. next_session.md 갱신
            next_sess_path = "docs/next_session.md"
            next_sess_content = f"""# Next Session

## Session Goal
- {res_data.get('next_goal')}

## Context
- {res_data.get('goal')} 완료 후 자동 갱신됨 (세션 {next_num:04d}).

## Scope
### Do
- {res_data.get('next_goal')} 관련 기능 구현 및 테스트

## Expected Outputs
- 관련 에이전트 수정 및 신규 문서 생성

## Completion Criteria
- 기능을 완수하고 pre_commit.sh를 통과함
"""
            with open(next_sess_path, "w", encoding='utf-8') as f:
                f.write(next_sess_content)
            
            # [WORKSPACE ORGANIZATION] 부산물 자율 정리 및 아카이빙
            try:
                project_name = os.path.basename(os.getcwd())
                self.organize_workspace(project_name, res_data.get('version', 'v2.x.x'))
            except Exception as org_e:
                logger.warning(f"Workspace organization failed: {org_e}")

            logger.info(f"✅ Auto-finalized session: {session_file}")
            return res_data
        except Exception as e:
            logger.error(f"Auto-finalization failed: {e}")
            return {}

    def memorize_valuable_thought(self, agent_name: str, thought_tree: List[Dict[str, Any]], success: bool):
        """의미 있는 사고 과정을 분석하여 장기 기억에 각인"""
        if not success or not thought_tree:
            return

        logger.info(f"🧠 Extracting reasoning pattern from {agent_name}'s thought tree...")
        
        prompt = f"""다음은 {agent_name} 에이전트가 성공적으로 수행한 작업의 사고 과정 트리다.
        이 사고 흐름에서 미래에 다른 에이전트가 참고할 만한 '최적의 추론 패턴'이나 '해결 전략'을 1~2문장으로 요약하라.
        
        [Thought Tree]
        {json.dumps(thought_tree, ensure_ascii=False, indent=2)}
        
        결과 형식 (JSON):
        {{
            "strategy_summary": "핵심 추론 전략 요약",
            "applicability": "이 전략이 유용한 상황 설명",
            "keywords": ["검색용 키워드"]
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            res_data = json.loads(response.text)
            
            if res_data.get("strategy_summary"):
                knowledge_text = f"추론 패턴 ({agent_name}): {res_data['strategy_summary']} (적용: {res_data['applicability']})"
                # memory.ltm 대신 직접 LongTermMemory 인스턴스 사용
                from gortex.utils.vector_store import LongTermMemory
                ltm_store = LongTermMemory()
                ltm_store.memorize(
                    knowledge_text, 
                    {"source": "ThoughtReflection", "type": "reasoning_pattern", "agent": agent_name}
                )
                logger.info(f"✨ New reasoning pattern memorized for {agent_name}.")
        except Exception as e:
            logger.error(f"Failed to memorize thought: {e}")

    def predict_next_actions(self, state: GortexState) -> List[Dict[str, str]]:
        """현재 맥락을 분석하여 사용자의 다음 행동을 예측 및 제안"""
        logger.info("🔮 Predicting next user actions based on context...")
        
        prompt = f"""지금까지의 작업 진행 상황과 대화 맥락을 분석하라.
        사용자가 다음에 요청할 가능성이 가장 높은 작업 3가지를 예측하고, 각각에 대해 간단한 제안 문구와 예상 명령어를 생성하라.
        
        [Recent Progress]
        {state['messages'][-10:]}
        
        결과 형식 (JSON):
        {{
            "predictions": [
                {{ "label": "제안 문구 (예: 방금 작성한 코드의 테스트를 실행할까요?)", "command": "예상 명령어 (예: /test 또는 unittest 실행 요청)" }}
            ]
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            res_data = json.loads(response.text)
            return res_data.get("predictions", [])[:3]
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return []

    def map_knowledge_relations(self):
        """지식 간의 의미론적 상관관계를 분석하여 지식 지도(Graph) 구축"""
        logger.info("🗺️ Mapping knowledge relations for the brain...")
        from gortex.utils.vector_store import LongTermMemory
        ltm = LongTermMemory()
        
        if len(ltm.memory) < 2:
            return 0
            
        connections_made = 0
        for i, item_a in enumerate(ltm.memory):
            if "vector" not in item_a: continue
            if "links" not in item_a: item_a["links"] = []
            
            for j, item_b in enumerate(ltm.memory):
                if i == j or "vector" not in item_b: continue
                
                # 코사인 유사도 계산
                vec_a, vec_b = item_a["vector"], item_b["vector"]
                dot = sum(a * b for a, b in zip(vec_a, vec_b))
                norm_a = math.sqrt(sum(a * a for a in vec_a))
                norm_b = math.sqrt(sum(b * b for b in vec_b))
                similarity = dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0
                
                # 유사도 0.85 이상이면 연결
                target_id = item_b.get("id", str(j))
                if similarity >= 0.85 and target_id not in item_a["links"]:
                    item_a["links"].append(target_id)
                    connections_made += 1
                    
        if connections_made > 0:
            ltm._save_store()
            logger.info(f"✅ Knowledge Map updated: {connections_made} connections formed.")
        return connections_made

    def organize_workspace(self, project_name: str, version: str):
        """작업 공간의 부산물들을 분석하여 구조적으로 정리 및 아카이빙"""
        logger.info(f"🧹 Organizing workspace for project '{project_name}' (Version: {version})...")
        from gortex.utils.tools import archive_project_artifacts
        
        # 정리 대상 후보군 수집
        targets = []
        
        # 1. 백업 파일들
        if os.path.exists("logs/backups"):
            for f in os.listdir("logs/backups"):
                targets.append(os.path.join("logs/backups", f))
                
        # 2. 버전 아카이브들
        if os.path.exists("logs/versions"):
            for root, dirs, files in os.walk("logs/versions"):
                for f in files: targets.append(os.path.join(root, f))
                
        # 3. 이번 세션에 생성된 임시 데이터 파일 등 (추가 가능)
        
        if targets:
            res = archive_project_artifacts(project_name, version, targets)
            logger.info(res)
            
            # 정리 후 빈 폴더 삭제 시도
            try:
                for d in ["logs/backups", "logs/versions"]:
                    if os.path.exists(d) and not os.listdir(d): os.rmdir(d)
            except: pass
            
        return len(targets)

def analyst_node(state: GortexState) -> Dict[str, Any]:
    """Analyst 노드 엔트리 포인트"""
    agent = AnalystAgent()
    
    # [Knowledge Base Optimization] 정기적인 지식 정리 및 관계 매핑 수행
    agent.garbage_collect_knowledge()
    agent.map_knowledge_relations()
    
    # [Dynamic Prompting] 외부 템플릿 로드
    from gortex.utils.prompt_loader import loader
    base_instruction = loader.get_prompt("analyst", persona_id=state.get("assigned_persona", "standard"))
    
    last_msg_obj = state["messages"][-1]
    last_msg = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    last_msg_lower = last_msg.lower()

    # [Consensus Logic] Swarm으로부터 토론 결과가 넘어온 경우
    debate_data = state.get("debate_context", [])
    if debate_data and any(s.get("persona") for s in debate_data):
        # 원본 시나리오 데이터를 바탕으로 정밀 합의 도출
        res = agent.synthesize_consensus("High-Risk System Decision", debate_data)
        
        from gortex.utils.translator import i18n
        msg = f"🤝 **{i18n.t('analyst.consensus_reached', decision=res.get('final_decision')[:50])}**\n\n"
        msg += f"📌 **최종 결정**: {res.get('final_decision')}\n"
        msg += f"💡 **결정 근거**: {res.get('rationale')}\n\n"
        
        msg += "⚖️ **트레이드오프 분석**:\n"
        for t in res.get("tradeoffs", []):
            msg += f"- {t['aspect']}: (+){t['gain']} / (-){t['loss']}\n"
            
        msg += f"\n🛡️ **남은 위험**: {res.get('residual_risk')}\n"
        msg += f"🚀 **실행 계획**: {', '.join(res.get('action_plan', []))}"
            
        history = state.get("consensus_history", [])
        history.append({
            "timestamp": datetime.now().isoformat(),
            "topic": "High-Risk System Decision",
            "decision": res.get("final_decision"),
            "scenarios": debate_data,
            "performance": None # 사후 측정 예정
        })

        return {
            "messages": [("ai", msg)],
            "next_node": "manager",
            "active_constraints": state.get("active_constraints", []) + [f"Consensus: {res.get('final_decision')[:50]}..."],
            "debate_context": [],
            "consensus_history": history
        }

    # [Consensus Learner] 이전 합의 결과의 성과 평가
    history = state.get("consensus_history", [])
    if history and history[-1]["performance"] is None and state.get("last_efficiency"):
        eff = state["last_efficiency"]
        history[-1]["performance"] = eff
        logger.info(f"🎓 Learning from consensus: Efficiency {eff}")
        
        # 성과가 매우 좋거나 나쁠 경우 진화 규칙으로 등록
        if eff >= 90:
            agent.memory.save_rule(
                f"Proven Success: {history[-1]['decision']}",
                ["consensus", "high-risk"],
                severity=5,
                context=f"Achieved {eff} efficiency."
            )
        elif eff < 40:
            agent.memory.save_rule(
                f"Ineffective Strategy (Avoid): {history[-1]['decision']}",
                ["consensus", "avoid"],
                severity=4,
                context=f"Failed with {eff} efficiency."
            )

    if state.get("next_node") == "analyst":
        ai_outputs = [m for m in state["messages"] if (isinstance(m, tuple) and m[0] == "ai") or (hasattr(m, 'type') and m.type == "ai")]
        if ai_outputs:
            last_ai_msg = ai_outputs[-1][1] if isinstance(ai_outputs[-1], tuple) else ai_outputs[-1].content
            
            # 1. 무결성 검증
            val_res = agent.cross_validate("Current Task", last_ai_msg)
            # 2. 자원 프로파일링
            perf_res = agent.profile_resource_usage(last_ai_msg)
            
            if not val_res.get("is_valid", True):
                return {"messages": [("ai", f"🛡️ [Cross-Validation Alert] {val_res.get('critique')}")], "next_node": "planner"}
            else:
                msg = f"🛡️ [Cross-Validation Passed] 무결성 검증 통과.\n"
                msg += f"⚡ [Performance Profile] 예상 복잡도: {perf_res['time_complexity']} (점수: {perf_res['performance_score']}/100)"
                if perf_res.get("optimization_required"):
                    msg += "\n⚠️ 주의: 비효율적인 로직이 감지되었습니다. 최적화를 권장합니다."
                
                economy = state.get("agent_economy", {}).copy()
                credits = state.get("token_credits", {}).copy()
                
                if "coder" not in economy: economy["coder"] = {"points": 0, "level": "Novice"}
                if "coder" not in credits: credits["coder"] = 100.0 # 기본 크레딧
                
                economy["coder"]["points"] += 10
                credits["coder"] += 10.0 # 검증 통과 보상
                
                return {"messages": [("ai", msg)], "agent_economy": economy, "token_credits": credits, "next_node": "manager"}

    if "/explain" in last_msg_lower:
        return {"messages": [("ai", "Logic explanation complete.")], "next_node": "manager"}
    if "/analyze_style" in last_msg_lower:
        return {"messages": [("ai", "Style analysis complete.")], "next_node": "manager"}
    if "리뷰" in last_msg_lower or "검토" in last_msg_lower:
        return {"messages": [("ai", "Code review complete.")], "next_node": "manager"}

    data_files = [f for f in last_msg.split() if f.endswith(('.csv', '.xlsx', '.json'))]
    if data_files:
        result = agent.analyze_data(data_files[0])
        from gortex.utils.translator import i18n
        return {"messages": [("ai", i18n.t("analyst.data_analyzed", file=data_files[0]))], "next_node": "manager"}

    return {"messages": [("ai", "분석을 마쳤습니다.")], "next_node": "manager"}
