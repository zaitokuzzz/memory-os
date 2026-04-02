import json
from pathlib import Path
from uuid import UUID

from app.core.config import settings


class ArchiveService:
    def __init__(self) -> None:
        self.provider = settings.archive_provider
        self.base_path = Path("local_archive")
        self.base_path.mkdir(parents=True, exist_ok=True)

    def store(self, memory_id: UUID, payload: dict) -> str:
        file_path = self.base_path / f"{memory_id}.json"
        file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if self.provider == "local":
            return str(file_path)
        return f"archive://{memory_id}.json"

    def load(self, archive_uri: str) -> dict | None:
        if archive_uri.startswith("archive://"):
            filename = archive_uri.replace("archive://", "")
            path = self.base_path / filename
        else:
            path = Path(archive_uri)

        if not path.exists():
            return None

        return json.loads(path.read_text(encoding="utf-8"))
