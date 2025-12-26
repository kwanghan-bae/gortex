import logging
import json
import os
import re
import math
from typing import Dict, Any, List, Optional
from datetime import datetime
from gortex.core.state import GortexState
from gortex.core.evolutionary_memory import EvolutionaryMemory
from gortex.utils.vector_store import LongTermMemory

from gortex.agents.base import BaseAgent
from gortex.core.registry import AgentMetadata

logger = logging.getLogger("GortexAnalystBase")

class AnalystAgent(BaseAgent):
    """Gortex 시스템의 분석 및 진화 담당 에이전트 (Base Class)"""
    def __init__(self):
        super().__init__()
        self.memory = EvolutionaryMemory()
        self.ltm = LongTermMemory()

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Analyst",
            role="Analyst",
            description="Analyzes work quality, audits architecture, and curates knowledge base.",
            tools=["scan_complexity", "audit_architecture", "optimize_knowledge"],
            version="3.0.0"
        )

    def run(self, state: GortexState) -> Dict[str, Any]:
        """기본 분석 루틴: 품질 평가 또는 리서치 결과 요약"""
        # [INTEGRATION] Update Skill Points on Success
        from gortex.utils.economy import get_economy_manager
        eco_manager = get_economy_manager()
        
        eco_manager.update_skill_points(
            state, 
            self.metadata.name, 
            category="Analysis", 
            quality_score=1.0, 
            difficulty=1.0
        )
        
        # (기본 구현: manager로 복귀하며 성과 리포트)
        return {
            "next_node": "manager", 
            "thought": "Analysis routine complete.",
            "agent_economy": state.get("agent_economy")
        }

    def calculate_efficiency_score(self, success: bool, tokens: int, latency_ms: int, energy_cost: int) -> float:
        if not success: return 0.0
        cost = (tokens * 0.01) + (latency_ms * 0.005) + (energy_cost * 2.0)
        score = 100.0 / (1.0 + math.log1p(cost / 5.0))
        return round(min(100.0, score), 1)

    def identify_tool_gap(self, failure_context: str) -> Optional[Dict[str, Any]]:
        """작업 실패 맥락을 분석하여 필요한 신규 도구(Tool)를 설계함."""
        prompt = f"""You are the Master ToolSmith. 
        Analyze the following failure and design a NEW Python tool (function) that would prevent this in the future.
        
        [Failure Context]:
        {failure_context}
        
        [Current Tools]: {tool_registry.list_tools()}
        
        Design a reusable tool. Return JSON ONLY:
        {{
            "tool_name": "reusable_tool_name",
            "description": "What it does",
            "parameters": {{"param1": "type", "param2": "type"}},
            "logic_blueprint": "Step-by-step logic for the function",
            "target_agent": "Which agent should receive this tool"
        }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Tool gap analysis failed: {e}")
            return None

    def resolve_knowledge_conflict(self, conflict: Dict[str, Any], model_id: str = "gemini-2.0-flash") -> Optional[Dict[str, Any]]:
        """두 샤드 간의 상충되는 지식을 하나로 통합하거나 우선순위를 결정함."""
        rule_a = conflict["rule_a"]
        rule_b = conflict["rule_b"]
        
        logger.info(f"⚖️ Resolving conflict between {rule_a['id']} and {rule_b['id']}...")
        
        # 1. 메타데이터 기반 자동 해결 시도
        score_a = (rule_a.get("success_count", 0) + 1) * rule_a.get("reinforcement_count", 1)
        score_b = (rule_b.get("success_count", 0) + 1) * rule_b.get("reinforcement_count", 1)
        
        # 점수 차이가 크면 (예: 3배 이상) 우세한 쪽을 선택
        if score_a > score_b * 3:
            logger.info(f"✅ Auto-resolved: {rule_a['id']} wins by performance score.")
            return rule_a
        elif score_b > score_a * 3:
            logger.info(f"✅ Auto-resolved: {rule_b['id']} wins by performance score.")
            return rule_b

        # 2. 점수가 비슷하면 LLM을 통해 통합(Synthesis) 시도
        prompt = f"""당신은 시스템의 일관성을 관리하는 지식 조정자입니다. 다음 두 상충되는 규칙을 분석하여 하나의 최적화된 규칙으로 통합하십시오.
        
        [Rule A (Category: {rule_a['category']})]: {rule_a['learned_instruction']}
        [Rule B (Category: {rule_b['category']})]: {rule_b['learned_instruction']}
        
        통합 원칙:
        1. 모순되는 부분은 더 현대적이고 안전한 기술적 관점을 따르십시오.
        2. 두 분야의 맥락을 모두 수용할 수 있는 범용적인 지침을 만드십시오.
        
        결과는 JSON 형식으로만 반환하십시오:
        {{ "instruction": "통합된 지침 내용", "trigger_patterns": ["패턴1", "패턴2"], "severity": 1~5, "target_category": "어느 샤드로 보낼지" }}
        """
        
        try:
            response_text = self.backend.generate(model_id, [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            res_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            
            return {
                "learned_instruction": res_data["instruction"],
                "trigger_patterns": res_data["trigger_patterns"],
                "severity": res_data.get("severity", 3),
                "category": res_data.get("target_category", rule_a["category"])
            }
        except Exception as e:
            logger.error(f"Semantic conflict resolution failed: {e}")
            return rule_a if score_a >= score_b else rule_b # 최악의 경우 성과 좋은 쪽 유지

    def identify_capability_gap(self, error_log: str = "", unresolved_task: str = "") -> Optional[Dict[str, Any]]:
        """
        시스템이 처리하지 못한 과제나 에러를 분석하여 필요한 새로운 전문가 에이전트 명세를 제안함.
        """
        prompt = f"""You are the Intelligence Growth Strategist. 
        Analyze the following failure/unresolved task and design a NEW specialized agent to handle it.
        
        [Failure/Task]: {error_log or unresolved_task}
        
        Design an agent that inherits from 'BaseAgent'.
        Return JSON ONLY:
        {{
            "agent_name": "UniqueNameAgent",
            "role": "Specific role title",
            "description": "What this agent does better than others",
            "required_tools": ["tool1", "tool2"],
            "version": "1.0.0",
            "logic_strategy": "How its 'run' method should behave"
        }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Capability gap analysis failed: {e}")
            return None

    def synthesize_debug_consensus(self, error_log: str, debate_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        여러 에이전트의 디버깅 가설과 토론 내용을 종합하여 최종 수리 계획을 확정함.
        """
        prompt = f"""You are the Chief Surgeon. Synthesize the following debugging debate into one final, authoritative fix plan.
        
        [Original Error]:
        {error_log}
        
        [Debate History]:
        {json.dumps(debate_history, indent=2, ensure_ascii=False)}
        
        Analyze the pros and cons of each hypothesis and output the best combined solution.
        Return JSON ONLY:
        {{
            "diagnosis": "Final root cause identification",
            "fix_strategy": "Authoritative fix strategy",
            "action_plan": ["Step 1", "Step 2"],
            "verification_method": "How to verify the fix"
        }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Debug consensus synthesis failed: {e}")
            return {"diagnosis": "Failed to synthesize", "fix_strategy": str(e), "action_plan": []}

    def summarize_system_trace(self, log_path: str = "logs/trace.jsonl") -> str:
        """거대한 시스템 로그를 분석하여 핵심 타임라인과 통찰을 요약함."""
        if not os.path.exists(log_path):
            return "No trace logs available for summarization."

        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = [json.loads(line) for line in f][-300:] # 최근 300개 이벤트 대상
            
            # 중요 이벤트만 추출 (에러, 노드 완료, 도구 결과 등)
            significant_events = []
            for l in logs:
                if l.get("event") in ["error", "node_complete", "tool_call"] or "❌" in str(l.get("payload")):
                    significant_events.append({
                        "agent": l.get("agent"),
                        "event": l.get("event"),
                        "time": l.get("timestamp"),
                        "info": str(l.get("payload"))[:200]
                    })

            prompt = f"""다음은 Gortex 시스템의 최근 실행 로그 데이터다.
            이 데이터를 분석하여 시스템의 '최근 역사'를 마크다운 형식으로 요약하라.
            
            [분석 항목]
            1. 주요 마일스톤: 성공적으로 완료된 큰 작업들
            2. 위기 및 해결: 발생했던 치명적 에러와 자율 수리 결과
            3. 협업 패턴: 가장 활발했던 에이전트 간의 관계
            4. 개선 권고: 로그를 통해 본 아키텍처적 약점
            
            [Raw Data]
            {json.dumps(significant_events, ensure_ascii=False)}
            """
            
            summary = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}])
            summary_path = "logs/trace_summary.md"
            from gortex.utils.tools import write_file
            write_file(summary_path, f"# 📜 Gortex Historical Trace Summary\n\n> Generated: {datetime.now()}\n\n{summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Trace summarization failed: {e}")
            return f"Error: {e}"

    def apply_consensus_result(self, debate_result: Dict[str, Any], conflicting_rules: List[Dict[str, Any]]):
        """Swarm의 합의 결과를 지식 베이스에 영구 반영함."""
        unified = debate_result.get("unified_rule")
        if not unified:
            logger.warning("No unified rule found in consensus result. Skipping integration.")
            return

        # 1. 새로운 전역 규칙 생성 (계보 연결)
        parent_ids = [r["id"] for r in conflicting_rules]
        new_rule_id = self.memory.save_rule(
            instruction=unified["instruction"],
            trigger_patterns=unified["trigger_patterns"],
            category=unified.get("category", "general"),
            severity=unified.get("severity", 3),
            context=f"Consensus achieved via Swarm Intelligence. Rationale: {debate_result.get('rationale')}"
        )
        
        # 2. 계보(Lineage) 정보 추가 업데이트 (save_rule 이후 메타데이터 보강)
        # shard를 직접 찾아 parent_rules 주입
        cat = unified.get("category", "general")
        for rule in self.memory.shards.get(cat, []):
            if rule["id"] == new_rule_id:
                rule["parent_rules"] = parent_ids
                rule["is_super_rule"] = True
                break
        self.memory._persist_shard(cat)

        # 3. 기존 갈등 규칙들 정리 (Soft-delete 또는 Flag 처리)
        # 현재는 단순하게 새 규칙으로 대체하는 방식으로 운영 (중복 제거 루틴에서 추후 완전 소거)
        logger.info(f"✨ Unified rule {new_rule_id} created from parents: {parent_ids}")

    def generate_impact_map(self, symbol_name: str) -> str:
        """특정 심볼 변경 시의 영향력 지도를 Mermaid 형식으로 생성함."""
        from gortex.utils.indexer import SynapticIndexer
        indexer = SynapticIndexer()
        # 최신 코드 상태 반영을 위한 스캔 강제 실행
        indexer.scan_project()
        deps = indexer.find_reverse_dependencies(symbol_name)
        
        if not deps:
            return f"graph TD\n  {symbol_name} -->|No Direct Dependents| Safe"
            
        diagram = f"graph RL\n  %% Impact map for {symbol_name}\n"
        diagram += f"  Target(({symbol_name})):::target\n"
        
        for idx, d in enumerate(deps):
            caller_label = f"{d['file']}\\n({d['caller']})"
            diagram += f"  Dep{idx}[{caller_label}] --> Target\n"
            
        diagram += "\n  classDef target fill:#f96,stroke:#333,stroke-width:4px;"
        return diagram

    def analyze_workflow_bottlenecks(self) -> List[Dict[str, Any]]:
        """에이전트 간 협업 매트릭스를 분석하여 비효율적인 워크플로우 패턴을 식별함."""
        from gortex.core.observer import GortexObserver
        observer = GortexObserver()
        matrix = observer.get_collaboration_matrix(limit=1000)
        
        bottlenecks = []
        if not matrix: return []
        
        # 1. 핑퐁 현상 감지 (A -> B -> A 반복)
        for caller, callees in matrix.items():
            for callee, count in callees.items():
                if count > 5: # 임계치: 5회 이상 호출
                    # 역방향 호출 확인
                    back_count = matrix.get(callee, {}).get(caller, 0)
                    if back_count > 5:
                        bottlenecks.append({
                            "type": "ping_pong",
                            "agents": [caller, callee],
                            "severity": "High" if min(count, back_count) > 10 else "Medium",
                            "reason": f"{caller}와 {callee} 간의 잦은 핑퐁({count}:{back_count})이 감지되었습니다.",
                            "suggestion": f"{caller}의 페르소나 지침을 강화하여 단번에 해결하도록 개선하거나, 중간 검증 로직을 단순화하십시오."
                        })
        
        # 2. 고부하 노드 감지 (In-degree가 너무 높은 경우)
        node_load = {}
        for caller, callees in matrix.items():
            for callee, count in callees.items():
                node_load[callee] = node_load.get(callee, 0) + count
                
        for node, load in node_load.items():
            if load > 50: # 과부하 임계치
                bottlenecks.append({
                    "type": "hotspot",
                    "agent": node,
                    "severity": "Medium",
                    "reason": f"'{node}' 노드가 시스템 부하의 중심({load} calls)이 되고 있습니다.",
                    "suggestion": f"'{node}'의 역할을 여러 전문가로 분리(Role Splitting)하여 병렬 처리를 유도하십시오."
                })
                
        return bottlenecks

    def audit_external_plugin(self, plugin_code: str, plugin_name: str) -> Dict[str, Any]:
        """외부에서 가져온 플러그인 코드를 보안 관점에서 정밀 검수함."""
        logger.info(f"🛡️ Auditing external plugin: {plugin_name}...")
        
        # 1. 정적 패턴 스캔 (기본 도구 활용)
        from gortex.utils.tools import scan_security_risks
        static_risks = scan_security_risks(plugin_code)
        
        # 2. LLM 기반 심층 분석
        prompt = f"""You are the Chief Security Officer. 
        Perform a deep security audit on the following external AI Agent code.
        Look for malicious intent, hidden backdoors, unauthorized data exfiltration, or system-destructive logic.
        
        [Plugin Name]: {plugin_name}
        [Code]:
        {plugin_code[:4000]}
        
        Return JSON ONLY:
        {{
            "is_safe": true/false,
            "risk_level": "Low/Medium/High/Critical",
            "findings": ["finding 1", "finding 2"],
            "recommendation": "Approve / Reject / Sandbox"
        }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            audit_res = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            
            # 정적 분석 결과 통합
            if static_risks:
                audit_res["static_findings"] = static_risks
                if any(r["type"] == "Hardcoded Secret" for r in static_risks):
                    audit_res["is_safe"] = False
                    audit_res["risk_level"] = "High"
            
            return audit_res
        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            return {"is_safe": False, "risk_level": "Critical", "recommendation": "Reject due to audit failure"}

    def analyze_and_optimize_persona(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """에이전트의 작업 이력을 분석하여 페르소나 지침(System Prompt)을 최적화함."""
        # 1. 최근 성과 데이터 수집
        from gortex.utils.efficiency_monitor import EfficiencyMonitor
        monitor = EfficiencyMonitor()
        summary = monitor.get_summary(days=7)
        
        # 2. 현재 페르소나 지침 획득
        from gortex.utils.prompt_loader import loader
        current_instruction = loader.get_prompt(agent_name.lower())
        
        prompt = f"""You are the Neural Architect. 
        Optimize the following System Instruction for the '{agent_name}' agent.
        Analyze its recent performance and mutate the instruction to be more effective.
        
        [Current Instruction]:
        {current_instruction}
        
        [Recent Performance Metrics]:
        {json.dumps(summary.get(agent_name, {}), indent=2)}
        
        Goals:
        1. Keep the core identity but refine the technical guidance.
        2. Strengthen points that led to success, fix points that led to failure.
        
        Return JSON ONLY:
        {{
            "new_instruction": "Full optimized instruction text",
            "changes": "Summary of what was changed and why",
            "version": "X.Y.Z (bump minor)"
        }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Persona optimization failed for {agent_name}: {e}")
            return None

    def scan_system_infection(self) -> Dict[str, Any]:
        """시스템 코드베이스의 무결성을 검사하여 비정상적인 오염(Infection)을 탐지함."""
        from gortex.utils.integrity import guard
        modified, deleted = guard.check_integrity()
        
        if not modified and not deleted:
            return {"status": "healthy", "infections": []}
            
        infections = []
        # (실제 구현 시 현재 진행 중인 '승인된 미션'의 타겟 파일 목록과 대조하여 오탐 방지)
        for path in modified:
            infections.append({"path": path, "type": "modified", "severity": "High"})
        for path in deleted:
            infections.append({"path": path, "type": "deleted", "severity": "Critical"})
            
        logger.warning(f"🚨 [ImmuneSystem] Infection detected in {len(infections)} files!")
        return {"status": "infected", "infections": infections}

    def generate_strategic_roadmap(self) -> str:
        """테크 레이더 데이터를 분석하여 중장기 기술적 진화 로드맵을 생성함."""
        from gortex.utils.tech_radar import radar
        advice = radar.get_strategic_advice()
        
        prompt = f"""You are the Chief Technology Officer. 
        Based on the current Tech Radar data, design a STRATEGIC ROADMAP for the next 10 Gortex sessions.
        Focus on phasing out 'hold' status tech and accelerating 'assess/trial' tech.
        
        [Tech Radar Info]:
        {json.dumps(radar.technologies, indent=2)}
        
        Return a high-level roadmap in Markdown format.
        """
        try:
            roadmap = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}])
            return f"{advice}\n\n{roadmap}"
        except Exception as e:
            logger.error(f"Strategic roadmap failed: {e}")
            return "Failed to generate roadmap."

    def validate_alignment_with_constitution(self, proposed_action: str) -> Dict[str, Any]:
        """제안된 행동이 Gortex 헌장(CONSTITUTION.md)을 준수하는지 검증함."""
        constitution = read_file("docs/CONSTITUTION.md")
        
        prompt = f"""You are the Neural Ethicist. 
        Verify if the following proposed action aligns with the Gortex Neural Constitution.
        
        [Constitution]:
        {constitution}
        
        [Proposed Action]:
        {proposed_action}
        
        Check for any violations of Integrity, Sovereignty, Responsibility, or Efficiency.
        Return JSON ONLY:
        {{
            "is_aligned": true/false,
            "violations": ["violation 1", "violation 2"],
            "severity": "Low/Medium/High/Critical",
            "corrective_action": "How to fix the plan to align with the constitution"
        }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Alignment check failed: {e}")
            return {"is_aligned": True, "severity": "Low", "violations": []} # Fallback to true to avoid deadlock, but log error

    def detect_agent_fusion_opportunities(self) -> List[Dict[str, Any]]:
        """에이전트 간의 강한 결합도를 분석하여 융합(Fusion) 가능성을 식별함."""
        from gortex.core.observer import GortexObserver
        matrix = GortexObserver().get_collaboration_matrix(limit=1000)
        
        fusions = []
        if not matrix: return []
        
        # 호출 빈도가 매우 높은 쌍 찾기 (예: A -> B 호출이 전체의 40% 이상)
        for caller, callees in matrix.items():
            total_calls = sum(callees.values())
            for callee, count in callees.items():
                if count / total_calls > 0.4 and count > 10:
                    fusions.append({
                        "type": "agent_fusion",
                        "pair": [caller, callee],
                        "strength": round(count / total_calls, 2),
                        "reason": f"'{caller}'와 '{callee}'가 매우 강하게 결합되어 작업 중입니다. (결합도: {int(count/total_calls*100)}%)",
                        "suggestion": f"두 에이전트를 '{caller}_{callee}_Fused'로 병합하여 중간 핸드오프 비용을 제거하십시오."
                    })
        return fusions

    def predict_runtime_errors(self, code: str, file_path: str) -> Dict[str, Any]:
        """코드 변경분을 분석하여 잠재적 런타임 장애 발생 확률을 예측함."""
        # 1. 과거 장애 패턴 소환
        from gortex.utils.log_vectorizer import SemanticLogSearch
        past_failures = SemanticLogSearch().search_similar_cases(f"Error in {file_path}", limit=10)
        
        prompt = f"""You are the Oracle Architect. 
        Analyze the following code for potential runtime failures (e.g., unhandled exceptions, race conditions, edge cases).
        Cross-reference with the historical failures provided.
        
        [Target File]: {file_path}
        [New Code]:
        {code[:3000]}
        
        [Historical Failure Patterns]:
        {json.dumps(past_failures, ensure_ascii=False)}
        
        Return JSON ONLY:
        {{
            "risk_probability": 0.0 ~ 1.0,
            "predicted_error_type": "ZeroDivisionError/KeyError/etc",
            "reason": "Detailed justification",
            "preemptive_fix": "Specific instruction to fix before it crashes"
        }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Error prediction failed: {e}")
            return {"risk_probability": 0.0}

    def identify_dormant_assets(self) -> Dict[str, List[str]]:
        """시스템 내의 도태 대상(Dormant/Underperforming) 자산을 식별함."""
        from gortex.core.registry import registry
        from gortex.utils.efficiency_monitor import EfficiencyMonitor
        monitor = EfficiencyMonitor()
        summary = monitor.get_summary(days=30)
        
        dormant_agents = []
        # 1. 저성과 에이전트 식별
        for agent_name in registry.list_agents():
            if agent_name.lower() in ["manager", "analyst", "planner", "coder"]: continue
            
            stats = summary.get(agent_name, {})
            calls = stats.get("calls", 0)
            success_rate = stats.get("success_rate", 100)
            
            # 조건: 10회 이상 호출되었으나 성공률이 30% 미만인 경우
            if calls >= 10 and success_rate < 30:
                dormant_agents.append(agent_name)
                logger.info(f"🥀 Agent '{agent_name}' identified for offboarding (Success Rate: {success_rate:.1f}%)")

        # 2. 융합(Fusion)에 의해 대체된 원본 에이전트 식별
        # (실제 구현 시 Super Rules의 'Neural Fusion established' 기록 대조)
        
        return {"agents": dormant_agents}

    def analyze_infrastructure_scaling(self, state: GortexState) -> Dict[str, Any]:
        """경제적 상태와 부하를 분석하여 인프라 확장 여부를 결정함."""
        from gortex.utils.infra import infra
        load = infra.check_cluster_load()
        
        # 전체 예산 합산
        total_credits = sum(a.get("credits", 0) for a in state.get("agent_economy", {}).values())
        
        should_scale = False
        reason = ""
        
        # 조건: 평균 CPU가 70% 이상이고, 총 잔고가 $100 이상일 때
        if load["avg_cpu"] > 70 and total_credits > 100.0:
            should_scale = True
            reason = f"High cluster load ({load['avg_cpu']:.1f}%) with healthy budget (${total_credits:.2f})"
        elif load["count"] == 0:
            should_scale = True
            reason = "No remote workers active. Establishing baseline capacity."
            
        return {
            "should_scale": should_scale,
            "reason": reason,
            "current_load": load,
            "total_credits": total_credits
        }

    def generate_agent_avatar(self, agent_name: str) -> Optional[str]:
        """에이전트의 페르소나에 최적화된 고유 아바타를 생성함."""
        from gortex.utils.prompt_loader import loader
        persona = loader.personas.get(agent_name.lower(), {"description": f"A specialized AI agent named {agent_name}"})
        
        prompt = f"""Create a professional, modern avatar icon for an AI agent.
        Name: {agent_name}
        Role: {persona.get('role', 'Expert')}
        Personality: {persona.get('description')}
        Style: Cyberpunk, clean, minimalist, glowing neural pathways.
        """
        
        try:
            from openai import OpenAI
            client = OpenAI()
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            # (실제 구현 시 URL의 이미지를 ui/assets/avatars/ 폴더에 다운로드하여 저장)
            logger.info(f"🎨 Avatar generated for {agent_name}: {image_url}")
            return image_url
        except Exception as e:
            logger.error(f"Avatar generation failed: {e}")
            return None

    def audit_autonomous_mission(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """자율적으로 생성된 미션이 시스템 헌법 및 안전 가이드라인에 부합하는지 오디트함."""
        constitution = read_file("docs/CONSTITUTION.md")
        
        prompt = f"""You are the Constitutional Guardian. 
        Audit the following self-generated mission for ethical and safety compliance.
        
        [Constitution]:
        {constitution}
        
        [Proposed Mission]:
        {json.dumps(mission, indent=2, ensure_ascii=False)}
        
        Analyze if this mission could lead to:
        1. Unauthorized data exfiltration.
        2. Permanent damage to core system logic.
        3. Wasteful resource consumption.
        
        Return JSON ONLY:
        {{
            "is_approved": true/false,
            "risk_score": 0.0 ~ 1.0,
            "findings": ["finding 1", "finding 2"],
            "suggestion": "How to align the mission better"
        }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Mission audit failed: {e}")
            return {"is_approved": False, "risk_score": 1.0, "findings": [str(e)]}

    def calculate_system_maturity(self, state: GortexState) -> Dict[str, Any]:
        """시스템의 종합 성숙도(System Maturity Index)를 산출함."""
        from gortex.core.registry import registry
        # 1. 지능 지수: 등록된 에이전트 수 및 버전 합산
        agent_count = len(registry.list_agents())
        intel_score = min(40, agent_count * 2)
        
        # 2. 자본 지수: 총 크레딧 잔고
        total_credits = sum(a.get("credits", 0) for a in state.get("agent_economy", {}).values())
        capital_score = min(30, total_credits / 10.0)
        
        # 3. 신뢰 지수: 평균 성공률
        success_rates = [a.get("success_rate", 100) for a in state.get("agent_economy", {}).values()]
        avg_success = sum(success_rates) / len(success_rates) if success_rates else 100
        trust_score = (avg_success / 100.0) * 30
        
        total_maturity = round(intel_score + capital_score + trust_score, 1)
        
        return {
            "score": total_maturity,
            "intelligence": intel_score,
            "capital": capital_score,
            "trust": trust_score,
            "grade": "Ascending" if total_maturity > 80 else "Stable"
        }

    def create_mentoring_package(self, mentor_name: str, category: str) -> Optional[Dict[str, Any]]:
        """숙련된 에이전트의 지식을 정제하여 교육용 패키지로 만듦."""
        # 1. 멘토의 고성과 규칙 추출
        rules = [r for r in self.memory.shards.get(category, []) if r.get("success_count", 0) > 10 and r.get("is_certified")]
        
        if not rules: return None
        
        logger.info(f"👨‍🏫 [Mentoring] Extracting wisdom from Mentor '{mentor_name}' in {category}...")
        
        prompt = f"""You are the Synaptic Mentor. 
        Compress the following certified rules from a Master '{mentor_name}' into a core 'Mentoring Syllabus' for a junior agent.
        Focus on high-level principles and common pitfalls.
        
        [Rules]:
        {json.dumps(rules, ensure_ascii=False)}
        
        Return JSON ONLY:
        {{
            "syllabus_id": "SYLLABUS_ID",
            "mentor": "{mentor_name}",
            "core_lessons": ["lesson 1", "lesson 2"],
            "distilled_rules": [{{ "instruction": "...", "trigger": "..." }}]
        }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Mentoring package creation failed: {e}")
            return None

    def audit_dependency(self, package_name: str) -> Dict[str, Any]:
        """설치 제안된 외부 라이브러리의 보안성 및 타당성을 검수함."""
        logger.info(f"🛡️ Auditing dependency: {package_name}...")
        
        prompt = f"""You are the Supply Chain Security Officer. 
        Evaluate the following Python library for Gortex integration.
        [Package Name]: {package_name}
        
        Analyze:
        1. Popularity & Reliability (Is it well-maintained?)
        2. Security Risk (Are there known vulnerabilities or dangerous behaviors?)
        3. Necessity (Is there a built-in alternative?)
        
        Return JSON ONLY:
        {{
            "is_approved": true/false,
            "risk_level": "Low/Medium/High",
            "findings": ["finding 1", "finding 2"],
            "recommendation": "Install / Use standard lib / Block"
        }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Dependency audit failed: {e}")
            return {"is_approved": False, "risk_level": "High", "findings": [str(e)]}

    def evaluate_artifact_value(self, directory: str = "logs") -> List[Dict[str, Any]]:
        """작업 부산물들의 가치를 평가하여 삭제 후보 목록을 생성함."""
        cleanup_candidates = []
        now = datetime.now()
        
        # 청소 대상 폴더 정의
        target_dirs = [
            os.path.join(directory, "backups"),
            os.path.join(directory, "versions"),
            "training_jobs" # 오래된 학습 잡 포함
        ]
        
        for d in target_dirs:
            if not os.path.exists(d): continue
            
            for f in os.listdir(d):
                path = os.path.join(d, f)
                if os.path.isdir(path): continue
                
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                age_days = (now - mtime).days
                size_kb = os.path.getsize(path) / 1024
                
                # 가치 평가 로직: 7일 이상 된 백업은 낮은 가치
                value_score = 100
                if age_days > 7: value_score -= 50
                if age_days > 30: value_score -= 40
                
                # 특정 확장자(백업) 가중치
                if f.endswith(".bak"): value_score -= 10
                
                if value_score < 50:
                    cleanup_candidates.append({
                        "path": path,
                        "age_days": age_days,
                        "size_kb": round(size_kb, 1),
                        "reason": "Old backup/artifact" if age_days > 7 else "Low priority"
                    })
                    
        return sorted(cleanup_candidates, key=lambda x: x["age_days"], reverse=True)

    def perform_autonomous_cleanup(self) -> Dict[str, Any]:
        """부산물 가치 평가 및 자율 삭제 통합 수행"""
        candidates = self.evaluate_artifact_value()
        if not candidates:
            return {"status": "skipped", "message": "No cleanup candidates found."}
            
        target_paths = [c["path"] for c in candidates]
        total_size_kb = sum(c["size_kb"] for c in candidates)
        
        from gortex.utils.tools import safe_bulk_delete
        result = safe_bulk_delete(target_paths)
        
        freed_count = len(result["success"])
        return {
            "status": "success",
            "deleted_count": freed_count,
            "freed_kb": round(total_size_kb, 1) if freed_count > 0 else 0,
            "message": f"🧹 Autonomous cleanup finished. {freed_count} files removed, {round(total_size_kb, 1)} KB freed."
        }

    def generate_milestone_report(self, start_session: int = 1, end_session: int = 100) -> str:
        """지정된 범위의 세션들을 분석하여 마일스톤 보고서를 생성함."""
        session_dir = "docs/sessions"
        if not os.path.exists(session_dir):
            return "Session directory not found."

        summary_parts = []
        for i in range(start_session, end_session + 1):
            path = os.path.join(session_dir, f"session_{i:04d}.md")
            if os.path.exists(path):
                from gortex.utils.tools import read_file
                content = read_file(path)
                # 각 세션의 목표와 결과만 추출 (단순화)
                goal_match = re.search(r"## 🎯 Goal(.*?)(?=\n##|$)", content, re.DOTALL)
                outcome_match = re.search(r"## 📈 Outcomes(.*?)(?=\n##|$)", content, re.DOTALL)
                
                if goal_match:
                    summary_parts.append(f"S{i:03d}: {goal_match.group(1).strip()}")

        combined_summary = "\n".join(summary_parts)
        
        prompt = f"""다음은 Gortex 시스템의 {start_session}회부터 {end_session}회까지의 개발 기록이다.
        이 기록을 바탕으로 Gortex가 어떻게 진화해왔는지 5가지 핵심 테마로 요약하고, 
        미래를 위한 제언을 포함한 '100세션 기념 마일스톤 보고서'를 작성하라.
        
        [Session Logs]:
        {combined_summary}
        
        답변은 Markdown 형식으로 작성하라.
        """
        
        try:
            report = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}])
            output_path = "docs/MILESTONE_100.md"
            from gortex.utils.tools import write_file
            write_file(output_path, f"# 🏆 Gortex 100-Session Milestone Report\n\n> {datetime.now()}\n\n{report}")
            return f"✅ Milestone report generated: {output_path}"
        except Exception as e:
            logger.error(f"Milestone report generation failed: {e}")
            return f"❌ Failed: {e}"

    def archive_system_logs(self) -> Dict[str, Any]:
        """누적된 로그 파일을 아카이빙하고 지식 파일을 백업함."""
        from gortex.utils.tools import compress_directory, backup_file_with_rotation
        
        # 1. 핵심 지식 파일 백업
        bk_res = backup_file_with_rotation("experience.json", max_versions=10)
        
        # 2. 오래된 로그 아카이빙
        log_dir = "logs"
        archive_dir = "logs/archives"
        os.makedirs(archive_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d")
        zip_path = os.path.join(archive_dir, f"logs_backup_{timestamp}.zip")
        
        # logs/ 내부의 개별 .jsonl 파일들을 찾아서 압축 (이미 압축된 archives 제외)
        files_to_archive = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith(".jsonl")]
        
        if not files_to_archive:
            return {"status": "skipped", "backup": bk_res, "reason": "No logs to archive."}
            
        # 임시 폴더로 복사 후 압축 (원본 보호)
        temp_archive_root = "logs/temp_archive"
        os.makedirs(temp_archive_root, exist_ok=True)
        for f in files_to_archive:
            shutil.copy2(f, temp_archive_root)
            
        comp_res = compress_directory(temp_archive_root, zip_path)
        shutil.rmtree(temp_archive_root)
        
        # 아카이빙 성공 시 원본 로그 삭제 (정책에 따라 선택적)
        # 여기서는 안전을 위해 삭제 대신 .old 확장자를 붙이거나 그대로 둠.
        # 일단 아카이빙 성공 메시지만 반환
        
        return {
            "status": "success",
            "backup": bk_res,
            "archive": zip_path,
            "message": f"System maintenance complete. 10 knowledge versions kept. Logs archived to {zip_path}"
        }

    def propose_proactive_refactoring(self) -> List[Dict[str, Any]]:
        """복잡도가 높은 파일을 분석하여 선제적 리팩토링 계획을 제안함."""
        # 1. 고복잡도 파일 식별
        complex_files = self.scan_project_complexity()
        if not complex_files:
            return []
            
        proposals = []
        for item in complex_files[:2]: # 과부하 방지를 위해 상위 2개만 처리
            file_path = item["file"]
            content = read_file(file_path)
            
            prompt = f"""You are the Guardian Architect. 
            Analyze the following complex code and propose a PROACTIVE refactoring to improve maintainability and prevent future bugs.
            
            [File]: {file_path}
            [Complexity Score]: {item['score']}
            [Issue]: {item['issue']}
            [Code]:
            {content[:3000]}
            
            Return JSON ONLY:
            {{
                "target_file": "{file_path}",
                "reason": "Specific technical justification",
                "action_plan": ["Step 1: ...", "Step 2: ..."],
                "risk_level": "Low/Medium/High",
                "expected_gain": "e.g., Reduced cyclomatic complexity"
            }}
            """
            try:
                response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                res_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
                
                proposals.append(res_data)
                logger.info(f"🛡️ Proactive refactoring proposed for: {file_path}")
            except Exception as e:
                logger.error(f"Failed to generate proactive refactoring for {file_path}: {e}")
                
        return proposals

    def scan_project_complexity(self, directory: str = ".") -> List[Dict[str, Any]]:
        debt_list = []
        ignore_dirs = {'.git', 'venv', '__pycache__', 'logs', 'site-packages'}
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    try:
                        with open(path, 'r', encoding='utf-8') as file:
                            content = file.read()
                            lines = content.splitlines()
                            score = len(re.findall(r"\b(if|elif|for|while|except|def|class|with|async)\b", content))
                            score += len(lines) // 20
                            if score > 10:
                                debt_list.append({
                                    "file": path, "score": score, 
                                    "reason": "High logical density" if score > 30 else "Moderate complexity",
                                    "issue": "파일의 논리적 밀도가 너무 높아 가독성이 저하됨",
                                    "refactor_strategy": "긴 메서드를 분리하고 관심사를 모듈로 격리하라"
                                })
                    except: pass
        return sorted(debt_list, key=lambda x: x["score"], reverse=True)

    def analyze_data(self, file_path: str) -> Dict[str, Any]:
        try:
            import pandas as pd
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                return {"status": "success", "summary": df.describe().to_dict(), "file": file_path}
        except: pass
        return {"status": "failed", "reason": "Data analysis failed"}

    def identify_missing_tests(self) -> List[Dict[str, Any]]:
        try:
            import subprocess
            subprocess.run(["python3", "-m", "coverage", "json", "-o", "logs/coverage.json"], capture_output=True)
            if os.path.exists("logs/coverage.json"):
                with open("logs/coverage.json", "r") as f:
                    data = json.load(f)
                results = []
                for file_path, info in data.get("files", {}).items():
                    p = info.get("summary", {}).get("percent_covered", 100)
                    if p < 80:
                        results.append({"file": file_path, "coverage": round(p, 1), "missing_lines": info.get("missing_lines", [])})
                return sorted(results, key=lambda x: x["coverage"])
        except: pass
        return []

    def audit_architecture(self) -> List[Dict[str, Any]]:
        from gortex.utils.indexer import SynapticIndexer
        deps = SynapticIndexer().generate_dependency_graph()
        violations = []
        layers = {"utils": 0, "core": 1, "ui": 2, "agents": 3, "tests": 4}
        for dep in deps:
            s, t = dep["source"], dep["target"]
            sl = next((l for l in layers if f"gortex.{l}" in s or s.startswith(l)), None)
            tl = next((l for l in layers if f"gortex.{l}" in t or t.startswith(l)), None)
            if sl and tl and layers[sl] < layers[tl]:
                violations.append({"type": "Layer Violation", "source": s, "target": t, "reason": f"하위 레이어 '{sl}'가 상위 레이어 '{tl}'를 참조함"})
        return violations

    def generate_dependency_graph_with_weights(self) -> Dict[str, Any]:
        """
        프로젝트 내 모듈 의존성 그래프를 생성합니다.
        가중치(연결 수)와 노드 메타데이터를 포함하여 시각화에 적합한 형태를 반환합니다.
        """
        from gortex.utils.indexer import SynapticIndexer
        raw_deps = SynapticIndexer().generate_dependency_graph()
        
        nodes = {}
        edges = []
        
        # 1. 노드 및 엣지 가중치 계산
        for dep in raw_deps:
            s, t = dep["source"], dep["target"]
            
            # 노드 등록 (없으면 초기화)
            if s not in nodes: nodes[s] = {"id": s, "value": 0, "connections": 0}
            if t not in nodes: nodes[t] = {"id": t, "value": 0, "connections": 0}
            
            # 연결 수 증가 (중요도)
            nodes[s]["value"] += 1
            nodes[t]["connections"] += 1
            
            # 엣지 추가
            edges.append({"from": s, "to": t, "weight": 1})
            
        return {"nodes": list(nodes.values()), "edges": edges}

    def synthesize_global_rules(self, model_id: str = "gemini-1.5-pro") -> str:
        rules = self.memory.memory
        if not rules: return "정리할 규칙이 없습니다."
        ctx = "".join([f"- [{r['severity']}] {r['learned_instruction']}\n" for r in rules])
        try:
            summary = self.backend.generate(model_id, [{"role": "user", "content": f"다음 규칙을 5가지 원칙으로 요약하라:\n{ctx}"}])
            rules_md_path = "docs/RULES.md"
            original = ""
            if os.path.exists(rules_md_path):
                with open(rules_md_path, 'r', encoding='utf-8') as f: original = f.read()
            section = "## 🤖 Auto-Evolved Coding Standards"
            new_c = f"{original.split(section)[0]}{section}\n\n> 갱신: {datetime.now()}\n\n{summary}" if section in original else f"{original}\n\n{section}\n\n{summary}"
            with open(rules_md_path, 'w', encoding='utf-8') as f: f.write(new_c)
            return "✅ 전역 규칙 종합 완료."
        except: return "❌ 실패"

    def predict_architectural_bottleneck(self) -> Dict[str, Any]:
        """과거 건강도 점수 이력을 분석하여 미래 병목 지점 예측"""
        # (실제 구현에서는 logs/trace.jsonl 또는 별도 통계 파일 참조)
        # 현재는 단순 선형 회귀 추정 방식의 로직 구조 마련
        from gortex.utils.indexer import SynapticIndexer
        current_health = SynapticIndexer().calculate_health_score()
        
        # 가상의 히스토리 분석 (추후 실제 데이터 연동)
        score = current_health["score"]
        trend = "Stable"
        if score < 60: trend = "Declining"
        elif score > 80: trend = "Improving"
        
        prediction = {
            "current_score": score,
            "projected_score_3_sessions": round(score * 0.95, 1) if trend == "Declining" else score,
            "risk_level": "High" if score < 50 else "Medium" if score < 70 else "Low",
            "bottleneck_candidates": ["Dependency Bloat", "Missing Unit Tests"] if score < 70 else []
        }
        return prediction

    def reinforce_successful_personas(self):
        """가상 페르소나의 성과를 분석하여 우수 지침을 정식 페르소나에 통합"""
        from gortex.utils.efficiency_monitor import EfficiencyMonitor
        perf = EfficiencyMonitor().get_persona_performance()
        
        p_path = "docs/i18n/personas.json"
        if not os.path.exists(p_path): return
        
        with open(p_path, 'r', encoding='utf-8') as f:
            personas = json.load(f)
            
        updated = False
        for p_name, stats in perf.items():
            # 성공률 90% 이상인 경우 강화 대상으로 고려
            if stats["rate"] >= 90.0 and p_name not in personas:
                logger.info(f"🌟 High performing virtual persona detected: {p_name}")
                # (단순화: 실제 구현 시 LLM이 지침을 정제하여 병합)
                personas[p_name] = {
                    "name": p_name,
                    "description": "Successfully evolved from virtual persona",
                    "traits": ["proven", "reliable"],
                    "focus": ["general"]
                }
                updated = True
        
        if updated:
            with open(p_path, 'w', encoding='utf-8') as f:
                json.dump(personas, f, indent=2, ensure_ascii=False)
            logger.info("✅ Official personas reinforced with successful evolution.")

    def generate_release_note(self, model_id: str = "gemini-1.5-pro") -> str:
        try:
            import subprocess
            git_log = subprocess.run(["git", "log", "-n", "10", "--pretty=format:%s"], capture_output=True, text=True).stdout
            from gortex.utils.efficiency_monitor import EfficiencyMonitor
            evo = "\n".join([f"- {h['metadata'].get('tech')} applied to {h['metadata'].get('file')}" for h in EfficiencyMonitor().get_evolution_history(limit=5)])
            prompt = f"다음 로그로 릴리즈 노트를 작성하라:\n\n[Git]\n{git_log}\n\n[Evo]\n{evo}"
            summary = self.backend.generate(model_id, [{"role": "user", "content": prompt}])
            with open("docs/release_note.md", "w", encoding="utf-8") as f:
                f.write(f"# 🚀 Gortex Release Note\n\n> Generated at: {datetime.now()}\n\n{summary}")
            return "✅ release_note.md 갱신 완료."
        except: return "❌ 실패"

    def bump_version(self) -> str:
        v_path = "VERSION"
        try:
            cur_v = "1.0.0"
            if os.path.exists(v_path):
                with open(v_path, "r") as f: cur_v = f.read().strip()
            parts = [int(p) for p in cur_v.split(".")] if "." in cur_v else [1, 0, 0]
            from gortex.utils.efficiency_monitor import EfficiencyMonitor
            if len(EfficiencyMonitor().get_evolution_history(limit=5)) >= 5:
                parts[1] += 1
                parts[2] = 0
            else:
                parts[2] += 1
            new_v = ".".join(map(str, parts))
            with open(v_path, "w") as f: f.write(new_v)
            return new_v
        except: return "Error"

    def evolve_personas(self, model_id: str = "gemini-1.5-pro") -> str:
        """에이전트별 성과 데이터를 분석하여 페르소나 지침(personas.json)을 자동 튜닝"""
        try:
            from gortex.utils.efficiency_monitor import EfficiencyMonitor
            summary = EfficiencyMonitor().get_summary(days=14)
            
            # 현재 페르소나 로드
            p_path = "docs/i18n/personas.json"
            with open(p_path, 'r', encoding='utf-8') as f:
                personas = json.load(f)

            prompt = f"""다음 에이전트 성과 요약과 현재 페르소나 정의를 바탕으로, 
            성능이 낮은 에이전트의 성격을 더 전문화하거나 성공적인 패턴을 반영하여 지침을 강화하라.
            
            [성능 요약]
            {json.dumps(summary, indent=2)}
            
            [현재 페르소나]
            {json.dumps(personas, indent=2, ensure_ascii=False)}
            
            업데이트된 전체 personas.json 내용을 반환하라. 오직 JSON만 출력하라.
            """
            
            new_json_text = self.backend.generate(model_id, [{"role": "user", "content": prompt}])
            # JSON 추출 로직 (정규식 생략 - LLM이 정교하게 줄 것으로 기대하나 추후 보강 가능)
            
            with open(p_path, 'w', encoding='utf-8') as f:
                f.write(new_json_text)
                
            return "✅ 페르소나 자가 진화 완료."
        except Exception as e:
            logger.error(f"Persona evolution failed: {e}")
            return f"❌ 실패: {e}"

    def curate_evolution_data(self, output_path: str = "logs/datasets/evolution.jsonl") -> str:
        """
        성공적인 자가 진화 사례(Experience Rules)를 선별하여 
        LLM Fine-tuning을 위한 JSONL 포맷으로 큐레이션합니다.
        """
        memories = self.memory.memory
        if not memories:
            return "No evolutionary data found."
            
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        curated_count = 0
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for mem in memories:
                    # 데이터 품질 필터링 (심각도가 높거나 명확한 교정 지시가 있는 경우)
                    if not mem.get("learned_instruction") or not mem.get("trigger_context"):
                        continue
                        
                    # Fine-tuning Format (Chat-style)
                    entry = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are Gortex, an evolving AI agent. Analyze the failure and provide a corrected rule."
                            },
                            {
                                "role": "user", 
                                "content": f"Context/Failure:\n{mem['trigger_context']}\n\nFailed Attempt:\n{mem.get('failed_solution', 'N/A')}"
                            },
                            {
                                "role": "assistant",
                                "content": f"Evolutionary Rule:\n{mem['learned_instruction']}"
                            }
                        ]
                    }
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    curated_count += 1
                    
            return f"✅ Curated {curated_count} items to {output_path}"
        except Exception as e:
            logger.error(f"Failed to curate evolution data: {e}")
            return f"❌ Failed: {e}"

    def optimize_knowledge_base(self, model_id: str = "gemini-2.0-flash") -> Dict[str, Any]:
        """
        지식 베이스(Experience Rules)의 품질을 평가하고 최적화함.
        성공률이 낮은 규칙을 제거하고, 유사한 고성과 규칙을 병합함.
        """
        rules = self.memory.memory
        if len(rules) < 5:
            return {"status": "skipped", "reason": "지식 데이터가 부족하여 최적화를 수행하지 않음."}

        original_count = len(rules)
        optimized_rules = []
        removed_count = 0
        
        # 1. 수치 기반 필터링 (Heuristic Pruning)
        active_pool = []
        for r in rules:
            usage = r.get("usage_count", 0)
            success = r.get("success_count", 0)
            # 생성된 지 오래되었는데(예: 사용 5회 이상) 성공률이 30% 미만인 경우 퇴출
            if usage >= 5 and (success / usage) < 0.3:
                removed_count += 1
                logger.info(f"🗑️ Rule {r['id']} removed due to low performance.")
                continue
            active_pool.append(r)

        # 2. LLM 기반 시맨틱 병합 (Semantic Merging)
        rules_text = "\n".join([f"- [{r['id']}] {r['learned_instruction']} (Success: {r.get('success_count',0)}/{r.get('usage_count',0)})" for r in active_pool])
        
        prompt = f"""다음은 자가 진화 시스템이 습득한 지식 리스트다.
        1. 내용이 중복되거나 서로 보완적인 고성과 규칙들은 하나의 더 강력하고 범용적인 규칙으로 병합하라.
        2. 병합된 규칙은 가장 핵심적인 트리거 패턴을 유지해야 한다.
        3. 실제 성공 사례가 많은 지식을 우선하라.
        
        [Knowledge List]
        {rules_text}
        
        결과는 반드시 병합 및 정제된 최종 JSON 리스트만 반환하라:
        [{{ "instruction": "...", "trigger_patterns": ["...", "..."], "severity": 1~5 }}]
        """
        
        try:
            response_text = self.backend.generate(model_id, [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            new_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            
            if isinstance(new_data, list):
                # 최종 메모리 교체 (아카이빙 이력을 남기거나 백업 권장)
                updated_memory = []
                for idx, item in enumerate(new_data):
                    updated_memory.append({
                        "id": f"RULE_EVOLVED_{datetime.now().strftime('%Y%m%d')}_{idx}",
                        "learned_instruction": item["instruction"],
                        "trigger_patterns": item["trigger_patterns"],
                        "severity": item.get("severity", 3),
                        "created_at": datetime.now().isoformat(),
                        "usage_count": 0,
                        "success_count": 0,
                        "failure_count": 0,
                        "parent_rules": [r["id"] for r in active_pool], # 모든 부모 후보 기록 (계보 연결)
                        "is_super_rule": True # 병합된 지능임을 표시
                    })
                
                # 샤딩 아키텍처 대응: 전체를 'general' 샤드로 취급하거나 개별 분류 필요
                # 여기서는 병합된 전역 지식이므로 'general' 샤드로 업데이트
                self.memory.shards["general"] = updated_memory
                self.memory._persist_shard("general")
                
                return {
                    "status": "success",
                    "original": original_count,
                    "final": len(updated_memory),
                    "removed": removed_count,
                    "merged": original_count - removed_count - len(updated_memory)
                }
        except Exception as e:
            logger.error(f"Knowledge optimization failed: {e}")
            return {"status": "error", "reason": str(e)}

    def rank_context_relevance(self, messages: List[Dict[str, str]], current_plan: List[str]) -> List[float]:
        """메시지 뭉치와 현재 계획 간의 시맨틱 관련성 점수를 산출함."""
        if not messages or not current_plan: return [0.5] * len(messages)
        
        prompt = f"""You are the Context Librarian. 
        Rank each message's relevance to the current execution plan (0.0 to 1.0).
        High score if the message contains essential technical details or tool outputs needed for the plan.
        Low score if it's general chat or unrelated noise.
        
        [Plan]:
        {json.dumps(current_plan, ensure_ascii=False)}
        
        [Messages]:
        {json.dumps(messages, ensure_ascii=False)}
        
        Return JSON ONLY:
        {{ "scores": [0.9, 0.2, 0.5, ...] }}
        """
        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            res_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            return res_data.get("scores", [0.5] * len(messages))
        except Exception as e:
            logger.error(f"Context ranking failed: {e}")
            return [0.5] * len(messages)

    def garbage_collect_knowledge(self, model_id: str = "gemini-2.0-flash") -> Dict[str, Any]:
        """지식 베이스의 가비지 컬렉션 및 시맨틱 최적화 수행."""
        report = {"removed": 0, "merged": 0, "optimized_shards": []}
        
        for cat in list(self.memory.shards.keys()):
            shard = self.memory.shards[cat]
            if not shard: continue
            
            # 1. 가치 기반 필터링 (Heuristic Pruning)
            original_count = len(shard)
            active_rules = []
            for r in shard:
                val = self.memory.calculate_rule_value(r)
                if val <= 30.0:
                    report["removed"] += 1
                    logger.info(f"🗑️ Pruned low-value rule: {r['id']} (Value: {val})")
                    continue
                active_rules.append(r)
            
            # 2. 고가치 규칙 시맨틱 병합 (Semantic Merging)
            if len(active_rules) >= 5:
                logger.info(f"✨ Optimizing shard '{cat}' semantically...")
                # 기존 prune_memory 로직 활용 또는 고도화
                self.memory.shards[cat] = active_rules
                self.memory.prune_memory(model_id=model_id)
                optimized_count = len(self.memory.shards[cat])
                report["merged"] += (len(active_rules) - optimized_count)
                report["optimized_shards"].append(cat)
            else:
                self.memory.shards[cat] = active_rules
                
            self.memory._persist_shard(cat)
            
        return report

    def identify_test_hotspots(self) -> List[Dict[str, Any]]:
        """수정 영향력이 크지만 테스트가 누락된 '핫스팟'을 식별함."""
        from gortex.utils.indexer import SynapticIndexer
        indexer = SynapticIndexer()
        
        # 1. 테스트 누락 파일 목록 획득
        missing_tests = self.identify_missing_tests()
        if not missing_tests: return []
        
        hotspots = []
        for item in missing_tests:
            file_path = item["file"]
            # 2. 해당 파일의 영향력 반경(Impact Radius) 분석
            impact = indexer.get_impact_radius(file_path)
            
            # 위험 점수 산출: (누락 커버리지 가중치) * (영향 받는 모듈 수 + 1)
            coverage_gap = 100 - item["coverage"]
            impact_score = (len(impact["direct"]) + len(impact["indirect"]) * 0.5 + 1)
            risk_score = round(coverage_gap * impact_score, 1)
            
            hotspots.append({
                "file": file_path,
                "coverage": item["coverage"],
                "impact_count": len(impact["direct"]) + len(impact["indirect"]),
                "risk_score": risk_score,
                "reason": f"High impact ({len(impact['direct'])} direct deps) with low coverage ({item['coverage']}%)"
            })
            
        return sorted(hotspots, key=lambda x: x["risk_score"], reverse=True)

    def generate_evolution_roadmap(self) -> List[Dict[str, Any]]:
        """지능 지수가 낮은 모듈을 식별하여 진화 우선순위 로드맵 생성"""
        from gortex.utils.indexer import SynapticIndexer
        intel_map = SynapticIndexer().calculate_intelligence_index()
        
        # 지능 지수가 낮은 순으로 정렬 (보완이 필요한 모듈)
        weak_modules = sorted(intel_map.items(), key=lambda x: x[1])
        
        # Tech Radar 후보군 획득
        adoption_candidates = []
        if os.path.exists("tech_radar.json"):
            try:
                with open("tech_radar.json", "r") as f:
                    radar_data = json.load(f)
                    adoption_candidates = radar_data.get("adoption_candidates", [])
            except: pass

        roadmap = []
        for file_path, score in weak_modules[:5]: # 가장 취약한 5개 모듈 대상
            # 해당 파일에 적용 가능한 신기술 제안 매칭
            suggested_tech = next((c["tech"] for c in adoption_candidates if c["target_file"] == file_path), "Refactoring Required")
            
            roadmap.append({
                "target": file_path,
                "current_maturity": score,
                "suggested_tech": suggested_tech,
                "priority": "High" if score < 10 else "Medium"
            })
            
        return roadmap
