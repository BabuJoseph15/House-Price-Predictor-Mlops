from flask import Flask, request, jsonify, Response
import pandas as pd
import time

from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)

from src.pipeline.prediction_pipeline import PredictionPipeline

app = Flask(__name__)

# ==========================
# Prometheus Metrics
# ==========================

PREDICTION_REQUESTS = Counter(
    "prediction_requests_total",
    "Total number of prediction requests"
)

PREDICTION_ERRORS = Counter(
    "prediction_errors_total",
    "Total number of prediction errors"
)

PREDICTION_LATENCY = Histogram(
    "prediction_latency_seconds",
    "Prediction request latency in seconds"
)


# ==========================
# Home Endpoint
# ==========================

@app.route("/")
def home():

    return jsonify({
        "message": "House Price Prediction API is running"
    })


# ==========================
# Health Endpoint
# ==========================

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy"
    })


# ==========================
# Metrics Endpoint
# ==========================

@app.route("/metrics")
def metrics():

    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


# ==========================
# Prediction Endpoint
# ==========================

@app.route("/predict", methods=["POST"])
def predict():

    start_time = time.time()

    PREDICTION_REQUESTS.inc()

    try:

        data = request.get_json()

        input_df = pd.DataFrame([data])

        predictor = PredictionPipeline()

        prediction = predictor.predict(input_df)

        response_time = time.time() - start_time

        PREDICTION_LATENCY.observe(
            response_time
        )

        return jsonify({
            "predicted_house_price": round(
                float(prediction[0]),
                2
            )
        })

    except Exception as e:

        PREDICTION_ERRORS.inc()

        return jsonify({
            "error": str(e)
        }), 500


# ==========================
# Main
# ==========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )
