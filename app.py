import os
import joblib
import boto3
import pandas as pd

from flask import Flask, request, jsonify
from prometheus_client import Counter, generate_latest

app = Flask(__name__)

# ==========================
# S3 Configuration
# ==========================
BUCKET_NAME = "house-price-mlops-models-babuguduru"

MODEL_PATH = "artifacts/model.pkl"
PREPROCESSOR_PATH = "artifacts/preprocessor.pkl"

# ==========================
# Prometheus Metrics
# ==========================
prediction_counter = Counter(
    "prediction_requests_total",
    "Total prediction requests"
)

# ==========================
# Download Artifacts from S3
# ==========================
def download_artifacts():
    os.makedirs("artifacts", exist_ok=True)

    s3 = boto3.client("s3")

    if not os.path.exists(MODEL_PATH):
        print("Downloading model.pkl from S3...")
        s3.download_file(
            BUCKET_NAME,
            "models/model.pkl",
            MODEL_PATH
