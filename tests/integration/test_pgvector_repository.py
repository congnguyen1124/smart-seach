"""Database integration tests enabled by TEST_DATABASE_URL."""

from __future__ import annotations

import os
from uuid import uuid4

import psycopg
import pytest

from app import create_app
from app.config.settings import Settings

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL is required for pgvector integration tests",
)


def test_api_data_persists_across_application_instances():
    assert TEST_DATABASE_URL is not None
    video_id = uuid4()
    settings = Settings(
        app_env="test",
        storage_backend="postgres",
        database_url=TEST_DATABASE_URL,
        embedding_dimension=768,
        default_search_threshold=0.0,
    )

    try:
        first_app = create_app(settings)
        first_app.config.update(TESTING=True)
        index_response = first_app.test_client().post(
            "/api/v1/videos/index",
            json={
                "id": str(video_id),
                "title": "Persistent Flutter Architecture",
                "description": "PostgreSQL pgvector integration test",
                "tags": ["flutter", "postgresql", "pgvector"],
            },
        )
        assert index_response.status_code == 201

        second_app = create_app(settings)
        second_app.config.update(TESTING=True)
        second_client = second_app.test_client()

        persisted_response = second_client.get(f"/api/v1/videos/{video_id}")
        assert persisted_response.status_code == 200
        assert persisted_response.get_json()["title"] == (
            "Persistent Flutter Architecture"
        )

        search_response = second_client.post(
            "/api/v1/search",
            json={"query": "flutter postgresql pgvector", "threshold": 0.0},
        )
        assert search_response.status_code == 200
        ids = {item["id"] for item in search_response.get_json()["items"]}
        assert str(video_id) in ids
    finally:
        with psycopg.connect(TEST_DATABASE_URL) as connection:
            connection.execute("DELETE FROM videos WHERE id = %s", (video_id,))
