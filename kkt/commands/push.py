import os
import re
from pathlib import Path
from typing import Dict

import click
from kaggle import KaggleApi
from kaggle.api_client import ApiClient
from kaggle.models.kaggle_models_extended import KernelPushResponse
from kaggle.models.kernel_push_request import KernelPushRequest
from slugify import slugify

from .kkt_command import kkt_command
from ..builders import get_builder
from ..repo import Repo
from ..exception import MetaDataNotFound


def kernels_push(
    api: KaggleApi, meta_data: Dict, script_body: str
) -> KernelPushResponse:
    """ read the metadata file and kernel files from a notebook, validate
        both, and use Kernel API to push to Kaggle if all is valid.
         Parameters
        ==========
        folder: the path of the folder
    """
    slug = "{}/{}".format(
        api.config_values[api.CONFIG_NAME_USER], meta_data.get("slug")
    )
    id_no = meta_data.get("id_no")

    language = "python"

    kernel_type = meta_data.get("kernel_type", "script")

    dataset_sources = api.get_or_default(meta_data, "dataset_sources", [])
    for source in dataset_sources:
        api.validate_dataset_string(source)

    kernel_sources = api.get_or_default(meta_data, "kernel_sources", [])
    for source in kernel_sources:
        api.validate_kernel_string(source)

    kernel_push_request = KernelPushRequest(
        id=id_no,
        slug=slug,
        new_title=api.get_or_default(meta_data, "slug", None),
        text=script_body,
        language=language,
        kernel_type=kernel_type,
        is_private=api.get_or_default(meta_data, "is_private", None),
        enable_gpu=api.get_or_default(meta_data, "enable_gpu", None),
        enable_internet=api.get_or_default(meta_data, "enable_internet", None),
        dataset_data_sources=dataset_sources,
        competition_data_sources=api.get_or_default(
            meta_data, "competition_sources", []
        ),
        kernel_data_sources=kernel_sources,
        category_ids=api.get_or_default(meta_data, "keywords", []),
    )

    result = KernelPushResponse(
        api.process_response(
            api.kernel_push_with_http_info(kernel_push_request=kernel_push_request)
        )
    )
    return result


def create_kernel_body(meta_data: Dict, env_variables: Dict) -> str:
    enable_internet = meta_data.get("enable_internet", False)
    kernel_type = meta_data.get("kernel_type", "script")
    code_file_path = Path(meta_data.get("code_file", "main.py"))
    if not code_file_path.is_absolute():
        code_file_path = Path.cwd() / code_file_path

    kernel_builder = get_builder(kernel_type, enable_internet)
    with code_file_path.open() as fp:
        return kernel_builder(fp, env_variables)


def push_impl(
    api: KaggleApi, meta_data: Dict, env_variables: Dict
) -> KernelPushResponse:
    kernel_body = create_kernel_body(meta_data, env_variables)
    return kernels_push(api, meta_data, kernel_body)


def dump_push_result(result: KernelPushResponse) -> None:
    if result.error is not None:
        print("error: {}".format(result.error))
    else:
        print("ref: {}".format(result.ref))
        print("url: {}".format(result.url))
        print("version: {}".format(result.versionNumber))


def merge_cli_args(meta_data: Dict, cli_args: Dict) -> Dict:
    valid_args = {k: v for k, v in cli_args.items() if v is not None}
    return {**meta_data, **valid_args}


def get_env_variables(env_variables: Dict) -> Dict:
    result = {**env_variables}
    for k, v in os.environ.items():
        m = re.match(r"^KKT_(.+)$", k)
        if m:
            update_key = m.groups()[0]
            result[update_key] = v
    return result


@click.command()
@click.option("--code-file", type=click.Path(exists=True))
@click.option("--enable-gpu", type=bool)
@click.option("--enable-internet", type=bool)
@click.option("--is-private", type=bool)
@kkt_command()
def push(api: KaggleApi, kkt: Dict, pyproject_path: Path, **kwargs: Dict) -> None:
    repo = Repo(pyproject_path.parent)
    enable_git_tag: bool = kkt.get("enable_git_tag", False)
    if enable_git_tag:
        repo.validate()

    if "meta_data" not in kkt:
        raise MetaDataNotFound()
    meta_data = kkt["meta_data"].value

    meta_data = merge_cli_args(meta_data, kwargs)
    env_variables = get_env_variables(kkt.get("environment_variables", {}))

    result = push_impl(api, meta_data, env_variables)
    dump_push_result(result)

    if enable_git_tag and result.versionNumber:
        repo.attach_version_tag(result.versionNumber, meta_data, env_variables)
