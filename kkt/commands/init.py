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


class KernelType(Enum):
    script = "script"
    notebook = "notebook"


def competition_prompt():
    competition_query = click.prompt("competition", default="", show_default=False)
    competitions = api.competitions_list(search=competition_query)
    for i, c in enumerate(competitions):
        print(i, c)
    competition_index = click.prompt(
        ">", type=int, show_choices=False, prompt_suffix=" "
    )
    return str(competitions[competition_index])


def dataset_prompt():
    dataset_sources = []
    while click.confirm("Would you like to add dataset sources?"):
        dataset_source = click.prompt("dataset source")
        dataset_sources.append(dataset_source)
    return dataset_sources


@click.command()
def init():
    pyproject_path = Path.cwd() / "pyproject.toml"
    parser = KktParser(pyproject_path)

    try:
        kkt = parser.read()
        if not click.confirm(
            "Kkt section is found in pyproject.yml. Do you want to continue?"
        ):
            return
    except KktSectionNotFound:
        pass

    click.echo("Appending Kkt section into your pyproject.toml config.")

    meta_data = {}
    meta_data["competition"] = competition_prompt()
    meta_data["slug"] = click.prompt("slug", type=str)
    meta_data["code_file"] = click.prompt("code_file", default="script.py")
    meta_data["kernel_type"] = click.prompt(
        "kernel_type",
        default=DEFAULT_KKT_CONFIG["meta_data"]["kernel_type"],
        type=KernelType,
    )
    meta_data["is_private"] = click.confirm(
        "is_private", default=DEFAULT_KKT_CONFIG["meta_data"]["is_private"]
    )
    meta_data["enable_gpu"] = click.confirm(
        "enable_gpu", default=DEFAULT_KKT_CONFIG["meta_data"]["enable_gpu"]
    )
    meta_data["enable_internet"] = click.confirm(
        "enable_internet", default=DEFAULT_KKT_CONFIG["meta_data"]["enable_internet"]
    )
    meta_data["dataset_sources"] = dataset_prompt()
    meta_data["competition_sources"] = [meta_data["competition"]]

    kkt_config = {
        "meta_data": meta_data,
    }
    kkt_config["enable_git_tag"] = click.confirm(
        "enable_git_tag", default=DEFAULT_KKT_CONFIG["enable_git_tag"]
    )
    parser.write(kkt_config)
