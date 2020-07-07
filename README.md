# kkt
kkt is a tool for kaggle kernel management.

[![Actions Status](https://github.com/ar90n/kkt/workflows/Python%20package/badge.svg)](https://github.com/ar90n/kkt/actions)
[![PyPI](https://img.shields.io/pypi/v/kkt.svg)](https://pypi.python.org/pypi/kkt)
[![PythonVersions](https://img.shields.io/pypi/pyversions/kkt.svg)](https://pypi.python.org/pypi/kkt)

## Feature
* Show the status of the latest version
* Push your script or notebook to the Kaggle Kernels
* Pack and emmbedded your library codes into the generated bootstrap codes
* Add bootstrap codes into the head of your script or notebook automatically
* Add git tags whose name is corresponding kernel version
* Set environment variable for your kernels

## Installation
For now, kkt is designed to be used with poetry. So kkt can be installed by the following.

```bash
$ poetry add kkt --dev
```

## Usage

### Set username and token of kaggle-api
Please setup your kaggle-api credentials as following this [article](https://github.com/Kaggle/kaggle-api#api-credentials)

### Setup kkt in your project
Setup this project for [digit-recognizer competition](https://www.kaggle.com/c/digit-recognizer).
In this configuration, we use script.py. If you want to use notebook, kkt also support it.

```bash
$ poetry run kkt init
Appending Kkt section into your pyproject.toml config.
competition: digit
0 digit-recognizer
> 0
slug: kkt-example
code_file [script.py]: script.py
kernel_type [script]: script
is_private [Y/n]: n
enable_gpu [y/N]: n
enable_internet [y/N]: y
Would you like to add dataset sources? [y/N]: n
enable_git_tag [y/N]: n
```

### Create kkt_example package and its driver code.
kkt_example provides random choice solver for digit-recognizer competition.
```bash
$ tree
.
├── kkt_example
│   └── __init__.py
├── poetry.lock
├── pyproject.toml
└── script.py

1 directory, 4 files
```

__init__.py
```python
from pathlib import Path
import random

import pandas as pd

def choice():
    return random.randint(0, 9)

def load_sample_submission():
    path = Path("..") / "input" / "digit-recognizer" / "sample_submission.csv"
    return pd.read_csv(path,  index_col="ImageId")
```

script.py
```python
import kkt_example

submission = kkt_example.load_sample_submission()
for _, row in submission.iterrows():
    row["Label"] = kkt_example.choice()

    submission.to_csv("submission.csv")
```

pyproject.toml
```toml
[tool.poetry]
name = "kkt-example"
version = "0.1.0"
description = ""
authors = ["Masahiro Wada <argon.argon.argon@gmail.com>"]

[tool.poetry.dependencies]
python = "^3.7"
pandas = "^1.0.0"

[tool.poetry.dev-dependencies]
kkt = "^0.3.1"


[tool.kkt]
enable_git_tag = false

[tool.kkt.meta_data]
code_file = "script.py"
competition = "digit-recognizer"
competition_sources = ["digit-recognizer"]
dataset_sources = []
enable_gpu = false
enable_internet = true
is_private = false
kernel_type = "script"
slug = "kkt-example"

[build-system]
requires = ["poetry>=0.12"]
build-backend = "poetry.masonry.api"
```

If you want run script.py in local environmet, please run the following.

```bash
$ poetry run python script.py
$ head submission.csv
ImageId,Label
1,1
2,1
3,0
4,2
5,4
6,8
7,5
8,3
9,2
```

### Push notebook to Kaggle Kernels
```bash
$ poetry run kkt push
ref: /ar90ngas/kkt-example
url: https://www.kaggle.com/ar90ngas/kkt-example
version: 1
```
Please visit [the result](https://www.kaggle.com/ar90ngas/kkt-example).

### Show the status
```bash
$ poetry run kkt status
status: complete
```

## (WIP) Examples
* Simple script example
* Simple notebook example
* Multi code files example
* Environment variable and dataset example

## License
This software is released under the Apache License, see [LICENSE](LICENSE).
