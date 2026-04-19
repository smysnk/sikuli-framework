from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module(module_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_config_defaults_to_sikuligo_without_env(monkeypatch):
    src_root = Path(__file__).resolve().parents[1] / "src"
    monkeypatch.syspath_prepend(str(src_root))
    monkeypatch.delenv("SIKULI_FRAMEWORK_BACKEND", raising=False)

    config_module = _load_module(src_root / "config.py", "config_cutover_check")

    assert config_module.BACKEND_SIKULIGO == "sikuligo"
    assert config_module.Config.backend == config_module.BACKEND_SIKULIGO


def test_example_map_modules_import_on_cpython(monkeypatch):
    workspace_root = Path(__file__).resolve().parents[1]
    src_root = workspace_root / "src"
    monkeypatch.syspath_prepend(str(src_root))

    calculator_module = _load_module(
        workspace_root / "examples" / "calculator" / "maps" / "calculator.py",
        "calculator_map_cutover_check",
    )
    textedit_module = _load_module(
        workspace_root / "examples" / "textedit" / "maps" / "textedit.py",
        "textedit_map_cutover_check",
    )

    assert calculator_module.Calculator.__name__ == "Calculator"
    assert textedit_module.TextEdit.__name__ == "TextEdit"
