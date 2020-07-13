from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from kaggle import KaggleApi
from kaggle.models.kaggle_models_extended import KernelPushResponse
from kaggle.models.kernel_push_request import KernelPushRequest

from ..exception import KktSectionNotFound
from ..parser import DEFAULT_KKT_CONFIG, KktParser
from .kkt_command import kkt_command


class KernelType(Enum):
    script = "script"
    notebook = "notebook"

    def __str__(self):
        return self.value


def competition_prompt(api: KaggleApi) -> str:
    competition_query = click.prompt("competition", default="", show_default=False)
    competitions = api.competitions_list(search=competition_query)
    for i, c in enumerate(competitions):
        click.echo(f"{i} {c}")
    competition_index = click.prompt(
        ">", type=int, show_choices=False, prompt_suffix=" "
    )
    return str(competitions[competition_index])


def dataset_prompt() -> List:
    dataset_sources = []
    while click.confirm("Would you like to add dataset sources?"):
        dataset_source = click.prompt("dataset source")
        dataset_sources.append(dataset_source)
    return dataset_sources


def init_impl(api: KaggleApi) -> Dict:
    meta_data: Dict[str, Any] = {}
    meta_data["competition"] = competition_prompt(api)
    meta_data["slug"] = click.prompt("slug", type=str)
    meta_data["code_file"] = click.prompt("code_file", default="script.py")
    meta_data["kernel_type"] = str(
        click.prompt(
            "kernel_type",
            default=DEFAULT_KKT_CONFIG["meta_data"]["kernel_type"],
            type=KernelType,
        )
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
    meta_data["enable_constraint"] = click.confirm(
        "enable_constraint",
        default=DEFAULT_KKT_CONFIG["meta_data"]["enable_constraint"],
    )

    kkt_config: Dict[str, Any] = {
        "meta_data": meta_data,
    }
    kkt_config["enable_git_tag"] = click.confirm(
        "enable_git_tag", default=DEFAULT_KKT_CONFIG["enable_git_tag"]
    )
    return kkt_config


def confirm_initialize() -> bool:
    return click.confirm(
        "Kkt section is found in pyproject.yml. Do you want to continue?"
    )


def get_project_name(parser: KktParser) -> Optional[str]:
    return parser.read_all().get("tool", {}).get("poetry", {}).get("name")


def has_package_source(project_root_path: Path, project_name: str) -> bool:
    pkg_dir = project_root_path / project_name
    src_pkg_dir = project_root_path / "src" / project_name
    return pkg_dir.exists() or src_pkg_dir.exists()


def confirm_add_package_source(project_name: str):
    return click.confirm("Would you like to add {project_name} package direcctory?")


def add_package_source(project_root_path: Path, project_name: str) -> None:
    pkg_dir_path = project_root_path / "src" / project_name
    print(pkg_dir_path)
    pkg_dir_path.mkdir(parents=True, exist_ok=True)

    init_file_path = pkg_dir_path / "__init__.py"
    print(init_file_path)
    init_file_path.touch()


@kkt_command(init=True)
def init(
    api: KaggleApi, kkt: Dict, pyproject_path: Path, *args: List, **kwargs: Dict
) -> None:
    if kkt is not None and not confirm_initialize():
        return
    click.echo("Appending Kkt section into your pyproject.toml config.")

    kkt = init_impl(api)

    parser = KktParser(pyproject_path)
    parser.write(kkt)

    project_name = get_project_name(parser)
    print(project_name)
    if project_name is None:
        print("no name")
        return

    project_root_path = pyproject_path.parent
    if has_package_source(project_root_path, project_name):
        print("has")
        return

    if confirm_add_package_source(project_name):
        print("add")
        add_package_source(project_root_path, project_name)
