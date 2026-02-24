from __future__ import annotations

from dataclasses import dataclass

import region.finder as finder_module
from region.finder import Finder


class _Formatter:
    def setLabel(self, *_args, **_kwargs):
        return self

    def showBaselines(self):
        return self

    def setLogLevel(self, *_args, **_kwargs):
        return self

    def __str__(self):
        return "fmt"


class _Logger:
    def trace(self, *_args, **_kwargs):
        return None

    def debug(self, *_args, **_kwargs):
        return None

    def info(self, *_args, **_kwargs):
        return None

    def warn(self, *_args, **_kwargs):
        return None

    def error(self, *_args, **_kwargs):
        return None

    def getFormatter(self):
        return lambda _entity: _Formatter()


class _IdentityTransform:
    CONTEXT_PREVIOUS = "PREVIOUS"
    CONTEXT_NEXT = "NEXT"
    CONTEXT_CURRENT = "CURRENT"
    CONTEXT_FINAL = "FINAL"
    CONTEXT_MATCH = "MATCH"
    CONTEXT_ENTITY = "ENTITY"

    def __init__(self, *_args, **_kwargs):
        pass

    def apply(self, operand, *_args, **_kwargs):
        return operand


class _PatternFake:
    def __init__(self, image: str):
        self.image = image

    @classmethod
    def from_image(cls, image: str):
        return cls(image)

    def __str__(self):
        return f"Pattern({self.image})"


@dataclass
class _FakeRegion:
    x: int = 0
    y: int = 0
    w: int = 100
    h: int = 100
    wait_timeout_millis: int | None = None
    wait_calls: int = 0

    def wait(self, _pattern, timeout_millis: int | None = None):
        self.wait_calls += 1
        self.wait_timeout_millis = timeout_millis
        return _FakeRegion(10, 20, 30, 40)

    def add(self, other):
        x1 = min(self.x, other.x)
        y1 = min(self.y, other.y)
        x2 = max(self.x + self.w, other.x + other.w)
        y2 = max(self.y + self.h, other.y + other.h)
        return _FakeRegion(x1, y1, x2 - x1, y2 - y1)

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getW(self):
        return self.w

    def getH(self):
        return self.h


class _EntityStub:
    def getCanonicalName(self, **_kwargs):
        return "Widget"

    def getClassName(self):
        return "Widget"

    @property
    def parent(self):
        return None

    def __str__(self):
        return "EntityStub"


class _ConfigStub:
    backend = "sikuligo"
    imageSuffix = ".png"
    regionTimeout = 2

    def __init__(self, image_root, screen_region):
        self.imageBaseline = str(image_root)
        self._screen_region = screen_region
        self.imageSearchPaths = [str(image_root)]

    def getScreen(self):
        return self._screen_region

    def getImageSearchPaths(self):
        return list(self.imageSearchPaths)


def test_finder_uses_adapter_wait_with_timeout_millis(tmp_path, monkeypatch):
    baseline_dir = tmp_path / "Widget"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    (baseline_dir / "Widget.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    search_region = _FakeRegion()
    cfg = _ConfigStub(tmp_path, search_region)

    Finder.setLogger(lambda _entity: _Logger())
    Finder.setConfig(cfg)
    Finder.setTransform(_IdentityTransform)
    monkeypatch.setattr(finder_module, "Pattern", _PatternFake)

    finder = Finder(_EntityStub())
    result = finder.find(timeout=1)

    assert result.getX() == 10
    assert result.getY() == 20
    assert result.getW() == 30
    assert result.getH() == 40
    assert search_region.wait_calls == 1
    assert search_region.wait_timeout_millis == 2000
