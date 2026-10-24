import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np

from app import create_app


class MockPreprocessor:

    def transform(self, dataframe):
        return np.array([[1.0, 2.0, 3.0]])


class MockModel:

    def predict(self, dataframe):
        return [431942.36]


app = create_app(
    model=MockModel(),
    preprocessor=MockPreprocessor()
)

client = app.test_client()


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert (
        b"House Price Prediction Platform"
        in response.data
    )


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"


def test_metrics():

    response = client.get("/metrics")

    assert response.status_code == 200


def test_predict_success():

    payload = {
        "longitude": -122.23,
        "latitude": 37.88,
        "housing_median_age": 41,
        "total_rooms": 880,
        "total_bedrooms": 129,
        "population": 322,
        "households": 126,
        "median_income": 8.3252,
        "ocean_proximity": "NEAR BAY"
    }

    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "predicted_house_price" in data

    assert (
        data["predicted_house_price"]
        == 431942.36
    )


def test_predict_missing_columns():

    response = client.post(
        "/predict",
        json={}
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "error" in data
