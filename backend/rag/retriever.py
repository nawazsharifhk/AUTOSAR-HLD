from typing import List, Dict, Any, Optional
from backend.rag.vector_store import vector_store
from backend.rag.citations import extract_citations_from_results
from backend.database.session import SessionLocal
from backend.models.db_models import DocumentChunkModel, DocumentModel


class AUTOSARRetriever:
    def __init__(self, collection_name: str = "autohld_default"):
        self.default_collection = collection_name

    def retrieve(
        self,
        query: str,
        document_id: Optional[int] = None,
        top_k: int = 5,
        collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant HLD chunks from ChromaDB, with automatic SQLite chunk fallback.
        """
        target_collection = collection_name or self.default_collection
        where_filter = {}
        if document_id is not None:
            where_filter["document_id"] = document_id

        # 1. Try vector store search on target collection
        raw_results = vector_store.search(
            collection_name=target_collection,
            query=query,
            top_k=top_k * 2,
            where=where_filter if where_filter else None
        )

        # 2. If no results found, search across all available Chroma collections or SQLite chunks
        if not raw_results:
            raw_results = self._retrieve_from_db_chunks(query, document_id, top_k * 2)

        if not raw_results:
            return {
                "context": "",
                "results": [],
                "citations": []
            }

        # 3. Rerank based on exact architectural keywords and token overlap
        query_words = set(query.lower().split())
        reranked = []
        for r in raw_results:
            text = r["text"].lower()
            keyword_score = sum(2.0 for w in query_words if len(w) > 2 and w in text)
            combined_score = r.get("score", 0.8) + (keyword_score * 0.15)
            r["combined_score"] = combined_score
            reranked.append(r)

        reranked.sort(key=lambda x: x["combined_score"], reverse=True)
        top_results = reranked[:top_k]

        # Format context text with page markers
        context_parts = []
        for res in top_results:
            page_hdr = f"--- [Document: {res.get('document_name', 'HLD')}, Page {res['page']}, Section: {res.get('section', 'N/A')}] ---"
            context_parts.append(f"{page_hdr}\n{res['text']}")

        full_context = "\n\n".join(context_parts)
        citations = extract_citations_from_results(top_results)

        return {
            "context": full_context,
            "results": top_results,
            "citations": citations
        }

    def _retrieve_from_db_chunks(self, query: str, document_id: Optional[int], top_k: int) -> List[Dict[str, Any]]:
        """
        Fallback keyword retrieval directly from SQLite document chunks.
        """
        db = SessionLocal()
        try:
            q = db.query(DocumentChunkModel, DocumentModel.name.label("doc_name")).join(
                DocumentModel, DocumentChunkModel.document_id == DocumentModel.id
            )
            if document_id is not None:
                q = q.filter(DocumentChunkModel.document_id == document_id)

            all_chunks = q.all()
            if not all_chunks:
                return []

            query_tokens = [t.lower() for t in query.split() if len(t) > 2]
            scored_chunks = []

            for chunk, doc_name in all_chunks:
                text_lower = chunk.text.lower()
                matches = sum(1 for tok in query_tokens if tok in text_lower)
                score = 0.6 + min(0.35, matches * 0.1)
                if matches > 0 or not query_tokens:
                    scored_chunks.append({
                        "text": chunk.text,
                        "page": chunk.page,
                        "section": chunk.section or f"Page {chunk.page}",
                        "component": chunk.component or "General",
                        "document_name": doc_name,
                        "document_id": chunk.document_id,
                        "score": round(score, 4)
                    })

            scored_chunks.sort(key=lambda x: x["score"], reverse=True)
            return scored_chunks[:top_k]
        except Exception as e:
            print(f"DB chunk retrieval error: {e}")
            return []
        finally:
            db.close()


retriever = AUTOSARRetriever()
