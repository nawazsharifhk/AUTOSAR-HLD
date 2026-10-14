import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from backend.rag.embeddings import embedding_service

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class VectorStoreManager:
    def __init__(self, persist_dir: str = CHROMA_PERSIST_DIR):
        self.persist_dir = persist_dir
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        self._client = None
        self._fallback_store: Dict[str, List[Dict[str, Any]]] = {}

    def get_client(self):
        if self._client is None and CHROMA_AVAILABLE:
            try:
                self._client = chromadb.PersistentClient(path=self.persist_dir)
            except Exception as e:
                print(f"ChromaDB client init note: {e}")
        return self._client

    def get_or_create_collection(self, collection_name: str = "autohld_default"):
        # Sanitize collection name (alphanumeric and underscores)
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in collection_name)
        if len(safe_name) < 3:
            safe_name = f"col_{safe_name}"

        client = self.get_client()
        if client:
            try:
                return client.get_or_create_collection(name=safe_name)
            except Exception as e:
                print(f"Error getting ChromaDB collection: {e}")

        # Fallback memory store
        if safe_name not in self._fallback_store:
            self._fallback_store[safe_name] = []
        return safe_name

    def add_chunks(self, collection_name: str, chunks: List[Dict[str, Any]], document_id: int, document_name: str) -> List[str]:
        """
        Embed and persist document chunks into ChromaDB.
        """
        texts = [c["text"] for c in chunks]
        embeddings = embedding_service.embed_documents(texts)
        ids = [f"doc_{document_id}_chunk_{idx}" for idx in range(len(chunks))]
        metadatas = [
            {
                "document_id": document_id,
                "document_name": document_name,
                "page": c["page"],
                "section": c.get("section", ""),
                "component": c.get("component", "General")
            }
            for c in chunks
        ]

        client = self.get_client()
        if client:
            try:
                collection = client.get_or_create_collection(name=collection_name)
                # Upsert chunks
                collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas
                )
                return ids
            except Exception as e:
                print(f"Chroma add_chunks fallback note: {e}")

        # Fallback in-memory / local storage
        if collection_name not in self._fallback_store:
            self._fallback_store[collection_name] = []

        for i, (cid, emb, txt, meta) in enumerate(zip(ids, embeddings, texts, metadatas)):
            self._fallback_store[collection_name].append({
                "id": cid,
                "embedding": emb,
                "document": txt,
                "metadata": meta
            })

        return ids

    def search(self, collection_name: str, query: str, top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search vector store for most relevant chunks matching query.
        """
        query_embedding = embedding_service.embed_query(query)
        client = self.get_client()

        if client:
            try:
                collection = client.get_or_create_collection(name=collection_name)
                kwargs = {
                    "query_embeddings": [query_embedding],
                    "n_results": top_k
                }
                if where:
                    kwargs["where"] = where

                results = collection.query(**kwargs)
                formatted = []
                if results and results.get("documents") and len(results["documents"]) > 0:
                    docs = results["documents"][0]
                    metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
                    distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

                    for d, m, dist in zip(docs, metas, distances):
                        # Convert distance to similarity score
                        score = max(0.0, 1.0 - (dist / 2.0)) if dist is not None else 0.8
                        formatted.append({
                            "text": d,
                            "page": m.get("page", 1),
                            "section": m.get("section", ""),
                            "component": m.get("component", ""),
                            "document_name": m.get("document_name", ""),
                            "document_id": m.get("document_id", 0),
                            "score": round(score, 4)
                        })
                return formatted
            except Exception as e:
                print(f"Chroma query fallback note: {e}")

        # Fallback cosine search
        import numpy as np
        stored = self._fallback_store.get(collection_name, [])
        if not stored:
            return []

        scored = []
        q_vec = np.array(query_embedding, dtype=np.float32)
        for item in stored:
            if where and "document_id" in where:
                if item["metadata"].get("document_id") != where["document_id"]:
                    continue
            d_vec = np.array(item["embedding"], dtype=np.float32)
            cosine = float(np.dot(q_vec, d_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(d_vec) + 1e-8))
            meta = item["metadata"]
            scored.append({
                "text": item["document"],
                "page": meta.get("page", 1),
                "section": meta.get("section", ""),
                "component": meta.get("component", ""),
                "document_name": meta.get("document_name", ""),
                "document_id": meta.get("document_id", 0),
                "score": round(cosine, 4)
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def delete_document_chunks(self, collection_name: str, document_id: int):
        client = self.get_client()
        if client:
            try:
                collection = client.get_or_create_collection(name=collection_name)
                collection.delete(where={"document_id": document_id})
            except Exception as e:
                print(f"Delete chunks note: {e}")

        if collection_name in self._fallback_store:
            self._fallback_store[collection_name] = [
                x for x in self._fallback_store[collection_name] if x["metadata"].get("document_id") != document_id
            ]


vector_store = VectorStoreManager()
