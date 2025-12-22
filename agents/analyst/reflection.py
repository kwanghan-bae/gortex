import json
import logging
import re
import ast
import os
from typing import Dict, Any, List, Optional
from gortex.agents.analyst.base import AnalystAgent
from gortex.utils.tools import read_file, write_file

logger = logging.getLogger("GortexAnalystReflection")

class ReflectionAnalyst(AnalystAgent):
    """시스템의 사고 과정을 성찰하고 진화 규칙을 생성하는 전문가"""
    
    def diagnose_bug(self, error_log: str) -> Dict[str, Any]:
        """
        시스템 로그를 분석하여 버그의 원인 지점을 특정하고 수정 계획을 수립함.
        """
        prompt = f"""You are the System Surgeon. Analyze this error log and find the root cause.
        
        [Error Log]:
        {error_log}
        
        Return JSON ONLY:
        {{
            "bug_type": "LogicError/SyntaxError/ImportError/etc",
            "target_file": "path/to/file.py",
            "line_number": 123,
            "cause_analysis": "Detailed reason",
            "fix_instruction": "Specific instruction for Coder",
            "is_patchable": true/false
        }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            res_data = json.loads(re.search(r'\{.*\}', response_text, re.DOTALL).group(0))
            return res_data
        except Exception as e:
            logger.error(f"Bug diagnosis failed: {e}")
            return {"is_patchable": False, "reason": str(e)}

    def evaluate_work_quality(self, agent_name: str, task: str, result: str) -> Dict[str, Any]:
        """
        특정 에이전트의 작업 결과물을 평가하여 품질 점수를 산출함.
        """
        prompt = f"""You are the Quality Assurance Chief. 
        Evaluate the work done by Agent '{agent_name}'.
        
        [Task]: {task}
        [Result]:
        {result}
        
        Evaluate based on:
        1. Technical Integrity (Is it correct and robust?)
        2. Efficiency (Did it use optimal path?)
        3. Compliance (Did it follow system rules?)
        
        Return JSON ONLY:
        {{
            "quality_score": 0.0 ~ 2.0 (1.0 is standard),
            "category": "Coding/Research/Design/Analysis",
            "rationale": "Brief reason for score",
            "feedback": "Feedback for the agent to improve"
        }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            res_data = json.loads(re.search(r'\{.*\}', response_text, re.DOTALL).group(0))
            return res_data
        except Exception as e:
            logger.error(f"Work quality evaluation failed: {e}")
            return {"quality_score": 1.0, "category": "Analysis", "rationale": "Fallback score due to error", "feedback": str(e)}

    def check_documentation_drift(self, file_path: str, doc_path: str, target_symbol: str) -> Dict[str, Any]:
        """
        코드 파일의 특정 심볼(Class/Function) 정의와 문서 내 기술(Markdown Code Block)을 비교하여
        불일치(Drift) 여부를 감지하고, 필요 시 문서 업데이트를 수행합니다.
        """
        if not os.path.exists(file_path) or not os.path.exists(doc_path):
            return {"status": "error", "reason": "File or doc not found"}

        # 1. Extract Code Definition (AST)
        try:
            code_content = read_file(file_path)
            tree = ast.parse(code_content)
            target_node = None
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == target_symbol:
                    target_node = node
                    break
            
            if not target_node:
                # If it's a TypedDict, it might be an assignment: GortexState = TypedDict(...)
                # But typically TypedDict is defined as class GortexState(TypedDict): ...
                # Let's assume class definition for now as per core/state.py
                return {"status": "skipped", "reason": f"Symbol {target_symbol} not found in AST"}

            # Reconstruct source for the target node
            start_line = target_node.lineno - 1
            end_line = target_node.end_lineno
            lines = code_content.splitlines()
            target_source = "\n".join(lines[start_line:end_line])

        except Exception as e:
            return {"status": "error", "reason": f"AST parsing failed: {e}"}

        # 2. Extract Doc Definition (Regex)
        doc_content = read_file(doc_path)
        # Find code block that likely describes this symbol
        # Strategy: Look for ```python ... class TargetSymbol ... ```
        pattern = rf"```python\n(class {target_symbol}.*?)\n```"
        match = re.search(pattern, doc_content, re.DOTALL)
        
        doc_source = match.group(1) if match else None
        
        if not doc_source:
            return {"status": "skipped", "reason": f"Documentation for {target_symbol} not found"}

        # 3. Compare (Simple String/Structure Comparison)
        # Whitespace normalization
        norm_code = re.sub(r'\s+', ' ', target_source).strip()
        norm_doc = re.sub(r'\s+', ' ', doc_source).strip()
        
        # 주석 등 세부 사항이 다를 수 있으므로, 단순 길이 차이나 필드명 존재 여부로 판단
        # 여기서는 LLM을 사용하여 의미적 불일치를 판단
        prompt = f"""Compare the following code and documentation for '{target_symbol}'.
        Does the documentation accurately reflect the code structure?
        Ignore minor formatting or comment differences. Focus on fields, types, and logic.
        
        [Actual Code]
        {target_source}
        
        [Documentation]
        {doc_source}
        
        If significant drift is detected (e.g. missing fields, wrong types), return JSON:
        {{ "drift_detected": true, "reason": "...", "suggested_doc": "Updated markdown code block content" }}
        
        Else:
        {{ "drift_detected": false }}
        """
        
        try:
            # 보다 안정적인 성능을 위해 gemini-2.0-flash 사용 권장
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            res_data = json.loads(re.search(r'\{.*\}', response_text, re.DOTALL).group(0))
            
            if res_data.get("drift_detected"):
                # 4. Auto-Heal (Update Doc)
                new_block = f"```python\n{res_data['suggested_doc']}\n```"
                new_doc_content = doc_content.replace(match.group(0), new_block)
                write_file(doc_path, new_doc_content)
                logger.info(f"🩹 Healed documentation drift for {target_symbol} in {doc_path}")
                return {"status": "healed", "reason": res_data["reason"]}
            else:
                return {"status": "synced"}
                
        except Exception as e:
            logger.error(f"Drift check failed: {e}")
            return {"status": "error", "reason": str(e)}

    def generate_anti_failure_rule(self, error_log: str, context: str) -> Optional[Dict[str, Any]]:
        """실패 사례 분석을 통한 방어 규칙 생성"""
        prompt = f"다음 에러를 분석하여 재발 방지 규칙을 JSON으로 제안하라.\nError: {error_log}\nContext: {context}"
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{{.*\}}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Rule generation failed: {e}")
            return None

    def synthesize_consensus(self, topic: str, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """여러 에이전트의 상반된 의견을 조율하여 최종 합의안 도출"""
        prompt = f"주제: {topic}\n토론 데이터: {json.dumps(scenarios)}\n가장 합리적인 최종 결정을 JSON으로 요약하라."
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{{.*\}}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            return {"final_decision": "Decision failed", "rationale": str(e)}

    def validate_constraints(self, constraints: List[str], tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """도구 호출이 시스템 규칙을 위반하는지 검증"""
        if not constraints: return {"is_valid": True}
        prompt = f"규칙: {json.dumps(constraints)}\n도구 호출: {json.dumps(tool_call)}\n위반 여부를 JSON으로 반환하라."
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{{.*\}}', response_text, re.DOTALL)
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
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except: return []

    def learn_from_interaction(self, question: str, answer: str):
        """질의응답을 통한 실시간 지식 학습"""
        prompt = f"질문: {question}\n답변: {answer}\n시스템이 기억해야 할 핵심 정보를 추출하라."
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}])
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
                response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}])
                test_code = re.sub(r'```python\n|```', '', response_text).strip()
                proposals.append({
                    "target_file": f"tests/test_auto_{os.path.basename(file)}",
                    "content": test_code,
                    "reason": f"Low coverage ({item['coverage']}%)"
                })
            except: pass
        return proposals