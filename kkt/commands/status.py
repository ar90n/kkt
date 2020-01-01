from pathlib import Path
from ..utils.parser import KktParser, DEFAULT_KKT_CONFIG
from ..exception import KktSectionNotFound
from enum import Enum

from kaggle import KaggleApi
from kaggle.api_client import ApiClient
from kaggle.models.kaggle_models_extended import KernelPushResponse
from kaggle.models.kernel_push_request import KernelPushRequest

import click

api = KaggleApi(ApiClient())
api.authenticate()


@click.command()
def status():
    pyproject_path = Path.cwd() / "pyproject.toml"
    parser = KktParser(pyproject_path)
    kkt = parser.read()
    meta_data = kkt.get("meta_data")

    user_name = api.config_values[api.CONFIG_NAME_USER]
    slug = meta_data.get("slug")
    result = api.kernel_status(user_name, slug)

    message_elms = [f"status: {result['status']}"]
    if result["failureMessage"]:
        message_elms.append(f"message: {result['failureMessage']}")
    message = "\n".join(message_elms)
    click.echo(message)
