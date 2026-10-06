import joblib
import mlflow
import mlflow.sklearn

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)

from src.components.data_transformation import DataTransformation


class ModelTrainer:

    def initiate_model_trainer(self):

        transformer = DataTransformation()

        X_train, X_test, y_train, y_test = (
            transformer.initiate_data_transformation()
        )

        mlflow.set_experiment(
            "House_Price_Prediction"
        )

        with mlflow.start_run():

            model = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )

            model.fit(
                X_train,
                y_train
            )

            y_pred = model.predict(
                X_test
            )

            r2 = r2_score(
                y_test,
                y_pred
            )

            mae = mean_absolute_error(
                y_test,
                y_pred
            )

            rmse = (
                mean_squared_error(
                    y_test,
                    y_pred
                ) ** 0.5
            )

            mlflow.log_param(
                "n_estimators",
                100
            )

            mlflow.log_metric(
                "r2_score",
                r2
            )

            mlflow.log_metric(
                "mae",
                mae
            )

            mlflow.log_metric(
                "rmse",
                rmse
            )

            mlflow.sklearn.log_model(
                model,
                "random_forest_model"
            )

            joblib.dump(
                model,
                "artifacts/model.pkl"
            )

            print(f"R2 Score : {r2:.4f}")
            print(f"MAE      : {mae:.2f}")
            print(f"RMSE     : {rmse:.2f}")

            print("Model saved successfully")
