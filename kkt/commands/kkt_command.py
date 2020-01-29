import sys
from pathlib import Path
from functools import wraps
from typing import Callable, List, Dict, Optional

from kaggle import KaggleApi
from kaggle.api_client import ApiClient

import click
from poetry.factory import Factory
from ..parser import KktParser
from ..exception import KktSectionNotFound

Wrapper = Callable[[Callable], Callable]


def kkt_command(init: bool = False, cwd: Optional[Path] = None) -> Wrapper:
    def _wrapper(command: Callable) -> Callable:
        @wraps(command)
        def _f(*args: List, **kwargs: Dict) -> None:
            prj_wd = Path.cwd() if cwd is None else cwd
            pyproject_path = Factory.locate(prj_wd)

            parser = KktParser(pyproject_path)

            try:
                kkt = parser.read()
            except KktSectionNotFound:
                if not init:
                    click.echo("Kkt section is not found in pyproject.yml.", err=True)
                    sys.exit(1)
                kkt = {}

            api = KaggleApi(ApiClient())
            api.authenticate()

            command(api, kkt, pyproject_path, *args, **kwargs)

        return _f

    return _wrapper
