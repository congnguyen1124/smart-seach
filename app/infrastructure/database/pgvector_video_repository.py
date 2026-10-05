"""PostgreSQL + pgvector implementation of the video repository port."""

from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from psycopg import Connection
from psycopg.rows import dict_row

from app.domain.entities.search_result import SearchCandidate
from app.domain.entities.video import Video


class PgVectorVideoRepository:
    def __init__(
        self,
        database_url: str,
        embedding_dimension: int,
        connect_timeout_seconds: int = 5,
    ) -> None:
        self._database_url = database_url
        self._embedding_dimension = embedding_dimension
        self._connect_timeout_seconds = connect_timeout_seconds

    @property
    def backend_name(self) -> str:
        return "postgresql+pgvector"

    @contextmanager
    def _connection(self) -> Iterator[Connection]:
        with psycopg.connect(
            self._database_url,
            connect_timeout=self._connect_timeout_seconds,
            row_factory=dict_row,
        ) as connection:
            register_vector(connection)
            yield connection

    def health_check(self) -> None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT
                    current_setting('server_version') AS server_version,
                    (
                        SELECT extversion
                        FROM pg_extension
                        WHERE extname = 'vector'
                    ) AS vector_version,
                    (
                        SELECT format_type(attribute.atttypid, attribute.atttypmod)
                        FROM pg_attribute AS attribute
                        WHERE attribute.attrelid = 'video_embeddings'::regclass
                          AND attribute.attname = 'embedding'
                          AND NOT attribute.attisdropped
                    ) AS embedding_type
                """
            ).fetchone()

        expected_type = f"vector({self._embedding_dimension})"
        if row is None or row["vector_version"] is None:
            raise RuntimeError("pgvector extension is not installed")
        if row["embedding_type"] != expected_type:
            raise RuntimeError(
                "database embedding dimension does not match application settings"
            )

    def upsert(
        self, video: Video, embedding: list[float], model_name: str
    ) -> None:
        self._validate_embedding(embedding)
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO videos (id, title, description, tags)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    tags = EXCLUDED.tags,
                    updated_at = NOW()
                """,
                (video.id, video.title, video.description, list(video.tags)),
            )
            connection.execute(
                """
                INSERT INTO video_embeddings (video_id, embedding, model_name)
                VALUES (%s, %s, %s)
                ON CONFLICT (video_id) DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    model_name = EXCLUDED.model_name,
                    updated_at = NOW()
                """,
                (video.id, Vector(embedding), model_name),
            )

    def get(self, video_id: UUID) -> Video | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT id, title, description, tags
                FROM videos
                WHERE id = %s
                """,
                (video_id,),
            ).fetchone()

        if row is None:
            return None
        return Video(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            tags=tuple(row["tags"] or ()),
        )

    def semantic_search(
        self, query_vector: list[float], candidate_limit: int
    ) -> list[SearchCandidate]:
        self._validate_embedding(query_vector)
        vector = Vector(query_vector)
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    video.id,
                    video.title,
                    video.description,
                    video.tags,
                    embedding.embedding <=> %s AS cosine_distance
                FROM video_embeddings AS embedding
                JOIN videos AS video ON video.id = embedding.video_id
                ORDER BY embedding.embedding <=> %s
                LIMIT %s
                """,
                (vector, vector, candidate_limit),
            ).fetchall()

        return [
            SearchCandidate(
                video_id=row["id"],
                title=row["title"],
                description=row["description"] or "",
                tags=tuple(row["tags"] or ()),
                score=1.0 - float(row["cosine_distance"]),
            )
            for row in rows
        ]

    def keyword_search(
        self, query: str, candidate_limit: int
    ) -> list[SearchCandidate]:
        query_terms = sorted(set(re.findall(r"[^\W_]+", query.casefold())))
        if not query_terms:
            return []

        with self._connection() as connection:
            rows = connection.execute(
                """
                WITH query_terms AS (
                    SELECT UNNEST(%s::text[]) AS term
                ), ranked AS (
                    SELECT
                        video.id,
                        video.title,
                        video.description,
                        video.tags,
                        SUM(
                            CASE
                                WHEN STRPOS(
                                    LOWER(CONCAT_WS(
                                        ' ',
                                        video.title,
                                        video.description,
                                        ARRAY_TO_STRING(video.tags, ' ')
                                    )),
                                    query_terms.term
                                ) > 0 THEN 1
                                ELSE 0
                            END
                        )::double precision / COUNT(*) AS score
                    FROM videos AS video
                    CROSS JOIN query_terms
                    GROUP BY video.id, video.title, video.description, video.tags
                )
                SELECT id, title, description, tags, score
                FROM ranked
                WHERE score > 0
                ORDER BY score DESC, id
                LIMIT %s
                """,
                (query_terms, candidate_limit),
            ).fetchall()

        return [
            SearchCandidate(
                video_id=row["id"],
                title=row["title"],
                description=row["description"] or "",
                tags=tuple(row["tags"] or ()),
                score=float(row["score"]),
            )
            for row in rows
        ]

    def _validate_embedding(self, embedding: list[float]) -> None:
        if len(embedding) != self._embedding_dimension:
            raise ValueError(
                f"expected embedding dimension {self._embedding_dimension}, "
                f"received {len(embedding)}"
            )
