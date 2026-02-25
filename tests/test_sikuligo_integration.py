from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import time
import importlib.util

import pytest

from adapters.sikuligo_backend import Screen


def _integration_enabled() -> bool:
    return os.getenv("SIKULIGO_INTEGRATION", "1").strip() != "0"


def _runtime_available() -> bool:
    return importlib.util.find_spec("sikuligo") is not None


def _wait_for_tcp(address: str, timeout_seconds: float = 10.0) -> None:
    host, port_text = address.split(":", 1)
    port = int(port_text)
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(0.05)
    raise TimeoutError(f"timeout waiting for {address}")


def _require_binary(path: Path) -> None:
    if not path.exists():
        pytest.skip(f"sikuligo binary not found: {path}")
    if not os.access(path, os.X_OK):
        pytest.skip(f"sikuligo binary is not executable: {path}")


@pytest.mark.integration
def test_screen_auto_spawns_server_and_connects(sikuligo_binary: Path, free_port: int):
    if not _integration_enabled():
        pytest.skip("set SIKULIGO_INTEGRATION=1 to run live integration tests")
    if not _runtime_available():
        pytest.skip("sikuligo python runtime package is not installed")
    _require_binary(sikuligo_binary)

    address = f"127.0.0.1:{free_port}"
    os.environ["SIKULIGO_BINARY_PATH"] = str(sikuligo_binary)

    screen = Screen.auto(
        address=address,
        binary_path=str(sikuligo_binary),
        admin_listen="",
        startup_timeout_seconds=10.0,
        stdio="ignore",
    )
    try:
        assert screen is not None
        assert screen.meta is not None
        assert screen.meta.spawned_server is True
    finally:
        screen.close()


@pytest.mark.integration
def test_screen_connect_and_auto_reuse_existing_server(sikuligo_binary: Path, free_port: int, tmp_path):
    if not _integration_enabled():
        pytest.skip("set SIKULIGO_INTEGRATION=1 to run live integration tests")
    if not _runtime_available():
        pytest.skip("sikuligo python runtime package is not installed")
    _require_binary(sikuligo_binary)

    address = f"127.0.0.1:{free_port}"
    db_path = tmp_path / "integration.db"
    proc = subprocess.Popen(
        [
            str(sikuligo_binary),
            "-listen",
            address,
            "-admin-listen",
            "",
            "-enable-reflection=false",
            "-sqlite-path",
            str(db_path),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        time.sleep(0.1)
        if proc.poll() is not None:
            pytest.skip(f"sikuligo process exited early with code={proc.returncode}")
        _wait_for_tcp(address, timeout_seconds=10.0)

        connected = Screen.connect(address=address, startup_timeout_seconds=5.0)
        try:
            assert connected is not None
            assert connected.meta is not None
            assert connected.meta.spawned_server is False
        finally:
            connected.close()

        auto = Screen.auto(
            address=address,
            binary_path=str(sikuligo_binary),
            startup_timeout_seconds=5.0,
            admin_listen="",
            stdio="ignore",
        )
        try:
            assert auto.meta is not None
            assert auto.meta.spawned_server is False
        finally:
            auto.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
