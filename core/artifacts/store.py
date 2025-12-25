
import os
import json
import shutil
from typing import Optional
from .base import BaseArtifact

class FileSystemArtifactStore:
    """로컬 파일 시스템에 Artifact를 영구 저장하는 저장소"""
    
    def __init__(self, base_path: str = "brain"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        self.artifacts_dir = os.path.join(self.base_path, "artifacts")
        os.makedirs(self.artifacts_dir, exist_ok=True)

    def save(self, artifact: BaseArtifact) -> str:
        """Artifact를 파일로 저장하고 경로를 반환합니다.
        파일 포맷: {id}.json (메타데이터 + 콘텐츠 포함)이 가장 확실하나,
        사용자 가독성을 위해 {id}.md로 저장하되 메타데이터는 주석이나 Frontmatter 처리하는 것이 이상적.
        여기서는 단순화를 위해 JSON으로 직렬화하여 저장합니다.
        (추후 Markdown 렌더링 지원 시 변경 가능)
        """
        file_path = os.path.join(self.artifacts_dir, f"{artifact.id}.json")
        
        # 버전 관리: 기존 파일이 있다면 백업
        if os.path.exists(file_path):
            backup_dir = os.path.join(self.base_path, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            shutil.copy2(file_path, os.path.join(backup_dir, f"{artifact.id}.bak"))

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(artifact.to_dict(), f, indent=4, ensure_ascii=False)
            
        return file_path

    def load(self, artifact_id: str) -> Optional[BaseArtifact]:
        """ID로 Artifact를 로드합니다."""
        file_path = os.path.join(self.artifacts_dir, f"{artifact_id}.json")
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return BaseArtifact.from_dict(data)
        except Exception:
            return None
