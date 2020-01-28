from typing import Dict, Callable, IO
from pathlib import Path

from .kernels import KERNEL_CREATEORS
from .packaging import poetry_packaging
from ..exception import NotSupportedKernelType

Builder = Callable[[IO[str], Dict], str]


def get_builder(kernel_type: str, enable_internet: bool = False) -> Builder:
    if kernel_type not in KERNEL_CREATEORS:
        raise NotSupportedKernelType(kernel_type)

    def _builder(kernel_body_io: IO[str], env_variables: Dict) -> str:
        pkg_name, pkg_encoded = poetry_packaging()
        kernel_body = kernel_body_io.read()
        return KERNEL_CREATEORS[kernel_type](
            kernel_body, pkg_name, pkg_encoded, env_variables, enable_internet
        )

    return _builder
