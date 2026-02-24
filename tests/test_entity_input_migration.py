from __future__ import annotations

from entity.clickStrategy import StandardClick
from entity.entities.clickableEntity import ClickableEntity
from entity.entities.textBox import TextBox


class _Point:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    def getX(self):
        return self._x

    def getY(self):
        return self._y


class _Region:
    def __init__(self, x: int = 10, y: int = 20):
        self._point = _Point(x, y)

    def getClickLocation(self):
        return self._point


class _Screen:
    def __init__(self):
        self.click_calls = []
        self.drag_calls = []
        self.type_calls = []

    def click_point(self, x, y, button="left"):
        self.click_calls.append((x, y, button))

    def drag_to(self, start, destination, button="left"):
        self.drag_calls.append((start, destination, button))

    def type_text(self, text):
        self.type_calls.append(text)


class _Config:
    backend = "sikuligo"

    def __init__(self, screen: _Screen):
        self._screen = screen

    def getScreen(self):
        return self._screen


class _Formatter:
    def __str__(self):
        return "fmt"


class _Logger:
    def info(self, *_args, **_kwargs):
        return None

    def warn(self, *_args, **_kwargs):
        return None

    def getFormatter(self):
        return lambda _entity: _Formatter()


def test_standard_click_uses_backend_click_point():
    screen = _Screen()
    StandardClick.setScreen(screen)
    strategy = StandardClick()

    class _Entity:
        def getRegion(self):
            return _Region(30, 40)

    strategy.click(_Entity())
    assert screen.click_calls == [(30, 40, "left")]


def test_clickable_entity_drag_uses_backend_drag_to():
    screen = _Screen()
    cfg = _Config(screen)

    entity = object.__new__(ClickableEntity)
    entity.config = cfg
    entity.region = _Region(5, 6)
    entity.LEFT_MOUSE = "left"
    entity.validate = lambda: None
    entity.invalidate_called = False

    def _invalidate(*_args, **_kwargs):
        entity.invalidate_called = True

    entity.invalidate = _invalidate

    ClickableEntity.drag(entity, destination=(50, 60))
    assert len(screen.drag_calls) == 1
    _, destination, button = screen.drag_calls[0]
    assert destination == (50, 60)
    assert button == "left"
    assert entity.invalidate_called is True


def test_textbox_type_uses_backend_click_and_type_text():
    screen = _Screen()
    cfg = _Config(screen)

    textbox = object.__new__(TextBox)
    textbox.config = cfg
    textbox.region = _Region(12, 34)
    textbox.parent = object()
    textbox.logger = _Logger()
    textbox.validate = lambda: None

    result = TextBox.type(textbox, "hello world", verify=True)

    assert result is textbox.parent
    assert screen.click_calls == [(12, 34, "left")]
    assert screen.type_calls == ["hello world"]
