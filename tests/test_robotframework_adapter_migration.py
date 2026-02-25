from __future__ import annotations

import importlib.util
from pathlib import Path


_MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "robotframework" / "sikuliFwRfAbstractLib.py"
_SPEC = importlib.util.spec_from_file_location("sikuliFwRfAbstractLib", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
rf_module = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(rf_module)


def test_rf_library_imports_on_cpython_backend():
    lib = rf_module.SikuliFwRfAbstractLib()
    assert lib is not None


def test_rf_sleep_uses_python_time(monkeypatch):
    durations: list[float] = []
    monkeypatch.setattr(rf_module.time, "sleep", lambda value: durations.append(float(value)))

    lib = rf_module.SikuliFwRfAbstractLib()
    lib.sleep("1.5")

    assert durations == [1.5]


def test_rf_set_screenshot_log_level_accepts_info(monkeypatch):
    levels: list[int] = []
    monkeypatch.setattr(rf_module.Config, "setScreenshotLoggingLevel", lambda value: levels.append(value))

    lib = rf_module.SikuliFwRfAbstractLib()
    lib.setScreenshotLogLevel("info")

    assert levels == [rf_module.INFO]
