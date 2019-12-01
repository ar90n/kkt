from pathlib import Path
from typing import Union, Dict, List

from tomlkit.toml_file import TOMLFile

from ..exception import KktSectionNotFound
from .dict import merge

MANDATORY_KEYS: List  = [("meta_data", [("slug", []), ("code_file", [])])]

DEFAULT_KKT_CONFIG = {
    "meta_data": {
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": False,
        "enable_internet": False,
        "dataset_sources": [],
        "kernel_data_sources": [],
        "competition_sources": [],
        "keywords": [],
    },
    "enable_git_tag": False,
}


def _validate_keys(obj, keys, path="") -> None:
    for cur, children in keys:
        path = "{}.{}".format(path, cur)
        if cur not in obj:
            raise ValueError(path)
        _validate_keys(obj[cur], children, path=path)


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

    def read(self):
        pyproj = super().read()
        try:
            kkt = pyproj["tool"]["kkt"]
        except KeyError:
            raise KktSectionNotFound()
        kkt = merge(DEFAULT_KKT_CONFIG, kkt)
        _validate_keys(kkt, MANDATORY_KEYS)

        return kkt
