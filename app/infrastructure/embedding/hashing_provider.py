"""Small deterministic embedding adapter for local and Docker development.

This provider intentionally avoids model downloads. It preserves the production
embedding contract, but it is a lexical approximation rather than a trained
semantic model.
"""

from __future__ import annotations

import hashlib
import math
import re

TOKEN_PATTERN = re.compile(r"[\w]+", re.UNICODE)


class HashingEmbeddingProvider:
    def __init__(self, dimension: int) -> None:
        self._dimension = dimension

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def embed_document(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        tokens = TOKEN_PATTERN.findall(text.casefold())
        if not tokens:
            raise ValueError("cannot embed empty text")

        features = tokens + [
            f"{left}::{right}" for left, right in zip(tokens, tokens[1:])
        ]
        vector = [0.0] * self._dimension
        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=16).digest()
            index = int.from_bytes(digest[:8], "big") % self._dimension
            sign = 1.0 if digest[8] & 1 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector]
