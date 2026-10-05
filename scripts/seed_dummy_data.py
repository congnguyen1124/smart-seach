"""Idempotently index dummy videos into the configured repository."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from uuid import UUID

from app.application.dto import IndexVideoRequest
from app.application.index_video import IndexVideoUseCase
from app.config.settings import Settings
from app.infrastructure.embedding.provider_factory import create_embedding_provider
from app.infrastructure.repositories.provider_factory import create_video_repository


def seed(source: Path) -> int:
    settings = Settings.from_env()
    embedding_provider = create_embedding_provider(settings)
    repository = create_video_repository(settings)
    repository.health_check()
    use_case = IndexVideoUseCase(
        embedding_provider=embedding_provider,
        repository=repository,
        model_name=settings.embedding_model,
    )

    records = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("dummy data must be a JSON array")

    for record in records:
        use_case.execute(
            IndexVideoRequest(
                video_id=UUID(record["id"]),
                title=record["title"],
                description=record.get("description", ""),
                tags=tuple(record.get("tags", ())),
            )
        )
    return len(records)


if __name__ == "__main__":
    source_path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/dummy_videos.json")
    count = seed(source_path)
    print(f"Seeded {count} videos from {source_path}")
