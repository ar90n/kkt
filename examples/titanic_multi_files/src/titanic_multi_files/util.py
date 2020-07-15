from typing import Tuple
import pandas as pd


def merge_dataset(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([train, test], sort=False)


def split_dataset(data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    train = data.loc[data["Survived"].notnull()]
    test = data.loc[data["Survived"].isnull()]
    return train, test
