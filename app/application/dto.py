"""Application-layer data transfer objects."""

from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.search_result import SearchResult


@dataclass(frozen=True, slots=True)
class SearchRequest:
    query: str
    limit: int
    threshold: float
    mode: str = "semantic"


@dataclass(frozen=True, slots=True)
class SearchResponse:
    query: str
    threshold: float
    mode: str
    items: tuple[SearchResult, ...]


@dataclass(frozen=True, slots=True)
class IndexVideoRequest:
    video_id: UUID
    title: str
    description: str
    tags: tuple[str, ...]
