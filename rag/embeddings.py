"""Embeddings module for RAG pipeline"""
import os
import hashlib
from typing import List, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


class EmbeddingModel:
    """Wrapper for sentence transformer embeddings with fallback"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: Optional[str] = None):
        self.model_name = model_name
        self.cache_dir = cache_dir
        self._model = None
        self._dimension = 384  # all-MiniLM-L6-v2 dimension
        self._use_fallback = not SENTENCE_TRANSFORMERS_AVAILABLE

    @property
    def model(self):
        if self._model is None and not self._use_fallback:
            try:
                self._model = SentenceTransformer(self.model_name, cache_folder=self.cache_dir)
            except Exception:
                self._use_fallback = True
        return self._model

    @property
    def dimension(self) -> int:
        return self._dimension

    def encode(self, texts: List[str], show_progress_bar: bool = False) -> np.ndarray:
        """Encode texts to embeddings"""
        if self._use_fallback or self.model is None:
            return self._fallback_encode(texts)

        try:
            embeddings = self.model.encode(texts, show_progress_bar=show_progress_bar, convert_to_numpy=True)
            return embeddings.astype(np.float32)
        except Exception:
            return self._fallback_encode(texts)

    def _fallback_encode(self, texts: List[str]) -> np.ndarray:
        """Simple hash-based fallback embeddings for demo mode"""
        embeddings = []
        for text in texts:
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            vec = np.frombuffer(hash_bytes, dtype=np.uint8).astype(np.float32)
            vec = np.tile(vec, self._dimension // len(vec) + 1)[:self._dimension]
            vec = vec / (np.linalg.norm(vec) + 1e-8)
            embeddings.append(vec)
        return np.array(embeddings, dtype=np.float32)

    def encode_single(self, text: str) -> np.ndarray:
        """Encode single text"""
        return self.encode([text])[0]


def get_embedding_model(model_name: str = "all-MiniLM-L6-v2", cache_dir: Optional[str] = None) -> EmbeddingModel:
    """Factory function to get embedding model"""
    return EmbeddingModel(model_name, cache_dir)