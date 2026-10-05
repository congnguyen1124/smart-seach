"""Search-related domain values."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SearchCandidate:
    video_id: UUID
    title: str
    description: str
    tags: tuple[str, ...]
    cosine_distance: float
    semantic_score: float


@dataclass(frozen=True, slots=True)
class SearchResult:
    video_id: UUID
    title: str
    description: str
    tags: tuple[str, ...]
    score: float
