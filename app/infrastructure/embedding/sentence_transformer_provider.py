"""Optional Sentence Transformers embedding adapter."""

from __future__ import annotations

from typing import Any


class SentenceTransformerEmbeddingProvider:
    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise RuntimeError(
                "sentence-transformers is not installed; install requirements-ml.txt"
            ) from error

        self._model: Any = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> list[float]:
        return self._encode(text)

    def embed_document(self, text: str) -> list[float]:
        return self._encode(text)

    def _encode(self, text: str) -> list[float]:
        vector = self._model.encode(text.strip(), normalize_embeddings=True)
        return vector.tolist()
