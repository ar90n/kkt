from pathlib import Path

import click


@click.command()
def init():
    pyproject_path = Path.cwd() / "pyproject.toml"
