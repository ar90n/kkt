import base64
import gzip
import io
import tarfile
from typing import IO, Callable, Dict, Iterable

from ..exception import NotSupportedKernelType
from .kernels import KERNEL_CREATEORS
from .package import Package
from .packaging_system import build_packages

Builder = Callable[[IO[str], str, Dict], str]


def create_encoded_archive(pkgs: Iterable[Package]) -> str:
    tar_output = io.BytesIO()
    with tarfile.TarFile(fileobj=tar_output, mode="w") as tar:
        for pkg in pkgs:
            info = tarfile.TarInfo(name=pkg.name)
            info.size = len(pkg.content)
            tar.addfile(info, io.BytesIO(pkg.content))

    compressed = gzip.compress(tar_output.getvalue(), compresslevel=9)
    return base64.b64encode(compressed).decode("utf-8")


def get_builder(kernel_type: str, enable_internet: bool = False,) -> Builder:
    if kernel_type not in KERNEL_CREATEORS:
        raise NotSupportedKernelType(kernel_type)

    def _builder(kernel_body_io: IO[str], pkg_dataset: str, env_variables: Dict) -> str:
        encoded_archive = create_encoded_archive(build_packages())
        kernel_body = kernel_body_io.read()
        return KERNEL_CREATEORS[kernel_type](
            kernel_body,
            pkg_encoded=encoded_archive,
            pkg_dataset=pkg_dataset,
            env_variables=env_variables,
            enable_internet=enable_internet,
        )

    return _builder
