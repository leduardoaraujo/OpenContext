from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel


class OpenContextSettings(BaseModel):
    project_root: Path
    knowledge_root: Path
    db_path: Path
    embedding_dimension: int = 256
    api_title: str = "OpenContext API"

    @classmethod
    def from_env(cls, project_root: Path | None = None) -> OpenContextSettings:
        root = (project_root or Path.cwd()).resolve()
        knowledge = Path(os.getenv("OPENCONTEXT_KNOWLEDGE_ROOT", "examples/knowledge"))
        db = Path(os.getenv("OPENCONTEXT_DB_PATH", ".opencontext/index.sqlite3"))
        return cls(
            project_root=root,
            knowledge_root=(root / knowledge).resolve()
            if not knowledge.is_absolute()
            else knowledge,
            db_path=(root / db).resolve() if not db.is_absolute() else db,
            embedding_dimension=int(os.getenv("OPENCONTEXT_EMBEDDING_DIMENSION", "256")),
        )
