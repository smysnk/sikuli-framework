from __future__ import annotations

from adapters.sikuligo_backend import Region
from log.formatter import Formatter
from log.level import INFO


class _Tool:
    saved_paths: list[str] = []

    @classmethod
    def saveAsset(cls, source_path: str) -> str:
        cls.saved_paths.append(source_path)
        return "asset.png"


class _Screen:
    def __init__(self, capture_path: str) -> None:
        self.capture_path = capture_path
        self.calls: list[object] = []

    def capture_region(self, region) -> str:
        self.calls.append(region)
        return self.capture_path


class _Config:
    screenshot_level = INFO
    screen = None

    @classmethod
    def getScreenshotLoggingLevel(cls):
        return cls.screenshot_level

    @classmethod
    def getScreen(cls):
        return cls.screen


def test_formatter_uses_backend_capture_region(tmp_path):
    capture_path = tmp_path / "capture.png"
    capture_path.write_bytes(b"\x89PNG\r\n\x1a\n")

    screen = _Screen(str(capture_path))
    _Config.screen = screen
    _Tool.saved_paths = []

    Formatter.setTool(_Tool)
    Formatter.setConfig(_Config)
    Formatter.setDefaultLevel(INFO)

    region = Region(raw_region=object(), bounds=(10, 20, 30, 40))
    text = str(Formatter(region).setLogLevel(INFO))

    assert screen.calls == [region]
    assert _Tool.saved_paths[-1] == str(capture_path)
    assert "Actual" in text
