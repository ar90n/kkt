from .bootstrap import create_bootstrap_code


SCRIPT_TEMPLATE: str = """{bootstrap_code}

{script_body}
"""


def create_script_kernel(
    script_body: str, pkg_name: str, pkg_encoded: str, enable_internet: bool = False
):
    bootstrap_code = create_bootstrap_code(
        pkg_name=pkg_name, pkg_encoded=pkg_encoded, enable_internet=enable_internet
    )
    return SCRIPT_TEMPLATE.format(
        bootstrap_code=bootstrap_code, script_body=script_body, encoding="utf8"
    )
