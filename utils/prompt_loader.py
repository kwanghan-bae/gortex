import yaml
import os
import logging
from typing import Dict, Any

logger = logging.getLogger("GortexPromptLoader")

class PromptLoader:
    """
    외부 YAML 파일로부터 에이전트 프롬프트 템플릿을 로드하고 관리함.
    """
    def __init__(self, prompt_dir: str = None):
        if prompt_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.prompt_dir = os.path.join(base_dir, "docs/prompts")
        else:
            self.prompt_dir = prompt_dir
        self.templates = self._load_all_templates()
        self.personas = self._load_personas()

    def _load_personas(self) -> Dict[str, Any]:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "docs/i18n/personas.json")
        if os.path.exists(path):
            try:
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _load_all_templates(self) -> Dict[str, Any]:
        all_templates = {}
        if not os.path.exists(self.prompt_dir):
            return {}
            
        for file in os.listdir(self.prompt_dir):
            if file.endswith(".yaml") or file.endswith(".yml"):
                path = os.path.join(self.prompt_dir, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data: all_templates.update(data)
                except Exception as e:
                    logger.error(f"Failed to load prompt file {file}: {e}")
        return all_templates

    def get(self, key: str, default: str = "") -> str:
        """YAML 템플릿 값 직접 조회 (단순 문자열 반환)"""
        return self.templates.get(key, default)

    def get_prompt(self, agent_id: str, persona_id: str = None, context_text: str = "", **kwargs) -> str:
        """지정된 에이전트의 프롬프트를 가져오고 페르소나 및 동적 규칙 주입"""
        template = self.templates.get(agent_id, {}).get("instruction", "")
        if not template:
            logger.warning(f"Prompt template for {agent_id} not found.")
            return ""
            
        # 1. 페르소나 지침 구성
        persona_header = ""
        if persona_id and persona_id in self.personas:
            p = self.personas[persona_id]
            persona_header = f"[ACTIVE PERSONA: {p['name']}]\n- Focus: {', '.join(p['focus'])}\n\n"

        # 2. 동적 정책(Dynamic Policy) 주입 (자가 진화된 지식)
        dynamic_policy = ""
        try:
            from gortex.core.evolutionary_memory import EvolutionaryMemory
            evo_mem = EvolutionaryMemory()
            rules = evo_mem.get_active_constraints(context_text or agent_id)
            if rules:
                dynamic_policy = "\n\n[USER-SPECIFIC EVOLVED POLICIES]\n" + "\n".join([f"- {r}" for r in rules])
        except: pass
        
        try:
            body = template.format(**kwargs)
            return persona_header + body + dynamic_policy
        except Exception:
            return persona_header + template + dynamic_policy

# 싱글톤 인스턴스 제공
loader = PromptLoader()