import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from titanic_multi_files import io, util
from pathlib import Path

INPUT_DIR = Path("/home/argon/data/kaggle")
train, test = io.load_dataset(INPUT_DIR)

data = util.merge_dataset(train, test)
data["Sex"].replace(["male", "female"], [0, 1], inplace=True)
data["Fare"].fillna(np.mean(data["Fare"]), inplace=True)
data["Age"].fillna(np.mean(data["Age"]), inplace=True)
data["Age"] = (data["Age"] - data["Age"].min()) / (
    data["Age"].max() - data["Age"].min()
)
data["Fare"] = (data["Fare"] - data["Fare"].min()) / (
    data["Fare"].max() - data["Fare"].min()
)
data = pd.concat(
    [
        data,
        pd.get_dummies(data.Embarked, prefix="Embarked"),
        pd.get_dummies(data.Pclass, prefix="Pclass"),
    ],
    axis=1,
)
train, test = util.split_dataset(data)

feature_columns = [
    "Pclass_1",
    "Pclass_2",
    "Pclass_3",
    "Embarked_C",
    "Embarked_Q",
    "Embarked_S",
    "Fare",
    "Parch",
    "SibSp",
    "Age",
    "Sex",
]
x_train = train[feature_columns].values
y_train = train["Survived"].values
x_test = test[feature_columns].values


clf = LogisticRegression(penalty="l2", solver="sag", random_state=0)
clf.fit(x_train, y_train)
y_pred = clf.predict(x_test)

sub = io.load_submission(INPUT_DIR)
sub["Survived"] = y_pred.astype(np.int32)
io.save_submission(sub)
