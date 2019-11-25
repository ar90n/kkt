from pathlib import Path
from typing import Union

from tomlkit.toml_file import TOMLFile


class PyprojectParser(TOMLFile):
    def __init__(self, path: Union[str, Path]) -> None:
        super().__init__(str(path))

        self._path = Path(path)

    @property
    def path(self) -> Path:
        return self._path


class KktParser(PyprojectParser):
    def __init__(self, path: Union[str, Path]) -> None:
        super().__init__(path)

    def read(self) -> dict:
        pyproj = super().read()
        return pyproj.get("tool").get("kkt").get("meta_data")
