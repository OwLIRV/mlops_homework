import argparse
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def load_label_studio_json(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as file:
        items = json.load(file)

    rows = []

    for item in items:
        text = item.get("data", {}).get("text", "")

        label = None
        annotations = item.get("annotations", [])

        if annotations:
            results = annotations[0].get("result", [])
            if results:
                value = results[0].get("value", {})
                choices = value.get("choices", [])
                if choices:
                    label = choices[0]

        if text and label:
            rows.append({"text": text, "label": label})

    return pd.DataFrame(rows)


def load_dataset(path: str) -> pd.DataFrame:
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    elif path.endswith(".json"):
        df = load_label_studio_json(path)
    else:
        raise ValueError("Підтримуються тільки .csv або .json файли")

    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("У датасеті мають бути колонки text та label")

    df = df.dropna(subset=["text", "label"])

    return df


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data-path",
        default="data/labeled/reviews_labeled_v2.json",
        help="Шлях до датасету",
    )

    parser.add_argument(
        "--experiment-name",
        default="sentiment-classification-training",
        help="Назва експерименту в MLflow",
    )

    parser.add_argument(
        "--registered-model-name",
        default="ukrainian-review-sentiment-model",
        help="Назва моделі в MLflow Model Registry",
    )

    parser.add_argument("--max-features", type=int, default=1000)
    parser.add_argument("--ngram-max", type=int, default=1)
    parser.add_argument("--c", type=float, default=1.0)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)

    args = parser.parse_args()

    Path("models").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment(args.experiment_name)

    df = load_dataset(args.data_path)

    
    
    print("=" * 50)
    print("Dataset loaded")
    print("Dataset size:", len(df))
    print("Labels:", df["label"].unique())
    print("Training parameters:")
    print("max_features:", args.max_features)
    print("ngram_max:", args.ngram_max)
    print("C:", args.c)
    print("test_size:", args.test_size)
    print("random_state:", args.random_state)
    print("=" * 50)

    X = df["text"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=y,
    )

    model = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=args.max_features,
                    ngram_range=(1, args.ngram_max),
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    C=args.c,
                    max_iter=1000,
                    random_state=args.random_state,
                ),
            ),
        ]
    )

    run_name = f"lr_c_{args.c}_features_{args.max_features}_ngram_{args.ngram_max}"

    with mlflow.start_run(run_name=run_name):
        mlflow.log_param("model_type", "TF-IDF + LogisticRegression")
        mlflow.log_param("data_path", args.data_path)
        mlflow.log_param("max_features", args.max_features)
        mlflow.log_param("ngram_range", f"1-{args.ngram_max}")
        mlflow.log_param("C", args.c)
        mlflow.log_param("test_size", args.test_size)
        mlflow.log_param("random_state", args.random_state)
        mlflow.log_param("dataset_size", len(df))

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_weighted", f1)
        mlflow.log_metric("precision_weighted", precision)
        mlflow.log_metric("recall_weighted", recall)

        report = classification_report(y_test, y_pred, zero_division=0)
        report_path = "reports/classification_report.txt"

        with open(report_path, "w", encoding="utf-8") as file:
            file.write(report)

        mlflow.log_artifact(report_path)

        labels = sorted(y.unique())

        ConfusionMatrixDisplay.from_predictions(
            y_test,
            y_pred,
            display_labels=labels,
            xticks_rotation=45,
        )

        plt.tight_layout()
        cm_path = "reports/confusion_matrix.png"
        plt.savefig(cm_path)
        plt.close()

        mlflow.log_artifact(cm_path)

        local_model_path = "models/sentiment_model.joblib"
        joblib.dump(model, local_model_path)
        mlflow.log_artifact(local_model_path)

        mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            registered_model_name=args.registered_model_name,
        )

        print("Training finished")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"F1 weighted: {f1:.4f}")
        print(f"Precision weighted: {precision:.4f}")
        print(f"Recall weighted: {recall:.4f}")


if __name__ == "__main__":
    main()