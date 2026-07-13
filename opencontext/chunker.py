from __future__ import annotations

import hashlib
import re

from opencontext.contracts import Chunk, Document

HEADER = re.compile(r"^(##|###)\s+(.+)$")


def _chunk_id(path: str, heading: str, content: str) -> str:
    return hashlib.sha1(f"{path}|{heading}|{content}".encode()).hexdigest()[:16]


def chunk_document(document: Document, max_chars: int = 1200) -> list[Chunk]:
    chunks: list[Chunk] = []
    h2 = document.title
    h3 = ""
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        content = "\n".join(buffer).strip()
        buffer = []
        if not content:
            return
        heading = h3 or h2
        heading_path = document.title if h2 == document.title else f"{document.title} > {h2}"
        if h3:
            heading_path = f"{heading_path} > {h3}"
        for offset in range(0, len(content), max_chars):
            part = content[offset : offset + max_chars].strip()
            if part:
                chunks.append(Chunk(
                    chunk_id=_chunk_id(document.relative_path, heading_path, part),
                    document_path=document.relative_path,
                    title=document.title,
                    heading=heading,
                    content=part,
                    metadata={**document.metadata, "heading_path": heading_path},
                ))

    for line in document.body.splitlines():
        if line.startswith("# "):
            continue
        match = HEADER.match(line.strip())
        if match:
            flush()
            level, title = match.groups()
            if level == "##":
                h2, h3 = title.strip(), ""
            else:
                h3 = title.strip()
        else:
            buffer.append(line)
    flush()
    return chunks or [Chunk(
        chunk_id=_chunk_id(document.relative_path, document.title, document.body),
        document_path=document.relative_path,
        title=document.title,
        heading=document.title,
        content=document.body or document.title,
        metadata=document.metadata,
    )]
