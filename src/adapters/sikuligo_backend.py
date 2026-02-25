"""
SikuliGO-backed adapter implementation.

This module provides legacy-friendly compatibility primitives used during
framework migration (`Screen`, `Region`, `Pattern`, `Location`).
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Iterable

try:
    from sikuligo import Pattern as SikuligoPattern
    from sikuligo import Screen as SikuligoScreen
    from sikuligo import SikuliError
except ImportError:  # pragma: no cover - optional runtime dependency
    SikuligoPattern = None
    SikuligoScreen = None
    SikuliError = RuntimeError

try:
    from generated.sikuli.v1 import sikuli_pb2 as pb
except ImportError:  # pragma: no cover - optional runtime dependency
    pb = None

from .types import BackendError, BackendMatch


def _require_runtime() -> None:
    if SikuligoPattern is None or SikuligoScreen is None:
        raise BackendError(
            "Missing sikuligo runtime package. Install it first: pip install sikuligo"
        )


def _require_pb():
    if pb is None:
        raise BackendError("Missing generated protobuf stubs required by sikuligo runtime")
    return pb


def _to_backend_error(exc: Exception) -> BackendError:
    if isinstance(exc, BackendError):
        return exc
    if isinstance(exc, SikuliError):
        return BackendError(str(exc))
    return BackendError(f"{type(exc).__name__}: {exc}")


def _rect_from_match(raw: Any) -> tuple[int, int, int, int]:
    if all(hasattr(raw, k) for k in ("x", "y", "w", "h")):
        return int(raw.x), int(raw.y), int(raw.w), int(raw.h)
    rect = getattr(raw, "rect", None)
    if rect is None:
        raise BackendError("match object does not expose rect bounds")
    return int(rect.x), int(rect.y), int(rect.w), int(rect.h)


def _target_from_match(raw: Any, fallback_rect: tuple[int, int, int, int]) -> tuple[int, int]:
    if all(hasattr(raw, k) for k in ("target_x", "target_y")):
        return int(raw.target_x), int(raw.target_y)
    target = getattr(raw, "target", None)
    if target is not None:
        return int(target.x), int(target.y)
    x, y, w, h = fallback_rect
    return x + (w // 2), y + (h // 2)


def _normalize_button(button: Any) -> str:
    if isinstance(button, str):
        value = button.strip().lower()
        if value in ("left", "right", "middle"):
            return value
    if isinstance(button, int):
        # Java InputEvent mask compatibility
        if button == 16:
            return "left"
        if button == 4:
            return "right"
        if button == 8:
            return "middle"
    return "left"


def _normalize_key(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    lowered = text.lower()
    if "backspace" in lowered:
        return "backspace"
    if len(text) == 1:
        return text.lower()
    return lowered


def _capture_to_png(path: str, bounds: tuple[int, int, int, int] | None) -> None:
    if sys.platform == "darwin":
        cmd = ["screencapture", "-x"]
        if bounds is not None:
            x, y, w, h = bounds
            if w > 0 and h > 0:
                cmd.append(f"-R{x},{y},{w},{h}")
        cmd.append(path)
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return

    import_cmd = shutil.which("import")
    if import_cmd:
        cmd = [import_cmd, "-window", "root"]
        if bounds is not None:
            x, y, w, h = bounds
            if w > 0 and h > 0:
                cmd.extend(["-crop", f"{w}x{h}+{x}+{y}"])
        cmd.append(path)
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return

    scrot_cmd = shutil.which("scrot")
    if scrot_cmd:
        cmd = [scrot_cmd]
        if bounds is not None:
            x, y, w, h = bounds
            if w > 0 and h > 0:
                cmd.extend(["-a", f"{x},{y},{w},{h}"])
        cmd.append(path)
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return

    raise BackendError("screen capture backend unavailable for this runtime")


def _coerce_point(value: Any) -> tuple[int, int]:
    if isinstance(value, Location):
        return int(value.x), int(value.y)
    if isinstance(value, tuple) and len(value) == 2:
        return int(value[0]), int(value[1])
    if isinstance(value, list) and len(value) == 2:
        return int(value[0]), int(value[1])
    if hasattr(value, "getX") and hasattr(value, "getY"):
        return int(value.getX()), int(value.getY())
    if hasattr(value, "x") and hasattr(value, "y"):
        return int(value.x), int(value.y)
    if hasattr(value, "target_x") and hasattr(value, "target_y"):
        return int(value.target_x), int(value.target_y)
    if hasattr(value, "getClickLocation"):
        return _coerce_point(value.getClickLocation())
    raise BackendError(f"Unable to coerce point from {type(value).__name__}")


@dataclass
class Location:
    x: int
    y: int

    def getX(self) -> int:
        return int(self.x)

    def getY(self) -> int:
        return int(self.y)

    def setX(self, value: int) -> None:
        self.x = int(value)

    def setY(self, value: int) -> None:
        self.y = int(value)


@dataclass
class Pattern:
    _raw: Any

    @classmethod
    def from_image(cls, image: str | bytes | bytearray | memoryview) -> "Pattern":
        _require_runtime()
        return cls(SikuligoPattern(image))

    def similar(self, similarity: float) -> "Pattern":
        self._raw = self._raw.similar(similarity)
        return self

    def exact(self) -> "Pattern":
        self._raw = self._raw.exact()
        return self

    def target_offset(self, dx: int, dy: int) -> "Pattern":
        self._raw = self._raw.target_offset(dx, dy)
        return self

    # Legacy alias
    def targetOffset(self, dx: int, dy: int) -> "Pattern":
        return self.target_offset(dx, dy)

    def resize(self, factor: float) -> "Pattern":
        self._raw = self._raw.resize(factor)
        return self

    @property
    def raw(self) -> Any:
        return self._raw

    def __str__(self) -> str:
        return str(self._raw)


class Region:
    def __init__(
        self,
        raw_region: Any,
        *,
        screen: "Screen | None" = None,
        bounds: tuple[int, int, int, int] | None = None,
        score: float = 0.0,
        index: int = 0,
        target: tuple[int, int] | None = None,
    ) -> None:
        self._raw = raw_region
        self._screen = screen
        self._bounds = tuple(int(v) for v in bounds) if bounds is not None else None
        self._click_offset = (0, 0)
        self.score = float(score)
        self.index = int(index)
        if target is None and self._bounds is not None:
            x, y, w, h = self._bounds
            target = (x + (w // 2), y + (h // 2))
        self.target_x = int(target[0]) if target else 0
        self.target_y = int(target[1]) if target else 0

    @staticmethod
    def _coerce_pattern(pattern: Pattern | str | bytes | bytearray | memoryview) -> Pattern:
        if isinstance(pattern, Pattern):
            return pattern
        return Pattern.from_image(pattern)

    @staticmethod
    def _coerce_bounds(value: Any) -> tuple[int, int, int, int]:
        if isinstance(value, Region):
            return value.getX(), value.getY(), value.getW(), value.getH()
        if isinstance(value, tuple) and len(value) == 4:
            return int(value[0]), int(value[1]), int(value[2]), int(value[3])
        if isinstance(value, list) and len(value) == 4:
            return int(value[0]), int(value[1]), int(value[2]), int(value[3])
        if all(hasattr(value, k) for k in ("x", "y", "w", "h")):
            return int(value.x), int(value.y), int(value.w), int(value.h)
        if all(hasattr(value, k) for k in ("getX", "getY", "getW", "getH")):
            return int(value.getX()), int(value.getY()), int(value.getW()), int(value.getH())
        raise BackendError(f"Unable to coerce region bounds from {type(value).__name__}")

    @classmethod
    def from_match(cls, raw_match: Any, *, raw_region: Any, screen: "Screen | None") -> "Region":
        rect = _rect_from_match(raw_match)
        target = _target_from_match(raw_match, rect)
        score = float(getattr(raw_match, "score", 0.0))
        index = int(getattr(raw_match, "index", 0))
        return cls(raw_region, screen=screen, bounds=rect, score=score, index=index, target=target)

    def _wrap_scope(self, raw_scope: Any, bounds: tuple[int, int, int, int] | None) -> "Region":
        return Region(raw_scope, screen=self._screen, bounds=bounds)

    def _point_union(self, x: int, y: int) -> "Region":
        x1, y1, w, h = self._bounds or (x, y, 1, 1)
        x2 = x1 + w
        y2 = y1 + h
        min_x = min(x1, x)
        min_y = min(y1, y)
        max_x = max(x2, x)
        max_y = max(y2, y)
        return self._wrap_scope(self._raw, (min_x, min_y, max_x - min_x, max_y - min_y))

    def getX(self) -> int:
        return int(self._bounds[0]) if self._bounds is not None else 0

    def getY(self) -> int:
        return int(self._bounds[1]) if self._bounds is not None else 0

    def getW(self) -> int:
        return int(self._bounds[2]) if self._bounds is not None else 0

    def getH(self) -> int:
        return int(self._bounds[3]) if self._bounds is not None else 0

    def setX(self, value: int) -> None:
        x, y, w, h = self._bounds or (0, 0, 0, 0)
        self._bounds = (int(value), y, w, h)

    def setY(self, value: int) -> None:
        x, y, w, h = self._bounds or (0, 0, 0, 0)
        self._bounds = (x, int(value), w, h)

    def setClickOffset(self, offset: Location) -> None:
        self._click_offset = (int(offset.getX()), int(offset.getY()))

    def getClickOffset(self) -> Location:
        return Location(self._click_offset[0], self._click_offset[1])

    def getClickLocation(self) -> Location:
        x = self.getX() + (self.getW() // 2) + self._click_offset[0]
        y = self.getY() + (self.getH() // 2) + self._click_offset[1]
        return Location(x, y)

    def add(self, operand: Any) -> "Region":
        if self._bounds is None:
            return self
        try:
            ox, oy, ow, oh = self._coerce_bounds(operand)
            x1, y1, w1, h1 = self._bounds
            min_x = min(x1, ox)
            min_y = min(y1, oy)
            max_x = max(x1 + w1, ox + ow)
            max_y = max(y1 + h1, oy + oh)
            return self._wrap_scope(self._raw, (min_x, min_y, max_x - min_x, max_y - min_y))
        except BackendError:
            px, py = _coerce_point(operand)
            return self._point_union(px, py)

    def limit(self, operand: Any) -> "Region":
        if self._bounds is None:
            return self
        x1, y1, w1, h1 = self._bounds
        x2, y2, w2, h2 = self._coerce_bounds(operand)
        left = max(x1, x2)
        top = max(y1, y2)
        right = min(x1 + w1, x2 + w2)
        bottom = min(y1 + h1, y2 + h2)
        if right < left or bottom < top:
            raise BackendError("Region is outside parent bounds")
        return self._wrap_scope(self._raw, (left, top, right - left, bottom - top))

    def nearby(self, value: int | None = None) -> "Region":
        if self._bounds is None:
            return self
        pad = int(value) if value is not None else 50
        x, y, w, h = self._bounds
        return self._wrap_scope(self._raw, (x - pad, y - pad, w + (2 * pad), h + (2 * pad)))

    def above(self, value: int | None = None) -> "Region":
        if self._bounds is None:
            return self
        x, y, w, _ = self._bounds
        h = int(value) if value is not None else max(1, self.getH())
        return self._wrap_scope(self._raw, (x, y - h, w, h))

    def below(self, value: int | None = None) -> "Region":
        if self._bounds is None:
            return self
        x, y, w, h0 = self._bounds
        h = int(value) if value is not None else max(1, h0)
        return self._wrap_scope(self._raw, (x, y + h0, w, h))

    def right(self, value: int | None = None) -> "Region":
        if self._bounds is None:
            return self
        x, y, w0, h = self._bounds
        w = int(value) if value is not None else max(1, w0)
        return self._wrap_scope(self._raw, (x + w0, y, w, h))

    def left(self, value: int | None = None) -> "Region":
        if self._bounds is None:
            return self
        x, y, w0, h = self._bounds
        w = int(value) if value is not None else max(1, w0)
        return self._wrap_scope(self._raw, (x - w, y, w, h))

    def find(self, pattern: Pattern | str | bytes | bytearray | memoryview, timeout_millis: int | None = None) -> "Region":
        resolved = self._coerce_pattern(pattern)
        try:
            match = self._raw.find(resolved.raw, timeout_millis=timeout_millis)
            return Region.from_match(match, raw_region=self._raw, screen=self._screen)
        except Exception as exc:  # pragma: no cover - backend proxy
            raise _to_backend_error(exc) from exc

    def exists(self, pattern: Pattern | str | bytes | bytearray | memoryview, timeout_millis: int = 0) -> "Region | None":
        resolved = self._coerce_pattern(pattern)
        try:
            match = self._raw.exists(resolved.raw, timeout_millis=timeout_millis)
            if match is None:
                return None
            return Region.from_match(match, raw_region=self._raw, screen=self._screen)
        except Exception as exc:  # pragma: no cover - backend proxy
            raise _to_backend_error(exc) from exc

    def wait(self, pattern: Pattern | str | bytes | bytearray | memoryview, timeout_millis: int = 3000) -> "Region":
        resolved = self._coerce_pattern(pattern)
        try:
            match = self._raw.wait(resolved.raw, timeout_millis=timeout_millis)
            return Region.from_match(match, raw_region=self._raw, screen=self._screen)
        except Exception as exc:  # pragma: no cover - backend proxy
            raise _to_backend_error(exc) from exc

    def click(self, pattern: Pattern | str | bytes | bytearray | memoryview, timeout_millis: int | None = None) -> "Region":
        resolved = self._coerce_pattern(pattern)
        try:
            match = self._raw.click(resolved.raw, timeout_millis=timeout_millis)
            return Region.from_match(match, raw_region=self._raw, screen=self._screen)
        except Exception as exc:  # pragma: no cover - backend proxy
            raise _to_backend_error(exc) from exc

    def hover(self, pattern: Pattern | str | bytes | bytearray | memoryview, timeout_millis: int | None = None) -> "Region":
        match = self.find(pattern, timeout_millis=timeout_millis)
        if self._screen is not None:
            self._screen.move_to(match.getClickLocation())
        return match

    # Compatibility methods used by legacy entity code
    def mouseMove(self, target: Any) -> None:
        if self._screen is None:
            raise BackendError("region is not associated with a screen")
        self._screen.move_to(target)

    def mouseDown(self, button: Any = "left") -> None:
        if self._screen is None:
            raise BackendError("region is not associated with a screen")
        self._screen.mouseDown(button)

    def mouseUp(self, button: Any = "left") -> None:
        if self._screen is None:
            raise BackendError("region is not associated with a screen")
        self._screen.mouseUp(button)

    def __str__(self) -> str:
        if self._bounds is None:
            return "ScreenRegion(*)"
        x, y, w, h = self._bounds
        return f"Region({x},{y},{w},{h})"


class Screen(Region):
    def __init__(self, raw_screen: Any) -> None:
        self._screen = self
        self._cursor = (0, 0)
        self._mouse_down_button = None
        self._raw_screen = raw_screen
        super().__init__(raw_screen, screen=self, bounds=None)

    @property
    def client(self):
        return self._raw_screen.client

    @property
    def meta(self):
        return getattr(self._raw_screen, "meta", None)

    @classmethod
    def auto(cls, **kwargs) -> "Screen":
        _require_runtime()
        try:
            return cls(SikuligoScreen.auto(**kwargs))
        except Exception as exc:  # pragma: no cover - backend proxy
            raise _to_backend_error(exc) from exc

    @classmethod
    def connect(cls, **kwargs) -> "Screen":
        _require_runtime()
        try:
            return cls(SikuligoScreen.connect(**kwargs))
        except Exception as exc:  # pragma: no cover - backend proxy
            raise _to_backend_error(exc) from exc

    @classmethod
    def spawn(cls, **kwargs) -> "Screen":
        _require_runtime()
        try:
            return cls(SikuligoScreen.spawn(**kwargs))
        except Exception as exc:  # pragma: no cover - backend proxy
            raise _to_backend_error(exc) from exc

    @classmethod
    def getNumberScreens(cls) -> int:
        return 1

    def setAutoWaitTimeout(self, timeout_seconds: float) -> None:
        # SikuliGO path controls timeout per-call; keep compatibility no-op.
        _ = timeout_seconds

    def region(self, x: int, y: int, w: int, h: int) -> Region:
        try:
            scoped = self._raw_screen.region(int(x), int(y), int(w), int(h))
            return Region(scoped, screen=self, bounds=(int(x), int(y), int(w), int(h)))
        except Exception as exc:  # pragma: no cover - backend proxy
            raise _to_backend_error(exc) from exc

    @staticmethod
    def _bounds_from_region(region: Any | None) -> tuple[int, int, int, int] | None:
        if region is None:
            return None
        try:
            return Region._coerce_bounds(region)
        except Exception:
            return None

    def capture_region(self, region: Any | None = None) -> str:
        bounds = self._bounds_from_region(region)
        fd, path = tempfile.mkstemp(prefix="sikuligo-capture-", suffix=".png")
        os.close(fd)
        try:
            _capture_to_png(path, bounds)
            return path
        except Exception as exc:
            try:
                os.unlink(path)
            except OSError:
                pass
            raise _to_backend_error(exc) from exc

    def move_mouse(self, x: int, y: int, delay_millis: int | None = None) -> None:
        pb_mod = _require_pb()
        req = pb_mod.MoveMouseRequest(x=int(x), y=int(y))
        if delay_millis is not None:
            req.opts.delay_millis = int(delay_millis)
        self.client.move_mouse(req)
        self._cursor = (int(x), int(y))

    def click_point(self, x: int, y: int, button: Any = "left", delay_millis: int | None = None) -> None:
        pb_mod = _require_pb()
        req = pb_mod.ClickRequest(x=int(x), y=int(y))
        req.opts.button = _normalize_button(button)
        if delay_millis is not None:
            req.opts.delay_millis = int(delay_millis)
        self.client.click(req)
        self._cursor = (int(x), int(y))

    def type_text(self, text: str, delay_millis: int | None = None) -> None:
        pb_mod = _require_pb()
        req = pb_mod.TypeTextRequest(text=str(text))
        if delay_millis is not None:
            req.opts.delay_millis = int(delay_millis)
        self.client.type_text(req)

    def hotkey(self, keys: Iterable[str]) -> None:
        pb_mod = _require_pb()
        req = pb_mod.HotkeyRequest(keys=[str(k) for k in keys if str(k).strip()])
        self.client.hotkey(req)

    def move_to(self, target: Any) -> None:
        x, y = _coerce_point(target)
        self.move_mouse(x, y)

    # Legacy naming compatibility
    def mouseMove(self, target: Any) -> None:
        self.move_to(target)

    def mouseDown(self, button: Any = "left") -> None:
        self._mouse_down_button = _normalize_button(button)

    def mouseUp(self, button: Any = "left") -> None:
        normalized = _normalize_button(button)
        if self._mouse_down_button is None:
            return
        self.click_point(self._cursor[0], self._cursor[1], button=normalized)
        self._mouse_down_button = None

    def drag_to(self, start: Any, destination: Any, button: Any = "left") -> None:
        # No dedicated drag RPC yet; keep input path backend-native by approximating:
        # move to start, then move + click destination.
        sx, sy = _coerce_point(start)
        dx, dy = _coerce_point(destination)
        self.move_mouse(sx, sy)
        self.move_mouse(dx, dy)
        self.click_point(dx, dy, button=button)

    # Legacy naming compatibility
    def type(self, key: Any = None, text: Any = None, keyMod: Any = None) -> None:
        key_name = _normalize_key(key)
        if key is None and text is not None:
            value = str(text)
            if keyMod is not None and len(value) == 1:
                self.hotkey([value])
            else:
                self.type_text(value)
            return
        if key is not None and text is None:
            if key_name:
                if len(key_name) == 1:
                    self.type_text(key_name)
                else:
                    self.hotkey([key_name])
            return
        if key is not None and text is not None:
            self.type_text(str(text))

    def paste(self, text: str) -> None:
        self.type_text(text)

    def close(self) -> None:
        self._raw_screen.close()
