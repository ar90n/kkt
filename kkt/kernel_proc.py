from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
from functools import singledispatch

import click
from kaggle import KaggleApi
from kaggle.models.dataset_new_request import DatasetNewRequest
from kaggle.models.dataset_new_version_request import DatasetNewVersionRequest
from kaggle.models.kaggle_models_extended import (
    DatasetNewResponse,
    DatasetNewVersionResponse,
    KernelPushResponse,
)
from kaggle.models.kernel_push_request import KernelPushRequest

from .resource import get_slug, get_username


@dataclass
class KernelPushParams:
    id_no: Optional[str]
    slug: str
    new_title: Optional[str]
    kernel_type: str
    is_private: Optional[bool]
    enable_gpu: Optional[bool]
    enable_internet: Optional[bool]
    dataset_data_sources: List[str]
    competition_data_sources: List[str]
    kernel_data_sources: List[str]
    category_ids: List[str]

    @classmethod
    def of(cls, api, meta_data: Dict) -> "KernelPushParams":
        id_no = meta_data.get("id_no")
        slug = get_slug(api, meta_data)
        new_title = api.get_or_default(meta_data, "slug", None)
        kernel_type = meta_data.get("kernel_type", "script")
        is_private = api.get_or_default(meta_data, "is_private", None)
        enable_gpu = api.get_or_default(meta_data, "enable_gpu", None)
        enable_internet = api.get_or_default(meta_data, "enable_internet", None)

        dataset_data_sources = api.get_or_default(meta_data, "dataset_sources", [])
        for source in dataset_data_sources:
            api.validate_dataset_string(source)

        competition_data_sources = api.get_or_default(
            meta_data, "competition_sources", []
        )

        kernel_data_sources = api.get_or_default(meta_data, "kernel_sources", [])
        for source in kernel_data_sources:
            api.validate_kernel_string(source)

        category_ids = api.get_or_default(meta_data, "keywords", [])

        return cls(
            id_no=id_no,
            slug=slug,
            new_title=new_title,
            kernel_type=kernel_type,
            is_private=is_private,
            enable_gpu=enable_gpu,
            enable_internet=enable_internet,
            dataset_data_sources=dataset_data_sources,
            competition_data_sources=competition_data_sources,
            kernel_data_sources=kernel_data_sources,
            category_ids=category_ids,
        )


def push(
    api: KaggleApi, params: KernelPushParams, script_body: str
) -> KernelPushResponse:
    """ read the metadata file and kernel files from a notebook, validate
        both, and use Kernel API to push to Kaggle if all is valid.
         Parameters
        ==========
        folder: the path of the folder
    """
    language = "python"
    kernel_push_request = KernelPushRequest(
        id=params.id_no,
        slug=params.slug,
        new_title=params.new_title,
        text=script_body,
        language=language,
        kernel_type=params.kernel_type,
        is_private=params.is_private,
        enable_gpu=params.enable_gpu,
        enable_internet=params.enable_internet,
        dataset_data_sources=params.dataset_data_sources,
        competition_data_sources=params.competition_data_sources,
        kernel_data_sources=params.kernel_data_sources,
        category_ids=params.category_ids,
    )

    result = KernelPushResponse(
        api.process_response(
            api.kernel_push_with_http_info(kernel_push_request=kernel_push_request)
        )
    )
    return result


def status(api: KaggleApi, kernel_slug: str):
    user_name = api.config_values[api.CONFIG_NAME_USER]
    return api.kernel_status(user_name, kernel_slug)


def list_outputs(api: KaggleApi, kernel_slug: str):
    user_name = api.config_values[api.CONFIG_NAME_USER]
    return api.process_response(
        api.kernel_output_with_http_info(user_name, kernel_slug)
    )


def create_dataset(
    api: KaggleApi,
    dataset_slug: str,
    license_name: str,
    target_dir: Path,
    quiet: bool = False,
):
    if len(dataset_slug) < 6 or len(dataset_slug) > 50:
        raise ValueError("The dataset slug must be between 6 and 50 characters")

    owner_slug = get_username(api)
    request = DatasetNewRequest(
        title=dataset_slug,
        slug=dataset_slug,
        owner_slug=owner_slug,
        license_name=license_name,
        subtitle=None,
        description=None,
        files=[],
        is_private=True,
        convert_to_csv=False,
        category_ids=[],
    )
    api.upload_files(request, None, target_dir, quiet)

    result = DatasetNewResponse(
        api.process_response(api.datasets_create_new_with_http_info(request))
    )
    return result


def update_dataset(
    api: KaggleApi,
    dataset_slug: str,
    target_dir: Path,
    quiet=False,
    delete_old_versions=True,
):
    owner_slug = get_username(api)
    request = DatasetNewVersionRequest(
        version_notes="test",
        subtitle=None,
        description=None,
        files=[],
        convert_to_csv=False,
        category_ids=[],
        delete_old_versions=delete_old_versions,
    )
    api.upload_files(request, None, target_dir, quiet)

    result = DatasetNewVersionResponse(
        api.process_response(
            api.datasets_create_version_with_http_info(
                owner_slug, dataset_slug, request
            )
        )
    )
    return result


@singledispatch
def print_response(result: Any) -> None:
    raise NotImplementedError(f"print_response not support {type(result)}")


@print_response.register
def _print_KernelPushResponse(result: KernelPushResponse) -> None:
    if result.error is not None:
        click.echo("error: {}".format(result.error))
    else:
        click.echo("ref: {}".format(result.ref))
        click.echo("url: {}".format(result.url))
        click.echo("version: {}".format(result.versionNumber))


@print_response.register
def _print_DatasetNewResponse(result: DatasetNewResponse) -> None:
    if result.status == "error":
        click.echo("error: {}".format(result.error))
    else:
        click.echo("ref: {}".format(result.ref))
        click.echo("url: {}".format(result.url))


@print_response.register
def _print_DatasetNewVersionResponse(result: DatasetNewVersionResponse) -> None:
    if result.status == "error":
        click.echo("error: {}".format(result.error))
    else:
        click.echo("ref: {}".format(result.ref))
        click.echo("url: {}".format(result.url))
