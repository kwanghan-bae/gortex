import unittest
import os
import shutil
import json
from unittest.mock import MagicMock, patch
from gortex.agents.coder import CoderAgent
from gortex.agents.trend_scout import TrendScoutAgent
from gortex.core.registry import registry
from gortex.core.state import GortexState

class TestAgentGeneration(unittest.TestCase):
    def setUp(self):
        self.coder = CoderAgent()
        self.coder.backend = MagicMock()
        self.auto_file = "agents/auto_spawned_securityauditor.py"

    def tearDown(self):
        if os.path.exists(self.auto_file):
            os.remove(self.auto_file)
        if "securityauditor" in registry._agents:
            del registry._agents["securityauditor"]

    def test_spawn_and_register_new_agent(self):
        """신규 에이전트 생성 및 레지스트리 자동 등록 통합 테스트"""
        proposal = {
            "agent_name": "SecurityAuditor",
            "role": "Security Specialist",
            "description": "Scans code for vulnerabilities",
            "required_tools": ["scan_file", "search_cve"],
            "logic_strategy": "Analyze AST for common security patterns."
        }
        
        # 1. 생성할 소스 코드 모킹 (v3.0 규격 완벽 준수)
        mock_code_content = r"""from gortex.agents.base import BaseAgent
from gortex.core.registry import AgentMetadata, registry
from typing import Dict, Any

class SecurityAuditorAgent(BaseAgent):
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="SecurityAuditor",
            role="Security Specialist",
            description="Generated Auditor",
            tools=["scan_file", "search_cve"],
            version="1.0.0"
        )
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"messages": [("ai", "Security scan complete.")], "next_node": "manager"}

# Registration
auditor_instance = SecurityAuditorAgent()
registry.register("SecurityAuditor", SecurityAuditorAgent, auditor_instance.metadata)
"""
        self.coder.backend.generate.return_value = f"""```python
{mock_code_content}
```"""
        
        # 2. 에이전트 스폰 실행
        res = self.coder.spawn_new_agent(proposal)
        
        # 3. 결과 검증
        self.assertEqual(res["status"], "success", f"Spawn failed: {res.get('reason')}")
        self.assertTrue(os.path.exists(self.auto_file))
        
        # 4. 레지스트리 등록 확인
        self.assertIn("securityauditor", registry.list_agents())
        
        # 5. 실행 능력 확인
        agent_class = registry.get_agent("securityauditor")
        self.assertIsNotNone(agent_class)
        instance = agent_class()
        state = {"messages": []}
        output = instance.run(state)
        self.assertIn("scan complete", output["messages"][0][1])

if __name__ == '__main__':
    unittest.main()