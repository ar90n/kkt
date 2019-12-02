from pathlib import Path

from .kernels import KERNEL_CREATEORS
from .packaging import poetry_packaging


def get_builder(kernel_type: str, enable_internet: bool=False):
    if kernel_type not in KERNEL_CREATEORS:
        raise ValueError(
            "kernel_type mus be in [{}]: {}".format(
                KERNEL_CREATEORS.keys(), kernel_type
            )
        )

    def _builder(kernel_body_path: Path) -> str:
        pkg_name, pkg_encoded = poetry_packaging()
        kernel_body = kernel_body_path.read_text()
        return KERNEL_CREATEORS[kernel_type](kernel_body, pkg_name, pkg_encoded, enable_internet)

    return _builder
