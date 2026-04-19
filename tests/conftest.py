from __future__ import annotations

import os
from pathlib import Path
import random
import shutil

import pytest

def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _binary_candidates() -> list[Path]:
    path = Path(__file__).resolve()
    candidates = []
    for index in range(2, min(len(path.parents), 5)):
        root = path.parents[index]
        candidates.append(root / "sikuligo")
        candidates.append(root / "sikuli-go")

    for binary_name in ("sikuligo", "sikuli-go"):
        resolved = shutil.which(binary_name)
        if resolved:
            candidates.append(Path(resolved).resolve())
    return candidates


@pytest.fixture(scope="session")
def sikuligo_binary() -> Path:
    env = os.getenv("SIKULIGO_BINARY_PATH", "").strip()
    if env:
        candidate = Path(env).expanduser().resolve()
        if candidate.exists():
            return candidate
    for candidate in _binary_candidates():
        if candidate.exists():
            return candidate
    return _workspace_root() / "sikuligo"


@pytest.fixture()
def free_port() -> int:
    return random.randint(50000, 59000)
