import re
from typing import List, Dict, Any
from backend.models.schemas import Citation


def extract_citations_from_results(retrieved_docs: List[Dict[str, Any]]) -> List[Citation]:
    """
    Build structured citations from retrieved document chunks.
    """
    citations = []
    seen = set()

    for item in retrieved_docs:
        page = item.get("page", 1)
        section = item.get("section", "")
        text = item.get("text", "")
        doc_name = item.get("document_name", "")
        score = item.get("score", 0.0)

        # Create brief excerpt (up to 180 chars)
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        excerpt = cleaned_text[:180] + ("..." if len(cleaned_text) > 180 else "")

        key = (page, section, excerpt[:50])
        if key not in seen:
            seen.add(key)
            citations.append(Citation(
                page=page,
                section=section,
                excerpt=excerpt,
                document_name=doc_name,
                score=score
            ))

    return citations


def format_citations_markdown(citations: List[Citation]) -> str:
    """
    Format citations into a clear markdown reference list.
    """
    if not citations:
        return "*No specific page citations found in retrieved evidence.*"

    lines = ["\n### 📑 Grounded Citations & Evidence:"]
    for idx, c in enumerate(citations, 1):
        sec_str = f" | Section: **{c.section}**" if c.section else ""
        doc_str = f" | Doc: `{c.document_name}`" if c.document_name else ""
        lines.append(f"{idx}. **Page {c.page}**{sec_str}{doc_str}")
        lines.append(f"   > *\"{c.excerpt}\"*")
    return "\n".join(lines)
