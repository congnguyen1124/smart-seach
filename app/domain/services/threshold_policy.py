"""Semantic-score threshold policy."""

from app.domain.entities.search_result import SearchCandidate


class ThresholdPolicy:
    def apply(
        self, candidates: list[SearchCandidate], threshold: float
    ) -> list[SearchCandidate]:
        return [
            candidate
            for candidate in candidates
            if candidate.semantic_score >= threshold
        ]
