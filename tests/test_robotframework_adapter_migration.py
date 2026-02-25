from __future__ import annotations

import importlib.util
from pathlib import Path


_MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "robotframework" / "sikuliFwRfAbstractLib.py"
_SPEC = importlib.util.spec_from_file_location("sikuliFwRfAbstractLib", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
rf_module = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(rf_module)


class _LogStub:
    def info(self, *_args, **_kwargs):
        return None

    def warn(self, *_args, **_kwargs):
        return None

    def error(self, *_args, **_kwargs):
        return None

    def getFormatter(self):
        return lambda _entity: _entity


class _Node:
    def __init__(self, name: str):
        self.name = name
        self.children: dict[str, "_Node"] = {}
        self.validations = 0
        self.clicks = 0
        self.typed: list[str] = []
        self.wait_appear_calls: list[dict[str, object]] = []
        self.wait_vanish_calls: list[dict[str, object]] = []

    def __getitem__(self, key: str):
        return self.children[str(key)]

    def validate(self):
        self.validations += 1
        return self

    def click(self):
        self.clicks += 1
        return self

    def type(self, text):
        self.typed.append(str(text))
        return self

    def waitUntilAppears(self, **kwargs):
        self.wait_appear_calls.append(kwargs)
        return self

    def waitUntilVanish(self, **kwargs):
        self.wait_vanish_calls.append(kwargs)
        return self

    def __str__(self):
        return f"Node({self.name})"


def _new_lib(root: _Node):
    lib = rf_module.SikuliFwRfAbstractLib()
    lib.entity = root
    lib.logger = _LogStub()
    return lib


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


def test_rf_validate_select_click_type_waits_use_adapter_style_entities(monkeypatch):
    root = _Node("root")
    window = _Node("window")
    button = _Node("button")
    textbox = _Node("textbox")
    root.children["window"] = window
    window.children["button"] = button
    window.children["textbox"] = textbox

    lib = _new_lib(root)

    # validate walks + validates each selected node
    key_validate = lib.validate("window", "button")
    resolved_validate = lib.retrieve(key_validate)
    assert resolved_validate is button
    assert window.validations == 1
    assert button.validations == 1

    # select walks without validation
    key_select = lib.select("window", "textbox")
    resolved_select = lib.retrieve(key_select)
    assert resolved_select is textbox

    # click delegates to ClickableEntity-compatible nodes
    monkeypatch.setattr(rf_module, "ClickableEntity", _Node)
    key_click = lib.click("window", "button")
    resolved_click = lib.retrieve(key_click)
    assert resolved_click is button
    assert button.clicks == 1

    # type delegates to context.type
    key_type = lib.type("hello world", "window", "textbox")
    resolved_type = lib.retrieve(key_type)
    assert resolved_type is textbox
    assert textbox.typed == ["hello world"]

    # wait keywords route timeout in kwargs
    key_appear = lib.waitUntilAppears("window", timeout=3)
    resolved_appear = lib.retrieve(key_appear)
    assert resolved_appear is window
    assert window.wait_appear_calls == [{"timeout": 3}]

    key_vanish = lib.waitUntilVanish("window", timeout=2)
    resolved_vanish = lib.retrieve(key_vanish)
    assert resolved_vanish is window
    assert window.wait_vanish_calls == [{"timeout": 2}]
