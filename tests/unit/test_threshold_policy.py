from uuid import UUID

from app.domain.entities.search_result import SearchCandidate
from app.domain.services.threshold_policy import ThresholdPolicy


def candidate(score: float) -> SearchCandidate:
    return SearchCandidate(
        video_id=UUID(int=1),
        title="video",
        description="",
        tags=(),
        score=score,
    )


def test_score_above_threshold_is_kept():
    assert ThresholdPolicy().apply([candidate(0.8)], 0.7)


def test_score_below_threshold_is_removed():
    assert ThresholdPolicy().apply([candidate(0.6)], 0.7) == []


def test_threshold_boundary_is_accepted():
    assert ThresholdPolicy().apply([candidate(0.7)], 0.7)
