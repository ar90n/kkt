from typing import Dict, Iterable

from .bootstrap import create_bootstrap_code


SCRIPT_TEMPLATE: str = """{bootstrap_code}

{script_body}
"""


def create_script_kernel(
    script_body: str,
    pkg_encoded: str,
    pkg_dataset: str,
    env_variables: Dict,
    dependencies: Iterable[str],
    enable_internet: bool = False,
) -> str:
    bootstrap_code = create_bootstrap_code(
        pkg_encoded=pkg_encoded,
        pkg_dataset=pkg_dataset,
        env_variables=env_variables,
        dependencies=dependencies,
        enable_internet=enable_internet,
    )
    return SCRIPT_TEMPLATE.format(
        bootstrap_code=bootstrap_code, script_body=script_body, encoding="utf8"
    )
