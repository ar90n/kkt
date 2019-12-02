from os import getcwd
from pathlib import Path
from tempfile import TemporaryDirectory

from poetry.io.null_io import NullIO
from poetry.masonry.builders import WheelBuilder
from poetry.poetry import Poetry
from poetry.utils.env import NullEnv

from ..utils.encode import encode


def poetry_packaging() -> (str, str):
    poetry = Poetry.create(getcwd())
    env = NullEnv()
    io = NullIO()

    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        wheel_pkg_name = WheelBuilder.make_in(poetry, env, io, temp_dir)
        pkg_path = temp_dir / wheel_pkg_name
        pkg_encoded = encode(pkg_path)

    return wheel_pkg_name, pkg_encoded
