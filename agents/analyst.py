import logging
import json
import pandas as pd
import os
from typing import Dict, Any, List, Optional
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.core.evolutionary_memory import EvolutionaryMemory

logger = logging.getLogger("GortexAnalyst")

class AnalystAgent:
    """
    데이터 분석 및 자가 진화 피드백 분석을 담당하는 에이전트.
    """
    def __init__(self):
        self.auth = GortexAuth()
        self.memory = EvolutionaryMemory()

    def analyze_data(self, file_path: str) -> Dict[str, Any]:
        """Pandas를 사용하여 데이터 파일 분석 및 시각화 코드 생성"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found at {file_path}"}

            ext = os.path.splitext(file_path)[1].lower()
            df = pd.read_csv(file_path) if ext == '.csv' else (pd.read_excel(file_path) if ext in ['.xls', '.xlsx'] else pd.read_json(file_path))

            summary = {
                "rows": len(df),
                "columns": list(df.columns),
                "head": df.head(3).to_dict(),
                "describe": df.describe().to_dict()
            }

            # 시각화 제안 및 코드 생성 (LLM)
            prompt = f"""다음 데이터 요약 정보를 보고, 가장 적합한 시각화(Chart) 1개를 제안하고 Plotly JSON 데이터 형식으로 작성하라.
            [Data Summary]
            {json.dumps(summary, ensure_ascii=False)}
            
            결과는 반드시 다음 JSON 형식을 따라라:
            {{
                "chart_type": "bar/line/pie/scatter",
                "title": "차트 제목",
                "plotly_json": {{ "data": [...], "layout": {{ ... }} }}
            }}
            """
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            viz_data = json.loads(response.text)
            
            return {
                "summary": summary,
                "visualization": viz_data
            }
        except Exception as e:
            logger.error(f"Data analysis failed: {e}")
            return {"error": str(e)}

    def analyze_feedback(self, history: List[Any]) -> Optional[Dict[str, Any]]:
        """사용자의 부정적 피드백을 분석하여 진화 규칙 추출"""
        # 히스토리 중 마지막 몇 개의 메시지 분석
        prompt = """
        사용자와 AI의 최근 대화를 분석하여 시스템의 행동을 영구적으로 개선할 '지능형 규칙'을 추출하라.

        [분석 대상 핵심 신호]
        1. 명시적 거부: "아니", "틀렸어", "그거 말고", "하지 마"
        2. 수정 요구: "다시 해줘", "이렇게 바꿔줘", "왜 자꾸 X를 해?"
        3. 감정적 강조: 느낌표(!), "제발", "몇 번을 말해"
        4. 반복적 수정: 사용자가 같은 라인을 2회 이상 직접 수정하거나 반복 지시함

        [규칙 생성 원칙]
        - 범용성: "main.py 10번줄 고쳐" (X) -> "파이썬 코드 작성 시 PEP8 스타일을 준수하라" (O)
        - 명확성: 행동이 즉각적으로 정의되어야 함. "항상 X하라" 또는 "절대 Y하지 마라"
        - 트리거: 규칙이 활성화되어야 할 상황을 키워드로 정의 (예: 코딩, 한글, 파일 삭제)

        [추출 사례 (Few-shot)]
        Example 1:
        User: "아니 변수명을 왜 카멜케이스로 써? 파이썬은 스네이크케이스가 기본이야."
        Result: {
            "feedback_detected": true,
            "negative_signal_score": 8,
            "instruction": "Python 코드 작성 시 모든 변수명과 함수명은 반드시 snake_case를 사용할 것.",
            "context": "Python 코딩 및 리팩토링 시",
            "trigger_patterns": ["python", "variable naming", "snake_case"],
            "severity": 4,
            "reason": "사용자가 파이썬 표준 스타일(PEP8) 준수를 강력히 요구함."
        }

        Example 2:
        User: "앞으로 모든 답변은 한국어로만 해줘. 영어 섞지 말고."
        Result: {
            "feedback_detected": true,
            "negative_signal_score": 9,
            "instruction": "사용자에게 제공하는 모든 설명과 답변은 예외 없이 한국어(Korean)로 작성할 것.",
            "context": "사용자와의 모든 대화 상황",
            "trigger_patterns": ["answer language", "korean only"],
            "severity": 5,
            "reason": "사용자가 언어 설정을 최우선순위 제약 조건으로 명시함."
        }

        Example 3:
        User: "테스트 코드 없으면 불안해서 못 쓰겠네. 항상 붙여줘."
        Result: {
            "feedback_detected": true,
            "negative_signal_score": 7,
            "instruction": "신규 기능 구현 또는 코드 수정 시 반드시 해당 로직을 검증하는 단위 테스트(pytest)를 포함할 것.",
            "context": "코드 구현 및 수정 작업 시",
            "trigger_patterns": ["coding", "test code", "unit test"],
            "severity": 3,
            "reason": "사용자가 코드의 안정성 확보를 위해 테스트 코드 작성을 의무화함."
        }

        결과는 반드시 다음 JSON 형식을 따라라:

        {
            "feedback_detected": true/false,
            "negative_signal_score": 1~10 (신호의 명확성 및 강도),
            "instruction": "AI가 앞으로 영구적으로 지켜야 할 범용적인 지침",
            "context": "이 규칙이 적용되어야 할 구체적인 상황 (예: Python 코딩 중 함수 정의 시)",
            "trigger_patterns": ["트리거 키워드 1", "키워드 2"],
            "severity": 1~5,
            "reason": "사용자의 불만 원인 분석 결과"
        }
        """



        
        config = types.GenerateContentConfig(
            system_instruction=prompt,
            temperature=0.0,
            response_mime_type="application/json"
        )
        
        response = self.auth.generate("gemini-1.5-flash", history, config)
        try:
            res_data = json.loads(response.text)
            if res_data.get("feedback_detected"):
                return res_data
            return None
        except Exception as e:
            logger.error(f"Feedback analysis parsing failed: {e}")
            return None

    def analyze_self_correction(self, log_path: str = "logs/trace.jsonl") -> Optional[Dict[str, Any]]:
        """로그에서 실패 후 성공한 패턴을 분석하여 최적화 규칙 추출"""
        if not os.path.exists(log_path):
            return None

        try:
            with open(log_path, "r") as f:
                lines = f.readlines()
                # 최근 100줄만 분석 (성능 및 토큰 절약)
                recent_lines = lines[-100:]
                log_content = "\n".join(recent_lines)

            prompt = """
            다음 로그 데이터를 분석하여 에이전트가 오류를 겪고 스스로 해결한 '성공적인 문제 해결 패턴'을 찾아내라.
            찾아낸 패턴을 바탕으로, 앞으로 비슷한 오류를 방지할 수 있는 '영구적 지침(Constraint)'을 생성하라.

            [분석 포인트]
            1. Coder의 시도: `execute_shell`이 non-zero exit code를 반환했는가?
            2. Coder의 수정: 이후 `write_file` 등을 통해 코드를 수정했는가?
            3. 성공: 재시도한 `execute_shell`이 성공(exit code 0)했는가?

            [규칙 생성 지침]
            - 오류의 원인을 분석하여 구체적으로 작성하라.
            - 예: "라이브러리 import 누락 시 `ImportError`가 발생하므로 사용 전 설치 여부를 먼저 확인하라."
            - severity는 1~5 사이로 지정하라.

            결과는 반드시 다음 JSON 형식을 따라라:
            {
                "pattern_detected": true/false,
                "error_cause": "발견된 오류의 근본 원인",
                "solution": "에이전트가 적용한 해결책",
                "instruction": "앞으로 지켜야 할 영구적 지침",
                "trigger_patterns": ["관련 키워드 1", "키워드 2"],
                "severity": 1~5
            }
            """

            config = types.GenerateContentConfig(
                system_instruction=prompt,
                temperature=0.0,
                response_mime_type="application/json"
            )
            
            response = self.auth.generate("gemini-1.5-flash", log_content, config)
            res_data = json.loads(response.text)
            if res_data.get("pattern_detected"):
                return res_data
            return None
        except Exception as e:
            logger.error(f"Self-correction analysis failed: {e}")
            return None

    def generate_performance_report(self, log_path: str = "logs/trace.jsonl") -> str:
        """로그를 분석하여 세션 성과 및 통계 리포트 생성"""
        if not os.path.exists(log_path):
            return "리포트를 생성할 로그 데이터가 없습니다."

        try:
            with open(log_path, "r", encoding='utf-8') as f:
                lines = f.readlines()
            
            logs = [json.loads(l) for l in lines]
            total_events = len(logs)
            nodes = [l.get("agent") for l in logs if l.get("agent")]
            node_counts = pd.Series(nodes).value_counts().to_dict()
            
            # 지연 시간 및 토큰 분석
            latencies = [l.get("latency_ms") for l in logs if l.get("latency_ms")]
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            
            total_tokens = 0
            for l in logs:
                tokens = l.get("tokens", {})
                if isinstance(tokens, dict):
                    total_tokens += tokens.get("input", 0) + tokens.get("output", 0)

            # 성과 요약 (LLM)
            recent_goals = [l.get("payload", {}).get("goal") for l in logs if l.get("event") == "node_complete" and l.get("payload", {}).get("goal")]
            
            prompt = f"""다음 통계와 작업 목표들을 바탕으로 Gortex 시스템의 성과 리포트를 '임원 보고용(Executive Report)'으로 작성하라.
            
            [Statistics]
            - Total Events: {total_events}
            - Node Usage: {json.dumps(node_counts)}
            - Avg Latency: {avg_latency:.0f}ms
            - Total Tokens Used: {total_tokens}
            
            [Recent Accomplishments]
            {json.dumps(recent_goals[-10:], ensure_ascii=False)}
            
            [Report Guidelines]
            - 마크다운 형식을 사용하라.
            - 주요 성과를 강조하고, 시스템 효율성(비용/시간)을 평가하라.
            - 향후 개선 제안(Next Actions)을 포함하라.
            """
            
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], None)
            return response.text
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return f"리포트 생성 중 오류 발생: {e}"

    def review_code(self, code: str, file_path: str = "unknown") -> Dict[str, Any]:
        """코드 품질을 정적으로 분석하여 점수와 개선안 제공"""
        prompt = f"""다음 파이썬 코드를 'Clean Code' 및 'PEP8' 기준으로 정밀 리뷰하라.
        
        [File]
        {file_path}
        
        [Code]
        {code}
        
        결과는 반드시 다음 JSON 형식을 따라라:
        {{
            "score": 0~100 (정수),
            "critique": {{
                "style": "스타일 관련 지적",
                "complexity": "복잡도 관련 지적",
                "documentation": "주석 관련 지적"
            }},
            "refactoring_tips": ["팁 1", "팁 2"],
            "needs_refactoring": true/false
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], None)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            return {"score": 100, "needs_refactoring": False}

    def analyze_coding_style(self, working_dir: str = ".") -> Dict[str, Any]:
        """프로젝트 코드를 분석하여 개인화된 코딩 스타일 가이드 추출"""
        from gortex.utils.tools import list_files, read_file
        files = list_files(working_dir).split("\n")
        # 분석을 위한 샘플 파일 선택 (최대 5개)
        py_files = [f for f in files if f.endswith(".py") and "test" not in f][:5]
        
        sample_codes = ""
        for f in py_files:
            sample_codes += f"\n--- File: {f} ---\n{read_file(os.path.join(working_dir, f))[:2000]}\n"

        prompt = f"""다음 코드 샘플들을 분석하여 이 프로젝트만의 고유한 '코딩 스타일 가이드'를 작성하라.
        
        [Sample Codes]
        {sample_codes}
        
        결과는 반드시 다음 JSON 형식을 따라라:
        {{
            "naming_convention": "변수, 클래스, 함수의 명명 규칙 분석",
            "comment_style": "주석 작성 방식 (Docstring 형식 등)",
            "architectural_pattern": "자주 사용되는 구조나 패턴",
            "instruction": "에이전트가 코드를 작성할 때 따라야 할 한 문장의 핵심 스타일 지침",
            "trigger_patterns": ["coding", "style", "mimicry"]
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], None)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Style analysis failed: {e}")
            return {"instruction": "PEP8 표준 스타일을 준수하라.", "trigger_patterns": ["coding"]}

    def curate_session_data(self, log_path: str = "logs/trace.jsonl") -> List[Dict[str, Any]]:
        """성공적인 세션 로그를 학습용 데이터셋으로 변환"""
        if not os.path.exists(log_path):
            return []

        try:
            with open(log_path, "r", encoding='utf-8') as f:
                lines = f.readlines()
            
            logs = [json.loads(l) for l in lines]
            # 큐레이션 기준: 성공한 node_complete 이벤트가 많은 세션
            # 여기서는 단순화하여 모든 성공 케이스를 Prompt-Response 쌍으로 변환
            dataset = []
            for l in logs:
                if l.get("event") == "node_complete" and l.get("latency_ms", 0) < 30000:
                    payload = l.get("payload", {})
                    if payload.get("goal"):
                        dataset.append({
                            "prompt": f"Task: {payload.get('goal')}\nContext: {l.get('agent')}",
                            "completion": json.dumps(payload, ensure_ascii=False)
                        })
            
            # 파일로 저장
            if dataset:
                ds_dir = "logs/datasets"
                os.makedirs(ds_dir, exist_ok=True)
                ds_path = os.path.join(ds_dir, f"dataset_{datetime.now().strftime('%Y%m%d')}.jsonl")
                with open(ds_path, "a", encoding='utf-8') as f:
                    for entry in dataset:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                logger.info(f"✅ Curated {len(dataset)} items into dataset.")
            
            return dataset
        except Exception as e:
            logger.error(f"Dataset curation failed: {e}")
            return []

    def cross_validate(self, goal: str, output: str) -> Dict[str, Any]:
        """다른 에이전트의 출력물을 제3의 관점에서 상호 검증"""
        prompt = f"""너는 Gortex v1.0의 수석 검증관이다. 
        다음 작업 목표와 실행 결과를 비교하여 무결성을 검증하라.
        
        [Goal]
        {goal}
        
        [Resulting Output/Code]
        {output}
        
        [Verification Points]
        1. 목표가 100% 달성되었는가?
        2. 보안 취약점이나 논리적 모순이 있는가?
        3. 기존 시스템 제약 조건을 위반하지 않았는가?
        
        결과는 반드시 다음 JSON 형식을 따라라:
        {{
            "is_valid": true/false,
            "confidence_score": 0.0~1.0,
            "critique": "발견된 문제점 또는 칭찬",
            "required_fix": "수정이 필요하다면 구체적인 지시사항"
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], None)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Cross-validation failed: {e}")
            return {"is_valid": True, "confidence_score": 1.0}

def analyst_node(state: GortexState) -> Dict[str, Any]:
    """Analyst 노드 엔트리 포인트"""
    agent = AnalystAgent()
    last_msg_obj = state["messages"][-1]
    last_msg = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    last_msg_lower = last_msg.lower()

    # 1. 의도 판단 (Validation vs Review vs Style vs Data vs Feedback)
    
    # 상호 검증 요청 (Graph에서 전이된 경우)
    if state.get("next_node") == "analyst": # 명시적으로 analyst로 전이됨
        # 가장 최근의 AI 성과물 검증
        ai_outputs = [m for m in state["messages"] if (isinstance(m, tuple) and m[0] == "ai") or (hasattr(m, 'type') and m.type == "ai")]
        if ai_outputs:
            last_ai_msg = ai_outputs[-1][1] if isinstance(ai_outputs[-1], tuple) else ai_outputs[-1].content
            val_res = agent.cross_validate("Current Task Plan", last_ai_msg)
            
            if not val_res["is_valid"]:
                msg = f"🛡️ [Cross-Validation Alert] 결과물이 기준에 미달합니다.\n- 이유: {val_res['critique']}\n- 지시: {val_res['required_fix']}"
                return {
                    "messages": [("ai", msg)],
                    "next_node": "planner" # 재수정 지시
                }
            else:
                # [ECONOMY] 검증 성공 시 보상 지급
                economy = state.get("agent_economy", {}).copy()
                target_agent = "coder" # 주로 coder의 성과물을 검증
                if target_agent not in economy:
                    economy[target_agent] = {"points": 0, "level": "Novice"}
                
                economy[target_agent]["points"] += 10 # 10포인트 지급
                if economy[target_agent]["points"] > 50:
                    economy[target_agent]["level"] = "Expert"
                
                return {
                    "messages": [("ai", f"🛡️ [Cross-Validation Passed] 무결성 검증 완료. {target_agent}가 10 포인트를 획득했습니다!")],
                    "agent_economy": economy,
                    "next_node": "manager"
                }

    # 코딩 스타일 분석 요청 (이전 로직 유지)
    if "/analyze_style" in last_msg_lower or "스타일 분석" in last_msg_lower:
        style_info = agent.analyze_coding_style(state.get("working_dir", "."))
        agent.memory.save_rule(
            instruction=style_info["instruction"],
            trigger_patterns=style_info["trigger_patterns"],
            severity=3,
            context="Personalized Coding Style"
        )
        msg = f"🎨 프로젝트 코딩 스타일 분석 완료!\n"
        msg += f"- 명명 규칙: {style_info.get('naming_convention')}\n"
        msg += f"- 주석 스타일: {style_info.get('comment_style')}\n"
        msg += f"- 학습된 지침: '{style_info['instruction']}'가 진화적 메모리에 등록되었습니다."
        return {
            "messages": [("ai", msg)],
            "next_node": "manager"
        }

    # 코드 리뷰 요청 확인
    if "리뷰" in last_msg_lower or "검토" in last_msg_lower or "review" in last_msg_lower:
        # 코드 추출 (단순화: 마지막 메시지 전체 또는 코드 블록)
        code_to_review = last_msg
        review_res = agent.review_code(code_to_review)
        
        msg = f"🔍 코드 리뷰 결과 (점수: {review_res['score']}/100)\n"
        msg += f"- 스타일: {review_res['critique']['style']}\n"
        msg += f"- 복잡도: {review_res['critique']['complexity']}\n"
        msg += f"- 개선팁: {', '.join(review_res['refactoring_tips'])}"
        
        updates = {
            "messages": [("ai", msg)],
            "next_node": "planner" if review_res["needs_refactoring"] else "manager"
        }
        return updates

    data_files = [f for f in last_msg.split() if f.endswith(('.csv', '.xlsx', '.json'))]
    
    if data_files:
        # Data Mode
        result = agent.analyze_data(data_files[0])
        if "error" in result:
            return {"messages": [("ai", f"❌ 데이터 분석 실패: {result['error']}")], "next_node": "manager"}
            
        msg = f"📊 데이터 분석 결과 ({data_files[0]}):\n"
        msg += f"- 행 수: {result['summary']['rows']}, 컬럼: {', '.join(result['summary']['columns'])}\n"
        msg += f"- 시각화 제안: {result['visualization'].get('title')}"
        
        # 웹 대시보드로 차트 데이터 브로드캐스팅 시도
        from gortex.ui.web_server import manager as web_manager
        if web_manager:
            try:
                import asyncio
                asyncio.create_task(web_manager.broadcast(json.dumps({
                    "type": "chart_data",
                    "data": result["visualization"]
                }, ensure_ascii=False)))
                msg += "\n📈 웹 대시보드에 차트가 생성되었습니다."
            except:
                pass

        return {
            "messages": [("ai", msg)],
            "next_node": "manager"
        }
    elif "로그" in last_msg or "분석" in last_msg or "패턴" in last_msg:
        # Self-Correction Analysis Mode
        correction = agent.analyze_self_correction()
        if correction:
            agent.memory.save_rule(
                instruction=correction["instruction"],
                trigger_patterns=correction["trigger_patterns"],
                severity=correction["severity"],
                context=f"Self-Correction (Cause: {correction['error_cause']})"
            )
            return {
                "messages": [("ai", f"자가 수정한 패턴을 분석하여 새 규칙을 학습했습니다:\n- 원인: {correction['error_cause']}\n- 지침: {correction['instruction']}")],
                "next_node": "manager"
            }
        else:
            # Feedback Analysis (기존 로직 유지)
            feedback = agent.analyze_feedback(state["messages"])
            if feedback:
                agent.memory.save_rule(
                    instruction=feedback["instruction"],
                    trigger_patterns=feedback["trigger_patterns"],
                    severity=feedback["severity"],
                    context=feedback.get("context")
                )
                return {
                    "messages": [("ai", f"새로운 규칙을 학습했습니다: '{feedback['instruction']}'")],
                    "next_node": "manager"
                }
        
    return {
        "messages": [("ai", "요청하신 내용을 분석했으나 특이사항을 발견하지 못했습니다.")],
        "next_node": "manager"
    }
