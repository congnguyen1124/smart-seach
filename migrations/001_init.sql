CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    tags TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS video_embeddings (
    video_id UUID PRIMARY KEY REFERENCES videos(id) ON DELETE CASCADE,
    embedding VECTOR(768) NOT NULL,
    model_name TEXT NOT NULL,
    content_hash TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS video_embeddings_hnsw_idx
ON video_embeddings
USING hnsw (embedding vector_cosine_ops);
