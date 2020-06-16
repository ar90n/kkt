import json
from typing import Dict

from .bootstrap import create_bootstrap_code


def erace_all_outputs(notebook: Dict) -> Dict:
    notebook = {**notebook}
    for cell in notebook.get("cells", []):
        if "outputs" in cell and cell["cell_type"] == "code":
            cell["outputs"] = []
    return notebook


def create_bootstrap_cell(
    pkg_encoded: str,
    pkg_dataset: str,
    env_variables: Dict,
    enable_internet: bool = False,
) -> Dict:
    bootstrap_code = create_bootstrap_code(
        pkg_encoded=pkg_encoded,
        pkg_dataset=pkg_dataset,
        env_variables=env_variables,
        enable_internet=enable_internet,
    )
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"trusted": True, "_kg_hide-input": True, "_kg_hide-output": True},
        "outputs": [],
        "source": [bootstrap_code],
    }


def create_notebook_kernel(
    notebook_body: str,
    pkg_encoded: str,
    pkg_dataset: str,
    env_variables: Dict,
    enable_internet: bool = False,
) -> str:
    notebook_obj = erace_all_outputs(json.loads(notebook_body))

    bootstrap_cell = create_bootstrap_cell(
        pkg_encoded=pkg_encoded,
        pkg_dataset=pkg_dataset,
        env_variables=env_variables,
        enable_internet=enable_internet,
    )
    notebook_obj.setdefault("cells", []).insert(0, bootstrap_cell)

    notebook_kernel = json.dumps(notebook_obj)
    return notebook_kernel
