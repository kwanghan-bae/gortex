
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class BaseArtifact:
    """Gortex 시스템의 기본 산출물(Artifact) 정의"""
    id: str  # 고유 식별자 (예: art-20231225-001)
    type: str # 유형 (plan, code, report, other)
    title: str # 사용자에게 보여질 제목
    content: str # 본문 내용 (Markdown/Code)
    metadata: Dict[str, Any] = field(default_factory=dict) # 부가 정보 (생성시간, 저자 등)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseArtifact':
        return cls(
            id=data["id"],
            type=data.get("type", "other"),
            title=data.get("title", "Untitled"),
            content=data.get("content", ""),
            metadata=data.get("metadata", {})
        )
