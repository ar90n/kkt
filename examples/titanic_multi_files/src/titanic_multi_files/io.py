import pandas as pd
from pathlib import Path

DEFAULT_INPUT_DIR = Path.cwd().parent / "input"


def load_dataset(input_dir: Path = DEFAULT_INPUT_DIR):
    train_path = input_dir / "titanic" / "train.csv"
    train = pd.read_csv(train_path)
    test_path = input_dir / "titanic" / "test.csv"
    test = pd.read_csv(test_path)

    return train, test


def load_submission(input_dir: Path = DEFAULT_INPUT_DIR):
    submission_path = input_dir / "titanic" / "gender_submission.csv"
    return pd.read_csv(submission_path)


def save_submission(sub):
    sub.to_csv("submission.csv", index=False)
