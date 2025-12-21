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

    def get_prompt(self, agent_id: str, persona_id: str = None, **kwargs) -> str:
        """지정된 에이전트의 프롬프트를 가져오고 페르소나 주입 및 변수 치환 수행"""
        template = self.templates.get(agent_id, {}).get("instruction", "")
        if not template:
            logger.warning(f"Prompt template for {agent_id} not found.")
            return ""
            
        # 페르소나 지침 구성
        persona_header = ""
        if persona_id and persona_id in self.personas:
            p = self.personas[persona_id]
            persona_header = f"""[ACTIVE PERSONA: {p['name']}]
- Description: {p['description']}
- Traits: {', '.join(p['traits'])}
- Focus Areas: {', '.join(p['focus'])}
- Instructions: 위 성격과 집중 분야를 반영하여 사고하고 행동하라.

"""
        
        try:
            # 전달된 인자들을 템플릿에 적용
            body = template.format(**kwargs)
            return persona_header + body
        except KeyError as e:
            logger.error(f"Missing required variable {e} for prompt {agent_id}")
            return persona_header + template # 실패 시 원문 반환
        except Exception as e:
            return persona_header + template

# 싱글톤 인스턴스 제공
loader = PromptLoader()
