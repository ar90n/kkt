from typing import Dict

from kaggle import KaggleApi


def get_slug(api: KaggleApi, meta_data: Dict) -> str:
    return "{}/{}".format(
        api.config_values[api.CONFIG_NAME_USER], meta_data.get("slug")
    )


def get_dataset_slug(api: KaggleApi, meta_data: Dict) -> str:
    slug = get_slug(api, meta_data)
    return f"{slug}-requirements"
