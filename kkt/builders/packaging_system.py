from os import getcwd
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from pkg_resources.extern.packaging.specifiers import SpecifierSet
from poetry.factory import Factory
from poetry.io.null_io import NullIO
from poetry.masonry.builders import WheelBuilder
from poetry.poetry import Poetry
from poetry.utils.env import NullEnv

from .package import Package
from .requirements import fetch_requirement_pkgs


def _get_pkg_name(require):
    constraint = str(require.constraint)
    if 0 < len(constraint) and constraint[0] in "0123456789":
        constraint = "==" + constraint
    constraint = str(SpecifierSet(constraint))

    return f"{require.name}{constraint}"


def _get_required_pkg_names(poetry: Poetry) -> List[str]:
    return [_get_pkg_name(r) for r in poetry.package.requires]


def _create_work_dir(poetry: Poetry):
    work_dir_path = poetry.file.path.parent / ".kkt"
    work_dir_path.mkdir(exist_ok=True)
    return work_dir_path


def build_package(with_requirements: bool) -> List[Package]:
    poetry = Factory().create_poetry(getcwd())
    env = NullEnv()
    io = NullIO()

    with TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        wheel_pkg_name = WheelBuilder.make_in(poetry, env, io, temp_dir)
        pkg_path = temp_dir / wheel_pkg_name
        pkg_bytes = pkg_path.read_bytes()
        pkgs = [Package(wheel_pkg_name, pkg_bytes)]

    if with_requirements:
        pkg_names = _get_required_pkg_names(poetry)
        work_dir = _create_work_dir(poetry)
        pkgs.extend(fetch_requirement_pkgs(pkg_names, work_dir))

    return pkgs
