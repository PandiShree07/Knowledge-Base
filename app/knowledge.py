import re
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"


def parse_okf_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        return {"path": path, "metadata": {}, "body": raw.strip()}
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {"path": path, "metadata": {}, "body": raw.strip()}
    metadata = yaml.safe_load(parts[1]) or {}
    return {"path": path, "metadata": metadata, "body": parts[2].strip()}


def load_knowledge() -> list[dict]:
    return [parse_okf_file(path) for path in sorted(KNOWLEDGE_DIR.rglob("*.md"))]


def tokenize(value: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_]+", value.lower()))


def retrieve_documents(question: str, knowledge: list[dict], limit: int = 5) -> list[dict]:
    """Simple lexical retrieval for the bundled document collection; not vector RAG."""
    query_terms = tokenize(question)
    scored = []
    for item in knowledge:
        if "documents" not in item["path"].parts:
            continue
        meta = item["metadata"]
        searchable = " ".join([
            str(meta.get("title", "")),
            str(meta.get("description", "")),
            " ".join(meta.get("tags", []) or []),
            item["body"],
        ])
        terms = tokenize(searchable)
        score = len(query_terms & terms)
        title_terms = tokenize(
            str(meta.get("title", "")) + " " + " ".join(meta.get("tags", []) or [])
        )
        score += 2 * len(query_terms & title_terms)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:limit]]


def schema_context(knowledge: list[dict]) -> str:
    items = [item for item in knowledge if "schema" in item["path"].parts]
    return "\n\n".join(
        f"OKF schema concept: {item['metadata'].get('title', item['path'].stem)}\n{item['body']}"
        for item in items
    )
