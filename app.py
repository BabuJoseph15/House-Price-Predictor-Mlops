import os
import sys
import boto3
import joblib
import pandas as pd

from flask import Flask, request, jsonify
from prometheus_client import Counter, generate_latest


BUCKET_NAME = "house-price-mlops-models-babuguduru"

MODEL_PATH = "artifacts/model.pkl"
PREPROCESSOR_PATH = "artifacts/preprocessor.pkl"


prediction_counter = Counter(
    "prediction_requests_total",
    "Total prediction requests"
)


def download_artifacts():

    os.makedirs("artifacts", exist_ok=True)

    s3 = boto3.client("s3")

    if not os.path.exists(MODEL_PATH):
        print("Downloading model.pkl from S3...")
        s3.download_file(
            BUCKET_NAME,
            "models/model.pkl",
            MODEL_PATH
        )

    if not os.path.exists(PREPROCESSOR_PATH):
        print("Downloading preprocessor.pkl from S3...")
        s3.download_file(
            BUCKET_NAME,
            "models/preprocessor.pkl",
            PREPROCESSOR_PATH
        )


def load_dependencies():

    download_artifacts()

    model = joblib.load(MODEL_PATH)

    preprocessor = joblib.load(PREPROCESSOR_PATH)

    return model, preprocessor


def create_app(model=None, preprocessor=None):

    app = Flask(__name__)

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "message": "House Price Prediction API is running"
        })

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy"
        })

    @app.route("/metrics", methods=["GET"])
    def metrics():
        return generate_latest(), 200, {
            "Content-Type": "text/plain"
        }

    @app.route("/predict", methods=["POST"])
    def predict():

        try:

            prediction_counter.inc()

            nonlocal model
            nonlocal preprocessor

            if model is None or preprocessor is None:
                model, preprocessor = load_dependencies()

            json_data = request.get_json()

            required_columns = [
                "longitude",
                "latitude",
                "housing_median_age",
                "total_rooms",
                "total_bedrooms",
                "population",
                "households",
                "median_income",
                "ocean_proximity"
            ]

            missing_columns = (
                set(required_columns)
                - set(json_data.keys())
            )

            if missing_columns:
                return jsonify({
                    "error": f"columns are missing: {missing_columns}"
                }), 400

            input_df = pd.DataFrame([json_data])

            transformed_data = preprocessor.transform(input_df)

            prediction = model.predict(transformed_data)

            return jsonify({
                "predicted_house_price": round(
                    float(prediction[0]),
                    2
                )
            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )
