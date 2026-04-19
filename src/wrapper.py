"""
Compatibility exports for the SikuliGO runtime.
"""

from __future__ import annotations

import platform
import shutil
import subprocess

from adapters.sikuligo_backend import Location, Pattern, Region, Screen
from config import Config


class OS(object):
    WINDOWS = "windows"
    MAC = "mac"
    LINUX = "linux"
    UNKNOWN = "unknown"


def _detect_os() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return OS.MAC
    if system == "windows":
        return OS.WINDOWS
    if system == "linux":
        return OS.LINUX
    return OS.UNKNOWN


def _run_clipboard_command(cmd: list[str]) -> str:
    try:
        proc = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        return ""
    return proc.stdout


class Env(object):
    @staticmethod
    def getOS() -> str:
        return _detect_os()

    @staticmethod
    def getOSVersion(fullName=None) -> str:
        os_name = _detect_os()
        if os_name == OS.MAC:
            version = platform.mac_ver()[0]
            if version:
                return version
        return platform.release()

    @staticmethod
    def getSikuliVersion() -> str:
        return "sikuli-go"

    @staticmethod
    def getClipboard() -> str:
        os_name = _detect_os()
        if os_name == OS.MAC:
            return _run_clipboard_command(["pbpaste"])
        if os_name == OS.WINDOWS:
            return _run_clipboard_command(
                ["powershell", "-NoProfile", "-Command", "Get-Clipboard"]
            )

        for command in (
            ["wl-paste", "-n"],
            ["xclip", "-selection", "clipboard", "-o"],
            ["xsel", "--clipboard", "--output"],
        ):
            if shutil.which(command[0]):
                return _run_clipboard_command(command)
        return ""


def capture(region):
    screen = Config.getScreen()
    capture_fn = getattr(screen, "capture_region", None)
    if not callable(capture_fn):
        raise RuntimeError("capture_region is unavailable on the configured screen")
    return capture_fn(region)


__all__ = [
    "Env",
    "OS",
    "Location",
    "Pattern",
    "Region",
    "Screen",
    "capture",
]
