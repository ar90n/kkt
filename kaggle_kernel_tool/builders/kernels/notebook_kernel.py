import json

from .bootstrap import create_bootstrap_code


def erace_all_outputs(notebook: dict):
    notebook = {**notebook}
    for cell in notebook.get("cells", []):
        if "outputs" in cell and cell["cell_type"] == "code":
            cell["outputs"] = []
    return notebook


def create_bootstrap_cell(
    pkg_name: str, pkg_encoded: str, enable_internet: bool = False
):
    bootstrap_code = create_bootstrap_code(
        pkg_name=pkg_name, pkg_encoded=pkg_encoded, enable_internet=enable_internet
    )
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [bootstrap_code],
    }


def create_notebook_kernel(
    notebook_body: str, pkg_name: str, pkg_encoded: str, enable_internet: bool = False
):
    bootstrap_code = create_bootstrap_code(
        pkg_name=pkg_name, pkg_encoded=pkg_encoded, enable_internet=enable_internet
    )

    notebook_obj = erace_all_outputs(json.loads(notebook_body))

    bootstrap_cell = create_bootstrap_cell(
        pkg_name=pkg_name, pkg_encoded=pkg_encoded, enable_internet=enable_internet
    )
    notebook_obj.setdefault("cells", []).insert(0, bootstrap_cell)

    notebook_kernel = json.dumps(notebook_obj)
    return notebook_kernel
