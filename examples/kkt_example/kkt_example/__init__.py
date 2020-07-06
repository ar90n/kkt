from pathlib import Path
import random

import pandas as pd


def choice():
    return random.randint(0, 9)


def load_sample_submission():
    path = Path("..") / "input" / "digit-recognizer" / "sample_submission.csv"
    return pd.read_csv(path, index_col="ImageId")
