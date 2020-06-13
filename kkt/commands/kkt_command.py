import sys
from pathlib import Path
from functools import wraps
from typing import Callable, List, Dict, Optional, Any, cast

from kaggle import KaggleApi
from kaggle.api_client import ApiClient

import click
from click import Command
from poetry.factory import Factory
from ..parser import KktParser
from ..exception import KktSectionNotFound

Wrapper = Callable[[Callable], Command]


def get_kaggle_api() -> Any:
    return KaggleApi(ApiClient())


def _wrap_click_command(f: Callable, init: bool) -> Command:
    if not init:
        f = click.option("-t", "--target", default=".", type=str)(f)
    return click.command()(f)


def kkt_command(init: bool = False, cwd: Optional[Path] = None) -> Wrapper:
    def _wrapper(command: Callable) -> Command:
        @wraps(command)
        def _f(*args: List, **kwargs: Dict) -> None:
            prj_wd = Path.cwd() if cwd is None else cwd
            pyproject_path = Factory.locate(prj_wd)

            parser = KktParser(pyproject_path)

            try:
                target = cast("str", kwargs.get("target", "."))
                kkt = parser.read(key=target)
            except KktSectionNotFound:
                if not init:
                    click.echo("Kkt section is not found in pyproject.yml.", err=True)
                    sys.exit(1)
                kkt = {}

            api = get_kaggle_api()
            api.authenticate()

            command(api, kkt, pyproject_path, *args, **kwargs)

        return _wrap_click_command(_f, init)

    return _wrapper
