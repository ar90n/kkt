from pathlib import Path

import torch
import pandas as pd
import numpy as np


def load_train_data(root: Path):
    train_data_path = root / "train.csv"
    train_data = pd.read_csv(train_data_path)

    labels = train_data["label"].values
    data = train_data.drop("label", axis=1).values.reshape(-1, 1, 28, 28)

    train_x = torch.FloatTensor(data).expand(-1, 3, 28, 28)
    train_y = torch.LongTensor(labels.tolist())
    return train_x, train_y


def load_test_data(root: Path):
    test_data_path = root / "test.csv"
    test_data = pd.read_csv(test_data_path).values.reshape(-1, 1, 28, 28)

    return torch.FloatTensor(test_data).expand(-1, 3, 28, 28)


def save_result(result):
    np.savetxt(
        "submission.csv",
        np.dstack((np.arange(1, result.size + 1), result))[0],
        "%d,%d",
        header="ImageId,Label",
        comments="",
    )
