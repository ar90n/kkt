import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from titanic_multi_files import io, util
from pathlib import Path

train, test = io.load_dataset()

data = util.merge_dataset(train, test)
data["Sex"].replace(["male", "female"], [0, 1], inplace=True)
data["Embarked"].replace(["C", "Q", "S", None], [0, 1, 2, 3], inplace=True)
data["Fare"].fillna(np.mean(data["Fare"]), inplace=True)
data["Age"].fillna(np.mean(data["Age"]), inplace=True)
train, test = util.split_dataset(data)

feature_columns = [
    "Pclass",
    "Embarked",
    "Fare",
    "Parch",
    "SibSp",
    "Age",
    "Sex",
]
x_train = train[feature_columns].values
y_train = train["Survived"].values
x_test = test[feature_columns].values

max_depth = int(os.environ.get("RF_MAX_DEPTH", 2))
crf = RandomForestClassifier(max_depth=max_depth, random_state=0)
crf.fit(x_train, y_train)
y_pred = crf.predict(x_test)

sub = io.load_submission()
sub["Survived"] = y_pred.astype(np.int32)
io.save_submission(sub)
