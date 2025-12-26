import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger("GortexKnowledgeGraph")

class KnowledgeGraph:
    """
    Gortex의 분산된 지능(에이전트, 규칙, 역사)을 그래프 구조로 통합함.
    """
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.node_ids = set()

    def add_node(self, node_id: str, label: str, type: str, metadata: Dict[str, Any] = None):
        if node_id not in self.node_ids:
            self.nodes.append({
                "id": node_id,
                "label": label,
                "type": type,
                "metadata": metadata or {}
            })
            self.node_ids.add(node_id)

    def add_edge(self, source: str, target: str, relation: str):
        self.edges.append({
            "source": source,
            "target": target,
            "relation": relation
        })

    def build_from_system(self):
        """시스템 메모리와 로그로부터 그래프를 구성함"""
        # 1. 에이전트 노드 추가
        from gortex.core.registry import registry
        for agent in registry.list_agents():
            meta = registry.get_metadata(agent)
            self.add_node(f"agent:{agent}", agent.capitalize(), "agent", {"role": meta.role})

        # 2. 경험 규칙 노드 및 계보 연결
        from gortex.core.evolutionary_memory import EvolutionaryMemory
        memory = EvolutionaryMemory()
        for rule in memory.memory:
            rule_id = f"rule:{rule['id']}"
            self.add_node(rule_id, rule['learned_instruction'][:30] + "...", "rule", {
                "category": rule.get("category"),
                "severity": rule.get("severity")
            })
            
            # 부모 규칙이 있다면 연결 (지능의 계보)
            if "parent_rules" in rule:
                for p_id in rule["parent_rules"]:
                    self.add_edge(f"rule:{p_id}", rule_id, "evolved_into")

        # 3. 최근 실행 이력(Trace) 기반 인과 관계 연결
        log_path = "logs/trace.jsonl"
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    logs = [json.loads(line) for line in f][-100:]
                
                for log in logs:
                    if "id" in log and "agent" in log:
                        event_id = f"event:{log['id']}"
                        agent_id = f"agent:{log['agent'].lower()}"
                        
                        self.add_node(event_id, log.get("event", "action"), "event")
                        self.add_edge(agent_id, event_id, "performed")
                        
                        if "cause_id" in log and log["cause_id"]:
                            self.add_edge(f"event:{log['cause_id']}", event_id, "caused")
            except Exception as e:
                logger.warning(f"Failed to parse trace for KG: {e}")

    def to_json(self) -> str:
        return json.dumps({"nodes": self.nodes, "edges": self.edges}, ensure_ascii=False, indent=2)

    def generate_summary(self) -> str:
        types = {}
        for n in self.nodes:
            types[n["type"]] = types.get(n["type"], 0) + 1
        
        summary = "### 🧠 Gortex Neural Map Summary\n"
        for t, count in types.items():
            summary += f"- **{t.capitalize()}s**: {count}\n"
        summary += f"- **Connections (Edges)**: {len(self.edges)}\n"
        return summary
