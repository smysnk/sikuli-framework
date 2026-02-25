from __future__ import annotations

import os
from pathlib import Path
import re
import sqlite3
import time
import zlib
import importlib.util

import pytest

from adapters.sikuligo_backend import BackendError, Region, Screen
from entity.entity import Entity
from region.finder import Finder


def _integration_enabled() -> bool:
    return os.getenv("SIKULIGO_INTEGRATION", "1").strip() != "0"


def _runtime_available() -> bool:
    return importlib.util.find_spec("sikuligo") is not None


def _require_binary(path: Path) -> None:
    if not path.exists():
        pytest.skip(f"sikuligo binary not found: {path}")
    if not os.access(path, os.X_OK):
        pytest.skip(f"sikuligo binary is not executable: {path}")


def _gray_image(name: str, rows: list[list[int]]):
    from generated.sikuli.v1 import sikuli_pb2 as pb

    height = len(rows)
    width = len(rows[0]) if height else 0
    if width <= 0 or height <= 0:
        raise ValueError("rows must contain at least one pixel")
    pix = bytearray()
    for row in rows:
        if len(row) != width:
            raise ValueError("rows must be rectangular")
        pix.extend(int(v) & 0xFF for v in row)
    return pb.GrayImage(name=name, width=width, height=height, pix=bytes(pix))


def _write_gray_png(path: Path, rows: list[list[int]]) -> None:
    height = len(rows)
    width = len(rows[0]) if height else 0
    if width <= 0 or height <= 0:
        raise ValueError("rows must contain at least one pixel")
    for row in rows:
        if len(row) != width:
            raise ValueError("rows must be rectangular")

    raw = bytearray()
    for row in rows:
        raw.append(0)  # filter: None
        raw.extend(int(v) & 0xFF for v in row)

    def _chunk(tag: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return (
            len(payload).to_bytes(4, "big")
            + tag
            + payload
            + crc.to_bytes(4, "big")
        )

    ihdr = (
        width.to_bytes(4, "big")
        + height.to_bytes(4, "big")
        + bytes([8, 0, 0, 0, 0])  # bit depth, grayscale, compression/filter/interlace
    )
    payload = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw)))
        + _chunk(b"IEND", b"")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _session_snapshot(db_path: Path) -> tuple[int, int, int, list[str], list[str]]:
    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM api_sessions")
        api_count = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM client_sessions")
        client_count = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM interactions")
        interaction_count = int(cur.fetchone()[0])
        cur.execute("SELECT method FROM interactions ORDER BY id ASC")
        methods = [str(row[0]) for row in cur.fetchall()]
        cur.execute("SELECT connection_id FROM client_sessions ORDER BY id ASC")
        connection_ids = [str(row[0]) for row in cur.fetchall()]
    return api_count, client_count, interaction_count, methods, connection_ids


def _wait_for_interactions(db_path: Path, timeout_seconds: float = 3.0) -> tuple[int, int, int, list[str], list[str]]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            snapshot = _session_snapshot(db_path)
        except sqlite3.Error:
            time.sleep(0.05)
            continue
        if snapshot[2] > 0:
            return snapshot
        time.sleep(0.05)
    return _session_snapshot(db_path)


class _Formatter:
    def setLabel(self, *_args, **_kwargs):
        return self

    def showBaseline(self, *_args, **_kwargs):
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


class _GrpcFindRegion:
    def __init__(self, *, address: str, auth_token: str, source_rows: list[list[int]], pattern_bank: dict[str, list[list[int]]]):
        self._address = address
        self._auth_token = auth_token
        self._source_rows = source_rows
        self._pattern_bank = pattern_bank

    @staticmethod
    def _resolve_pattern_path(pattern) -> str:
        if hasattr(pattern, "raw") and hasattr(pattern.raw, "image"):
            return str(Path(str(pattern.raw.image)).resolve())
        if hasattr(pattern, "image"):
            return str(Path(str(pattern.image)).resolve())
        match = re.search(r'P\((?P<path>.*?)\)', str(pattern), re.IGNORECASE)
        if match:
            return str(Path(match.group("path")).resolve())
        raise BackendError(f"unable to resolve pattern path from {pattern}")

    def wait(self, pattern, timeout_millis: int | None = None):
        import grpc
        from generated.sikuli.v1 import sikuli_pb2 as pb
        from generated.sikuli.v1 import sikuli_pb2_grpc as pb_grpc

        resolved_pattern = self._resolve_pattern_path(pattern)
        pattern_rows = self._pattern_bank.get(resolved_pattern)
        if pattern_rows is None:
            raise BackendError(f"pattern not found in sample map bank: {resolved_pattern}")

        req = pb.FindRequest(
            source=_gray_image("sample-map-source", self._source_rows),
            pattern=pb.Pattern(image=_gray_image(Path(resolved_pattern).name, pattern_rows)),
        )
        timeout_seconds = max(0.2, float(timeout_millis or 1000) / 1000.0)
        metadata = [("x-api-key", self._auth_token)] if self._auth_token else None

        channel = grpc.insecure_channel(self._address)
        try:
            stub = pb_grpc.SikuliServiceStub(channel)
            try:
                response = stub.Find(req, timeout=timeout_seconds, metadata=metadata)
            except grpc.RpcError as exc:
                raise BackendError(exc.details() or "grpc find failed") from exc
        finally:
            channel.close()

        if response.match is None:
            raise BackendError("find returned no match")
        return Region.from_match(response.match, raw_region=self, screen=None)


class _ConfigStub:
    backend = "sikuligo"
    imageSuffix = ".png"
    regionTimeout = 1

    def __init__(self, image_root: Path, region: _GrpcFindRegion):
        self.imageBaseline = str(image_root)
        self.imageSearchPaths = [str(image_root)]
        self._region = region

    def getImageSearchPaths(self):
        return list(self.imageSearchPaths)

    def getScreen(self):
        return self._region


class SampleMapEntity(Entity):
    pass


@pytest.mark.integration
def test_sample_map_validate_uses_live_grpc_find(sikuligo_binary: Path, free_port: int, tmp_path: Path, monkeypatch):
    if not _integration_enabled():
        pytest.skip("set SIKULIGO_INTEGRATION=1 to run live integration tests")
    if not _runtime_available():
        pytest.skip("sikuligo python runtime package is not installed")
    if importlib.util.find_spec("generated.sikuli.v1.sikuli_pb2") is None:
        pytest.skip("generated sikuligo protobuf stubs are unavailable")
    _require_binary(sikuligo_binary)

    source_rows = [[255 for _ in range(32)] for _ in range(24)]
    pattern_rows = [[0 for _ in range(5)] for _ in range(5)]
    for y in range(6, 11):
        for x in range(8, 13):
            source_rows[y][x] = 0

    baseline_path = (tmp_path / "SampleMapEntity" / "SampleMapEntity.png").resolve()
    _write_gray_png(baseline_path, pattern_rows)
    db_path = tmp_path / "sample-map-integration.db"

    address = f"127.0.0.1:{free_port}"
    screen = Screen.auto(
        address=address,
        binary_path=str(sikuligo_binary),
        sqlite_path=str(db_path),
        admin_listen="",
        startup_timeout_seconds=10.0,
        stdio="ignore",
    )
    try:
        region = _GrpcFindRegion(
            address=screen.meta.address,
            auth_token=screen.meta.auth_token,
            source_rows=source_rows,
            pattern_bank={str(baseline_path): pattern_rows},
        )
        cfg = _ConfigStub(tmp_path, region)

        monkeypatch.setattr(Finder, "logger", lambda _entity: _Logger())
        monkeypatch.setattr(Finder, "config", cfg)
        monkeypatch.setattr(Finder, "transform", _IdentityTransform)

        monkeypatch.setattr(Entity, "logger", lambda _entity: _Logger())
        monkeypatch.setattr(Entity, "config", cfg)
        monkeypatch.setattr(Entity, "regionFinderStrategy", Finder)
        monkeypatch.setattr(Entity, "searcherStrategy", lambda: None)
        monkeypatch.setattr(Entity, "multiResultProxyStrategy", lambda _parent, result, _caller: result)

        mapped = SampleMapEntity(None)
        result = mapped.validate(timeout=2)

        assert result is mapped
        assert mapped.region is not None
        assert mapped.region.getX() == 8
        assert mapped.region.getY() == 6
        assert mapped.region.getW() == 5
        assert mapped.region.getH() == 5

        assert db_path.exists()
        api_count, client_count, interaction_count, methods, connection_ids = _wait_for_interactions(db_path)
        assert api_count >= 1
        assert client_count >= 1
        assert interaction_count >= 1
        assert any(method.endswith("/Find") for method in methods)
        uuid_re = re.compile(
            r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        )
        assert all(uuid_re.match(value) for value in connection_ids if value)
    finally:
        screen.close()
