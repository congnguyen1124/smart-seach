"""Build the configured embedding adapter."""

from app.config.settings import Settings
from app.domain.ports.embedding_provider import EmbeddingProvider
from app.infrastructure.embedding.hashing_provider import HashingEmbeddingProvider
from app.infrastructure.embedding.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "sentence_transformer":
        return SentenceTransformerEmbeddingProvider(settings.embedding_model)
    return HashingEmbeddingProvider(settings.embedding_dimension)
