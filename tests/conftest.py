"""Shared test fixtures."""

import pytest

from app import create_app
from app.config.settings import Settings


@pytest.fixture()
def client():
    app = create_app(
        Settings(
            app_env="test",
            storage_backend="memory",
            database_url=None,
            embedding_dimension=64,
            default_search_threshold=0.0,
        )
    )
    app.config.update(TESTING=True)
    return app.test_client()
