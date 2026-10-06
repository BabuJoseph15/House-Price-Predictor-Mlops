import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


class DataTransformation:

    def initiate_data_transformation(self):

        train_df = pd.read_csv("artifacts/train.csv")
        test_df = pd.read_csv("artifacts/test.csv")

        X_train = train_df.drop("median_house_value", axis=1)
        y_train = train_df["median_house_value"]

        X_test = test_df.drop("median_house_value", axis=1)
        y_test = test_df["median_house_value"]

        numeric_features = X_train.select_dtypes(
            exclude=["object"]
        ).columns

        categorical_features = X_train.select_dtypes(
            include=["object"]
        ).columns

        numeric_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ]
        )

        categorical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore"))
            ]
        )

        preprocessor = ColumnTransformer(
            [
                ("num", numeric_pipeline, numeric_features),
                ("cat", categorical_pipeline, categorical_features)
            ]
        )

        X_train_processed = preprocessor.fit_transform(X_train)
        X_test_processed = preprocessor.transform(X_test)

        joblib.dump(
            preprocessor,
            "artifacts/preprocessor.pkl"
        )

        print("Data Transformation Completed")

        return (
            X_train_processed,
            X_test_processed,
            y_train,
            y_test
        )


if __name__ == "__main__":
    obj = DataTransformation()
    obj.initiate_data_transformation()
