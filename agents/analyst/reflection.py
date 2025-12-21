import json
import logging
import re
from typing import Dict, Any, List, Optional
from gortex.agents.analyst.base import AnalystAgent

logger = logging.getLogger("GortexAnalystReflection")

class ReflectionAnalyst(AnalystAgent):
    """시스템의 사고 과정을 성찰하고 진화 규칙을 생성하는 전문가"""
    
    def generate_anti_failure_rule(self, error_log: str, context: str) -> Optional[Dict[str, Any]]:
        """실패 사례 분석을 통한 방어 규칙 생성"""
        prompt = f"다음 에러를 분석하여 재발 방지 규칙을 JSON으로 제안하라.\nError: {error_log}\nContext: {context}"
        try:
            response_text = self.backend.generate("gemini-1.5-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Rule generation failed: {e}")
            return None

    def synthesize_consensus(self, topic: str, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """여러 에이전트의 상반된 의견을 조율하여 최종 합의안 도출"""
        prompt = f"주제: {topic}\n토론 데이터: {json.dumps(scenarios)}\n가장 합리적인 최종 결정을 JSON으로 요약하라."
        try:
            response_text = self.backend.generate("gemini-1.5-pro", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            return {"final_decision": "Decision failed", "rationale": str(e)}

    def validate_constraints(self, constraints: List[str], tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """도구 호출이 시스템 규칙을 위반하는지 검증"""
        if not constraints: return {"is_valid": True}
        prompt = f"규칙: {json.dumps(constraints)}\n도구 호출: {json.dumps(tool_call)}\n위반 여부를 JSON으로 반환하라."
        try:
            response_text = self.backend.generate("gemini-1.5-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except: return {"is_valid": True}

    def suggest_refactor_target(self) -> Optional[Dict[str, Any]]:
        """프로젝트 내 기술 부채가 심한 파일을 리팩토링 대상으로 제안"""
        debt = self.scan_project_complexity()
        return debt[0] if debt else None

    def analyze_feedback(self, feedback: str) -> List[Dict[str, Any]]:
        """사용자 피드백을 분석하여 개선 규칙 추출"""
        prompt = f"피드백 분석: {feedback}\n개선이 필요한 규칙들을 JSON 리스트로 추출하라."
        try:
            response_text = self.backend.generate("gemini-1.5-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except: return []

    def learn_from_interaction(self, question: str, answer: str):
        """질의응답을 통한 실시간 지식 학습"""
        prompt = f"질문: {question}\n답변: {answer}\n시스템이 기억해야 할 핵심 정보를 추출하라."
        try:
            response_text = self.backend.generate("gemini-1.5-flash", [{"role": "user", "content": prompt}])
            from gortex.utils.vector_store import LongTermMemory
            LongTermMemory().memorize(f"User Knowledge: {response_text}", {"source": "Interaction"})
        except: pass

        def predict_next_actions(self, state: Any) -> List[Dict[str, str]]:

            """다음 사용자 행동 예측"""

            # 단순화된 예측 로직

            return [{"label": "테스트 실행", "command": "/test"}]

    

        def propose_test_generation(self) -> List[Dict[str, Any]]:

            """누락된 테스트에 대한 구체적인 시나리오 제안"""

            missing = self.identify_missing_tests()

            proposals = []

            

            for item in missing[:2]: # 한 번에 최대 2개씩만 진행

                file = item["file"]

                lines = item["missing_lines"]

                code_context = read_file(file)

                

                prompt = f"""다음 파이썬 파일의 누락된 라인({lines})을 테스트하는 unittest 코드를 작성하라.

                

                [File] {file}

                [Code]

                {code_context}

                

                기존 테스트 관례를 따르며, MagicMock을 적극 활용하여 독립적인 테스트를 구성하라. 

                오직 코드만 반환하라.

                """

                try:

                    test_code = self.backend.generate("gemini-1.5-pro", [{"role": "user", "content": prompt}])

                    test_code = re.sub(r'```python\n|```', '', test_code).strip()

                    proposals.append({

                        "target_file": f"tests/test_auto_{os.path.basename(file)}",

                        "content": test_code,

                        "reason": f"Low coverage ({item['coverage']}%)"

                    })

                except: pass

            return proposals

    