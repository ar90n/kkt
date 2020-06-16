from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from pkg_resources.extern.packaging.specifiers import SpecifierSet
from poetry.factory import Factory
from poetry.io.null_io import NullIO
from poetry.masonry.builders import WheelBuilder
from poetry.utils.env import NullEnv

from .package import Package


def _get_constraint(require) -> str:
    constraint = str(require.constraint)
    if constraint == "*":
        constraint = ""
    if 0 < len(constraint) and constraint[0] in "0123456789":
        constraint = "==" + constraint
    return str(SpecifierSet(constraint))


def _get_pkg_name(require, enable_constraint: bool = False):
    constraint = _get_constraint(require) if enable_constraint else ""
    pkg_name = f"{require.name}{constraint}"
    return pkg_name


def get_dependencies(enable_constraint: bool = False) -> List[str]:
    poetry = Factory().create_poetry(Path.cwd())
    dependencies = [
        _get_pkg_name(r, enable_constraint) for r in poetry.package.requires
    ]
    return dependencies


def build_packages() -> List[Package]:
    poetry = Factory().create_poetry(Path.cwd())
    env = NullEnv()
    io = NullIO()

    with TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        wheel_pkg_name = WheelBuilder.make_in(poetry, env, io, temp_dir)
        pkg_path = temp_dir / wheel_pkg_name
        pkg_bytes = pkg_path.read_bytes()
        pkgs = [Package(wheel_pkg_name, pkg_bytes)]

    return pkgs
