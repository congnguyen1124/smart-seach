"""Deterministic semantic ranking."""

from app.domain.entities.search_result import SearchCandidate


class RankingService:
    def rank(self, candidates: list[SearchCandidate]) -> list[SearchCandidate]:
        return sorted(
            candidates,
            key=lambda item: (-item.score, str(item.video_id)),
        )
