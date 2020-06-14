from typing import Dict, Callable

from .script_kernel import create_script_kernel
from .notebook_kernel import create_notebook_kernel

KERNEL_CREATEORS: Dict[str, Callable[..., str]] = {
    "script": create_script_kernel,
    "notebook": create_notebook_kernel,
}
