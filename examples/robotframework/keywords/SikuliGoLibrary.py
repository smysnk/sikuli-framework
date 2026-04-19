from __future__ import annotations

from pathlib import Path

from robot.libraries.BuiltIn import BuiltIn
from sikuligo import Pattern, Screen


class SikuliGoLibrary:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self) -> None:
        self._screen = None

    def open_screen(self) -> None:
        if self._screen is None:
            self._screen = Screen()

    def close_screen(self) -> None:
        if self._screen is None:
            return
        self._screen.close()
        self._screen = None

    def click_image(self, image_path: str, timeout_millis: int = 5000, exact: bool = True):
        if self._screen is None:
            self.open_screen()

        resolved = self._resolve_image_path(image_path)
        pattern = Pattern(str(resolved))
        if exact:
            pattern = pattern.exact()

        match = self._screen.click(pattern, timeout_millis=int(timeout_millis))
        return [match.target_x, match.target_y]

    def _resolve_image_path(self, image_path: str) -> Path:
        path = Path(image_path)
        if path.is_absolute() and path.exists():
            return path

        suite_source = BuiltIn().get_variable_value("${SUITE SOURCE}")
        if suite_source:
            suite_relative = Path(str(suite_source)).resolve().parent / path
            if suite_relative.exists():
                return suite_relative

        project_relative = Path(__file__).resolve().parents[1] / path
        if project_relative.exists():
            return project_relative

        raise FileNotFoundError(f"image path not found: {image_path}")
