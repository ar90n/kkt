# mnist_efficientnet
Logistic Regression, Random Forest and XGBoost for titanic.

## Deploy
kkt supports multiple targets. In this example, Logistic Regression is default target. And the target name of Random Forest is rf. And the target name of XGBoost is xgboost.

### Setup project
```
$ poetry install
$ poetry run kkt install
```

### Logistic Regression
```
$ poetry run kkt push
```

### Random Forest
```
$ poetry run kkt push --target .rf
```

### Random Forest with specifying max_depth vis environment variable
kkt embeded environment variables whose prefix is `KKT_` into the bootstrap code.
In the following case, `RF_MAX_DEPTH` is embededed as environment variable.

```
$ KKT_RF_MAX_DEPTH=8 poetry run kkt push --target .rf
```

### XGBoost
```
$ poetry run kkt push --target .xgb
```

## Result
Logistic Regression: https://www.kaggle.com/ar90ngas/titanic-multi-files?scriptVersionId=38885256
Random Forest: https://www.kaggle.com/ar90ngas/titanic-multi-files?scriptVersionId=38886572
Random Forest (max_depth=8): https://www.kaggle.com/ar90ngas/titanic-multi-files?scriptVersionId=38886860
XGBoost:https://www.kaggle.com/ar90ngas/titanic-multi-files?scriptVersionId=38902658
