"""Thread-safe in-memory adapter used until PostgreSQL is connected."""

from __future__ import annotations

import re
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
                    score=score,
                )
            )

        return sorted(
            candidates,
            key=lambda candidate: (-candidate.score, str(candidate.video_id)),
        )[:candidate_limit]

    def keyword_search(
        self, query: str, candidate_limit: int
    ) -> list[SearchCandidate]:
        query_terms = set(re.findall(r"[^\W_]+", query.casefold()))
        if not query_terms:
            return []

        with self._lock:
            snapshot = tuple(self._items.values())

        candidates: list[SearchCandidate] = []
        for item in snapshot:
            document = " ".join(
                (
                    item.video.title,
                    item.video.description,
                    " ".join(item.video.tags),
                )
            ).casefold()
            matched_terms = sum(term in document for term in query_terms)
            if matched_terms == 0:
                continue
            candidates.append(
                SearchCandidate(
                    video_id=item.video.id,
                    title=item.video.title,
                    description=item.video.description,
                    tags=item.video.tags,
                    score=matched_terms / len(query_terms),
                )
            )

        return sorted(
            candidates,
            key=lambda candidate: (-candidate.score, str(candidate.video_id)),
        )[:candidate_limit]
