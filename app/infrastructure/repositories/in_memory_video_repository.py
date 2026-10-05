"""Thread-safe in-memory adapter used until PostgreSQL is connected."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from uuid import UUID

from app.domain.entities.search_result import SearchCandidate
from app.domain.entities.video import Video


@dataclass(frozen=True, slots=True)
class _IndexedVideo:
    video: Video
    embedding: tuple[float, ...]
    model_name: str


class InMemoryVideoRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, _IndexedVideo] = {}
        self._lock = RLock()

    @property
    def backend_name(self) -> str:
        return "in-memory"

    def health_check(self) -> None:
        return None

    def upsert(
        self, video: Video, embedding: list[float], model_name: str
    ) -> None:
        indexed_video = _IndexedVideo(video, tuple(embedding), model_name)
        with self._lock:
            self._items[video.id] = indexed_video

    def get(self, video_id: UUID) -> Video | None:
        with self._lock:
            item = self._items.get(video_id)
        return item.video if item else None

    def semantic_search(
        self, query_vector: list[float], candidate_limit: int
    ) -> list[SearchCandidate]:
        with self._lock:
            snapshot = tuple(self._items.values())

        candidates: list[SearchCandidate] = []
        for item in snapshot:
            if len(item.embedding) != len(query_vector):
                raise ValueError("query and document embedding dimensions do not match")
            score = sum(
                query_value * document_value
                for query_value, document_value in zip(
                    query_vector, item.embedding, strict=True
                )
            )
            candidates.append(
                SearchCandidate(
                    video_id=item.video.id,
                    title=item.video.title,
                    description=item.video.description,
                    tags=item.video.tags,
                    cosine_distance=1.0 - score,
                    semantic_score=score,
                )
            )

        return sorted(
            candidates,
            key=lambda candidate: (
                candidate.cosine_distance,
                str(candidate.video_id),
            ),
        )[:candidate_limit]
