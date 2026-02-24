from __future__ import annotations

import os
from pathlib import Path
import random

import pytest


# Run migration tests against the new backend path by default.
os.environ.setdefault("SIKULI_FRAMEWORK_BACKEND", "sikuligo")


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def sikuligo_binary() -> Path:
    env = os.getenv("SIKULIGO_BINARY_PATH", "").strip()
    if env:
        candidate = Path(env).expanduser().resolve()
        if candidate.exists():
            return candidate
    candidate = _workspace_root() / "sikuligo"
    return candidate


@pytest.fixture()
def free_port() -> int:
    return random.randint(50000, 59000)
