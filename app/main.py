import os
import time
import csv
from pathlib import Path
from datetime import datetime, timezone
from typing import List

import mlflow
import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response


# =========================
# MLflow model settings
# =========================

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
MLFLOW_MODEL_URI = os.getenv(
    "MLFLOW_MODEL_URI",
    "models:/ukrainian-review-sentiment-model/6"
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
model = mlflow.pyfunc.load_model(MLFLOW_MODEL_URI)


# =========================
# FastAPI app
# =========================

app = FastAPI(
    title="Ukrainian Review Sentiment Inference API",
    description="HW3 inference service with HW4 monitoring and observability",
    version="4.0.0"
)


# =========================
# Prometheus metrics
# =========================

PREDICTIONS_TOTAL = Counter(
    "ml_predictions_total",
    "Total number of model predictions",
    ["predicted_class"]
)

PREDICTION_LATENCY_SECONDS = Histogram(
    "ml_prediction_latency_seconds",
    "Prediction latency in seconds"
)

PREDICTION_BATCH_SIZE = Histogram(
    "ml_prediction_batch_size",
    "Number of texts in one prediction request"
)

PREDICTION_ERRORS_TOTAL = Counter(
    "ml_prediction_errors_total",
    "Total number of prediction errors"
)


# =========================
# Request / response models
# =========================

class PredictionRequest(BaseModel):
    texts: List[str]


class PredictionResponse(BaseModel):
    predictions: List[str]
    latency_seconds: float
    model_uri: str


# =========================
# Logging predictions to CSV
# =========================

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "predictions.csv"


def save_prediction_logs(texts: List[str], predictions: List[str], latency_seconds: float) -> None:
    LOG_DIR.mkdir(exist_ok=True)

    file_exists = LOG_FILE.exists()

    with LOG_FILE.open("a", newline="", encoding="utf-8") as file:
        fieldnames = [
            "timestamp",
            "text",
            "text_length",
            "word_count",
            "prediction",
            "latency_seconds"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for text, prediction in zip(texts, predictions):
            writer.writerow({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "text": text,
                "text_length": len(text),
                "word_count": len(text.split()),
                "prediction": prediction,
                "latency_seconds": latency_seconds
            })


def run_model_prediction(texts: List[str]):
    """
    The model from MLflow can expect either:
    1. list of strings
    2. pandas DataFrame with text column

    This function supports both variants.
    """
    try:
        raw_predictions = model.predict(texts)
    except Exception:
        input_df = pd.DataFrame({"text": texts})
        raw_predictions = model.predict(input_df)

    if hasattr(raw_predictions, "tolist"):
        predictions = raw_predictions.tolist()
    else:
        predictions = list(raw_predictions)

    return [str(prediction) for prediction in predictions]


# =========================
# API endpoints
# =========================

@app.get("/")
def root():
    return {
        "message": "ML inference service is running",
        "model_uri": MLFLOW_MODEL_URI,
        "docs": "/docs",
        "metrics": "/metrics"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_uri": MLFLOW_MODEL_URI
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    start_time = time.perf_counter()

    try:
        predictions = run_model_prediction(request.texts)

        latency_seconds = time.perf_counter() - start_time

        for prediction in predictions:
            PREDICTIONS_TOTAL.labels(predicted_class=prediction).inc()

        PREDICTION_LATENCY_SECONDS.observe(latency_seconds)
        PREDICTION_BATCH_SIZE.observe(len(request.texts))

        save_prediction_logs(
            texts=request.texts,
            predictions=predictions,
            latency_seconds=latency_seconds
        )

        return {
            "predictions": predictions,
            "latency_seconds": round(latency_seconds, 6),
            "model_uri": MLFLOW_MODEL_URI
        }

    except Exception as error:
        PREDICTION_ERRORS_TOTAL.inc()
        raise error


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )