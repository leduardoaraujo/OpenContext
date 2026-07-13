from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from opencontext.contracts import Document


def _parse(path: Path, root: Path) -> Document:
    text = path.read_text(encoding="utf-8-sig")
    metadata: dict[str, Any] = {}
    body = text
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        closing = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
        if closing is None:
            raise ValueError(f"Invalid frontmatter in {path}")
        parsed = yaml.safe_load("\n".join(lines[1:closing]))
        metadata = parsed if isinstance(parsed, dict) else {}
        body = "\n".join(lines[closing + 1 :])
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    title = next(
        (line[2:].strip() for line in body.splitlines() if line.startswith("# ")),
        path.stem,
    )
    return Document(
        relative_path=path.relative_to(root).as_posix(),
        title=title,
        body=body,
        metadata=metadata,
    )


def load_documents(root: Path) -> list[Document]:
    root = root.resolve()
    if not root.exists():
        return []
    return [_parse(path, root) for path in sorted(root.rglob("*.md"))]
