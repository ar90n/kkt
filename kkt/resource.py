from typing import Dict

from kaggle import KaggleApi


def get_username(api: KaggleApi) -> str:
    return api.config_values[api.CONFIG_NAME_USER]


def get_slug(api: KaggleApi, meta_data: Dict) -> str:
    user_name = get_username(api)
    slug = meta_data["slug"]
    return f"{user_name}/{slug}"


def get_dataset_slug(api: KaggleApi, meta_data: Dict) -> str:
    slug = get_slug(api, meta_data)
    return f"{slug}-requirements"
