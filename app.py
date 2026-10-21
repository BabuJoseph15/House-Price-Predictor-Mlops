import mlflow.pyfunc
import pandas as pd

from flask import Flask, request, jsonify
from prometheus_client import Counter, generate_latest

app = Flask(__name__)

MODEL_URI = "models:/HousePriceModel@production"

prediction_counter = Counter(
    "prediction_requests_total",
    "Total prediction requests"
)

model = None


def load_model():
    global model

    if model is None:
        print(
            f"Loading model from MLflow Registry: {MODEL_URI}"
        )

        model = mlflow.pyfunc.load_model(
            MODEL_URI
        )

    return model


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

        model = load_model()

        payload = request.get_json()

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
            - set(payload.keys())
        )

        if missing_columns:
            return jsonify({
                "error":
                f"columns are missing: {missing_columns}"
            }), 400

        input_df = pd.DataFrame([payload])

        prediction = model.predict(input_df)

        return jsonify({
            "predicted_house_price":
            round(float(prediction[0]), 2)
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )
