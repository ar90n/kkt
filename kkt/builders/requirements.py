import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

from johnnydep.lib import JohnnyDist, flatten_deps, pipper
from percache import Cache
from pkg_resources.extern.packaging.specifiers import SpecifierSet

from .default_hosted_pkgs import DEFAULT_HOSTED_PKGS
from .package import Package


def _cache(work_dir: Path) -> Callable:
    return Cache(str(work_dir / "cache"))


def _calc_kernel_requirements(
    requirements: Iterable[str], hosted_pkgs: Dict[str, str]
) -> Dict[str, SpecifierSet]:
    def _is_hosted(dep) -> bool:
        print(type(dep))
        n = dep.name
        s = dep.req.specifier
        return n in hosted_pkgs and hosted_pkgs[n] in s

    result: Dict[str, SpecifierSet] = defaultdict(SpecifierSet)
    for req in requirements:
        for dep in flatten_deps(JohnnyDist(req)):
            if not _is_hosted(dep):
                result[dep.name] &= dep.req.specifier
    return result


def _download_dep_pkgs(deps: Dict[str, SpecifierSet], target_dir: Path) -> List[Path]:
    if not target_dir.is_dir():
        raise ValueError(f"taret_dir is not directory.: {target_dir}")

    result = []
    requirements = (f"{n}{str(s)}" for n, s in deps.items())
    for req in requirements:
        res = pipper.get(req, tmpdir=str(target_dir))
        if "path" in res:
            result.append(Path(res["path"]))
    return result


def _get_custom_pkg_json_path() -> Path:
    return Path(os.environ["HOME"]) / ".kkt" / "kernel_pkg.json"


def _load_kaggle_hosted_pkgs() -> Dict[str, str]:
    try:
        pkg_json_path = _get_custom_pkg_json_path()
        kaggle_hosted_pkgs = json.load(pkg_json_path.open("rb"))
        return {req["name"]: req["version"] for req in kaggle_hosted_pkgs}
    except (OSError, KeyError):
        pass

    return DEFAULT_HOSTED_PKGS


def fetch_requirement_pkgs(requirements: Iterable[str], work_dir: Path):
    kaggle_hosted_pkgs = _load_kaggle_hosted_pkgs()
    kernel_requirements = _cache(work_dir)(_calc_kernel_requirements)(
        requirements, kaggle_hosted_pkgs
    )
    pkg_paths = _download_dep_pkgs(kernel_requirements, work_dir)

    return [Package(p.name, p.read_bytes()) for p in pkg_paths]
