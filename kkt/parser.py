from pathlib import Path
from typing import Union, Dict, List, Any, Iterable

from tomlkit.toml_file import TOMLFile
from tomlkit import table

from .exception import KktSectionNotFound, MandatoryKeyNotFound
from .utils.dict import merge

MANDATORY_KEYS: List = [("meta_data", [("slug", []), ("code_file", [])])]

DEFAULT_KKT_CONFIG: Dict = {
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


def _validate_keys(obj: Dict[str, Any], keys: List, path: str = "") -> None:
    for cur, children in keys:
        path = "{}.{}".format(path, cur)
        if cur not in obj:
            raise MandatoryKeyNotFound(path)
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

    def read(self) -> Dict[str, Any]:
        pyproj = super().read()
        try:
            kkt = pyproj["tool"]["kkt"]
        except KeyError:
            raise KktSectionNotFound()
        kkt = merge(DEFAULT_KKT_CONFIG, kkt)
        _validate_keys(kkt, MANDATORY_KEYS)

        return kkt

    def write(self, kkt_config: Dict[str, Any]) -> None:
        pyproj = super().read()
        pyproj["tool"]["kkt"] = kkt_config

        super().write(pyproj)
