from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import click
from kaggle import KaggleApi
from kaggle.models.kaggle_models_extended import KernelPushResponse
from kaggle.models.kernel_push_request import KernelPushRequest

from ..exception import MetaDataNotFound
from ..parser import DEFAULT_KKT_CONFIG, KktParser
from .kkt_command import kkt_command


def status_impl(api: KaggleApi, meta_data: Dict) -> str:
    user_name = api.config_values[api.CONFIG_NAME_USER]
    slug = meta_data.get("slug")
    result = api.kernel_status(user_name, slug)

    message_elms = [f"status: {result['status']}"]
    if result["failureMessage"]:
        message_elms.append(f"message: {result['failureMessage']}")
    message = "\n".join(message_elms)
    return message


@kkt_command()
def status(api: KaggleApi, kkt: Dict, *args: List, **kwargs: Dict) -> None:
    if "meta_data" not in kkt:
        raise MetaDataNotFound()
    meta_data = kkt["meta_data"].value

    message = status_impl(api, meta_data)
    click.echo(message)
