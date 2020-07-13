import re
from pathlib import Path
from typing import Any, Dict, List, Union

from tomlkit.exceptions import NonExistentKey
from tomlkit.toml_file import TOMLFile

from .exception import (
    InvalidTarget,
    KktSectionNotFound,
    MandatoryKeyNotFound,
    MetaDataNotFound,
)
from .util import merge

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
        "enable_constraint": False,
    },
    "enable_git_tag": False,
}

META_DATA_KEYS = set(DEFAULT_KKT_CONFIG["meta_data"].keys())
META_DATA_KEYS.add("slug")
META_DATA_KEYS.add("code_file")
META_DATA_KEYS.add("competition")


def _validate_keys(obj: Dict[str, Any], mandatory_keys: List, path: str = "") -> None:
    """
    Raise MandatoryKeyNotFound if given obj doesn't contain all elements of mandatory_keys.

    >>> _validate_keys({"meta_data": {"slug": "slug", "code_file": "code_file"}}, MANDATORY_KEYS)

    # Comment out because pytest integration joesn't work
    #>>> _validate_keys({"meta_data": {"slug": "slug"}}, MANDATORY_KEYS)
    #MandatoryKeyNotFound('.meta_data.slug.code_file',)
    """

    for cur, children in mandatory_keys:
        path = "{}.{}".format(path, cur)
        if cur not in obj:
            raise MandatoryKeyNotFound(path)
        _validate_keys(obj[cur], children, path=path)


def _get_meta_data_keys(key: str) -> List[str]:
    """
    Return a list of keys to fetch partial meta_data from meta_data root.

    >>> _get_meta_data_keys(".")
    ['meta_data']
    >>> _get_meta_data_keys(".a.b.c")
    ['meta_data', 'a', 'b', 'c']
    """

    if re.match(r"^(\.|(\.[^.]+)+)$", key) is None:
        raise InvalidTarget(key)

    # key == "." means the root of meta_data
    return ["meta_data"] if key == "." else f"meta_data{key}".split(".")


def _trim_redundant_fields(meta_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trim field whose key are not in META_DATA_KEYS.

    >>> _trim_redundant_fields({"slug": "slug", "redundant": "redundant"})
    {'slug': 'slug'}
    """

    return {k: v for k, v in meta_data.items() if k in META_DATA_KEYS}


def _compose_meta_data(kkt: Dict[str, Any], key: str) -> Dict[str, Any]:
    """
    Compose a meta_data dict by recurcive sampling and merging them.

    >>> kkt = {                                \
        "meta_data": {                         \
            "slug": "slug",                    \
            "nest1": {                         \
                "code_file": "script.py",      \
                "nest2": {                     \
                    "kernel_type" : "script"   \
                }                              \
            }                                  \
        }                                      \
    }
    >>> _compose_meta_data(kkt, ".nest1.nest2")
    {'slug': 'slug', 'code_file': 'script.py', 'kernel_type': 'script'}
    """

    def _aux(meta_data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
        if len(keys) == 0:
            return meta_data

        try:
            meta_data = meta_data[keys[0]]
        except KeyError:
            raise MetaDataNotFound(key)

        return {**meta_data, **_aux(meta_data, keys[1:])}

    keys = _get_meta_data_keys(key)
    return _trim_redundant_fields(_aux(kkt, keys))


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

    def read_all(self) -> Dict[str, Any]:
        return super().read()

    def read(self, key: str = ".") -> Dict[str, Any]:
        pyproj = super().read()
        try:
            kkt = pyproj["tool"]["kkt"]
        except (NonExistentKey, KeyError):
            raise KktSectionNotFound()

        # following code didn't work.
        # kkt["meta_data"] =  _compose_meta_data(kkt, key)
        tmp = _compose_meta_data(kkt, key)
        del kkt["meta_data"]
        kkt.add("meta_data", tmp)

        kkt = merge(DEFAULT_KKT_CONFIG, kkt)
        _validate_keys(kkt, MANDATORY_KEYS)

        return kkt

    def write(self, kkt_config: Dict[str, Any]) -> None:
        pyproj = super().read()
        pyproj.setdefault("tool", {})["kkt"] = kkt_config

        super().write(pyproj)
