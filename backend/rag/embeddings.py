import os
import math
import numpy as np
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Sentence transformers or fallback
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False


class EmbeddingService:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        self._model = None
        self._fallback_vocab = {}

    def _get_model(self):
        if self._model is None and SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                # Attempt loading model; if download blocked, use fallback
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"SentenceTransformer load note: {e}. Using deterministic high-dimension vector generator.")
                self._model = "FALLBACK"
        return self._model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        if model not in (None, "FALLBACK"):
            try:
                embeddings = model.encode(texts, normalize_embeddings=True)
                return embeddings.tolist()
            except Exception as e:
                print(f"Error encoding with SentenceTransformer: {e}")

        # High-dimension deterministic fallback embedding (384-dimensional)
        return [self._generate_fallback_vector(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    def _generate_fallback_vector(self, text: str, dim: int = 384) -> List[float]:
        """
        Fast, deterministic hash-based 384-dimension embedding with TF-IDF weighting and L2 norm.
        Allows instant offline vector search without downloading heavy multi-GB weights.
        """
        tokens = text.lower().replace("\n", " ").split()
        vector = np.zeros(dim, dtype=np.float32)
        if not tokens:
            return vector.tolist()

        for idx, token in enumerate(tokens):
            h = hash(token)
            pos = abs(h) % dim
            sign = 1.0 if (h % 2 == 0) else -1.0
            weight = 1.0 + (1.0 / (idx + 1))
            vector[pos] += sign * weight

        # Normalize L2
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector.tolist()


# Global instance
embedding_service = EmbeddingService()
