"""Video domain entity."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Video:
    id: UUID
    title: str
    description: str
    tags: tuple[str, ...]
