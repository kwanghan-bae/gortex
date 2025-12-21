import yaml
import os
import logging
from typing import Dict, Any

logger = logging.getLogger("GortexPromptLoader")

class PromptLoader:
    """
    외부 YAML 파일로부터 에이전트 프롬프트 템플릿을 로드하고 관리함.
    """
    def __init__(self, prompt_dir: str = "docs/prompts"):
        self.prompt_dir = prompt_dir
        self.templates = self._load_all_templates()

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

    def get_prompt(self, agent_id: str, **kwargs) -> str:
        """지정된 에이전트의 프롬프트를 가져오고 변수 치환 수행"""
        template = self.templates.get(agent_id, {}).get("instruction", "")
        if not template:
            logger.warning(f"Prompt template for {agent_id} not found.")
            return ""
            
        try:
            # 전달된 인자들을 템플릿에 적용
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing required variable {e} for prompt {agent_id}")
            return template # 실패 시 원문 반환
        except Exception as e:
            return template

# 싱글톤 인스턴스 제공
loader = PromptLoader()
