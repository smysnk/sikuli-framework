"""
Compatibility helpers used during migration from Python 2/Jython to Python 3.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

text_type = str


def execfile_compat(path: str, globals_dict: dict[str, Any]) -> None:
    """
    Python 3 replacement for execfile(path, globals).
    """
    source = Path(path).read_text(encoding="utf-8")
    code = compile(source, path, "exec")
    exec(code, globals_dict)
