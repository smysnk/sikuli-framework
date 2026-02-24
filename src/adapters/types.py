"""
Backend adapter contracts used by the migration path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class BackendError(RuntimeError):
    pass


@dataclass(frozen=True)
class BackendMatch:
    x: int
    y: int
    w: int
    h: int
    target_x: int
    target_y: int
    score: float
    index: int = 0

    @staticmethod
    def from_raw(raw) -> "BackendMatch":
        return BackendMatch(
            x=int(getattr(raw, "x")),
            y=int(getattr(raw, "y")),
            w=int(getattr(raw, "w")),
            h=int(getattr(raw, "h")),
            target_x=int(getattr(raw, "target_x")),
            target_y=int(getattr(raw, "target_y")),
            score=float(getattr(raw, "score")),
            index=int(getattr(raw, "index", 0)),
        )


class BackendPattern(Protocol):
    def similar(self, similarity: float) -> "BackendPattern":
        ...

    def exact(self) -> "BackendPattern":
        ...

    def target_offset(self, dx: int, dy: int) -> "BackendPattern":
        ...

    def resize(self, factor: float) -> "BackendPattern":
        ...


class BackendRegion(Protocol):
    def find(self, pattern: BackendPattern, timeout_millis: int | None = None):
        ...

    def exists(self, pattern: BackendPattern, timeout_millis: int = 0):
        ...

    def wait(self, pattern: BackendPattern, timeout_millis: int = 3000):
        ...

    def click(self, pattern: BackendPattern, timeout_millis: int | None = None):
        ...


class BackendScreen(BackendRegion, Protocol):
    @classmethod
    def auto(cls, **kwargs) -> "BackendScreen":
        ...

    @classmethod
    def connect(cls, **kwargs) -> "BackendScreen":
        ...

    @classmethod
    def spawn(cls, **kwargs) -> "BackendScreen":
        ...

    def region(self, x: int, y: int, w: int, h: int) -> BackendRegion:
        ...

    def close(self) -> None:
        ...
