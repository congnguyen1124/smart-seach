"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    app_env: str = "development"
    embedding_provider: str = "hashing"
    embedding_model: str = "hashing-demo-v1"
    embedding_dimension: int = 384
    default_search_threshold: float = 0.15
    default_search_limit: int = 10
    max_search_limit: int = 50
    search_candidate_multiplier: int = 5

    def __post_init__(self) -> None:
        if self.embedding_provider not in {"hashing", "sentence_transformer"}:
            raise ValueError(
                "EMBEDDING_PROVIDER must be 'hashing' or 'sentence_transformer'"
            )
        if self.embedding_dimension < 8:
            raise ValueError("EMBEDDING_DIMENSION must be at least 8")
        if not -1.0 <= self.default_search_threshold <= 1.0:
            raise ValueError("DEFAULT_SEARCH_THRESHOLD must be between -1 and 1")
        if self.default_search_limit < 1:
            raise ValueError("DEFAULT_SEARCH_LIMIT must be positive")
        if self.max_search_limit < self.default_search_limit:
            raise ValueError("MAX_SEARCH_LIMIT must be at least DEFAULT_SEARCH_LIMIT")
        if self.search_candidate_multiplier < 1:
            raise ValueError("SEARCH_CANDIDATE_MULTIPLIER must be positive")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            embedding_provider=os.getenv("EMBEDDING_PROVIDER", "hashing"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "hashing-demo-v1"),
            embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "384")),
            default_search_threshold=float(
                os.getenv("DEFAULT_SEARCH_THRESHOLD", "0.15")
            ),
            default_search_limit=int(os.getenv("DEFAULT_SEARCH_LIMIT", "10")),
            max_search_limit=int(os.getenv("MAX_SEARCH_LIMIT", "50")),
            search_candidate_multiplier=int(
                os.getenv("SEARCH_CANDIDATE_MULTIPLIER", "5")
            ),
        )
