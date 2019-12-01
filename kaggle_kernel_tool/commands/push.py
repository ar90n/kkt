import os
from pathlib import Path

import click
from kaggle import KaggleApi
from kaggle.api_client import ApiClient
from kaggle.models.kaggle_models_extended import KernelPushResponse
from kaggle.models.kernel_push_request import KernelPushRequest
from slugify import slugify

from ..builders import get_builder
from ..repo import Repo
from ..utils.parser import KktParser

api = KaggleApi(ApiClient())
api.authenticate()


def kernels_push(api, meta_data, script_body):
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


def create_kernel_body(meta_data):
    enable_internet = meta_data.get("enable_internet", False)
    kernel_type = meta_data.get("kernel_type", "script")
    code_file_path = Path(meta_data.get("code_file", "main.py"))
    if not code_file_path.is_absolute():
        code_file_path = Path.cwd() / code_file_path

    kernel_builder = get_builder(kernel_type, enable_internet)
    return kernel_builder(code_file_path)


def push_impl(meta_data):
    kernel_body = create_kernel_body(meta_data)
    return kernels_push(api, meta_data, kernel_body)

def dump_push_result(result: KernelPushResponse) -> None:
    print("ref: {}".format(result.ref))
    print("url: {}".format(result.url))
    print("version: {}".format(result.versionNumber))

@click.command()
def push():
    pyproject_path = Path.cwd() / "pyproject.toml"
    parser = KktParser(pyproject_path)
    kkt = parser.read()
    meta_data = kkt.get("meta_data")

    repo = Repo(Path.cwd())
    enable_git_tag = kkt.get("enable_git_tag")
    if enable_git_tag:
        repo.validate()

    result = push_impl(meta_data)
    dump_push_result(result)

    if enable_git_tag:
        repo.attach_version_tag(r.versionNumber)
