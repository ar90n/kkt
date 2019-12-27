from typing import Tuple
from os import getcwd
from pathlib import Path
from tempfile import TemporaryDirectory

from poetry.io.null_io import NullIO
from poetry.masonry.builders import WheelBuilder
from poetry.factory import Factory
from poetry.utils.env import NullEnv

from ..utils.encode import encode


def poetry_packaging() -> Tuple[str, str]:
    poetry = Factory().create_poetry(getcwd())
    env = NullEnv()
    io = NullIO()

    with TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        wheel_pkg_name = WheelBuilder.make_in(poetry, env, io, temp_dir)
        pkg_path = temp_dir / wheel_pkg_name
        pkg_encoded = encode(pkg_path)

    return wheel_pkg_name, pkg_encoded
