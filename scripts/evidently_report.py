from pathlib import Path

import pandas as pd


LOG_FILE = Path("logs/predictions.csv")
REPORT_DIR = Path("reports")
REPORT_FILE = REPORT_DIR / "data_drift_report.html"


def load_prediction_logs() -> pd.DataFrame:
    if not LOG_FILE.exists():
        raise FileNotFoundError(
            "File logs/predictions.csv not found. "
            "Run FastAPI and then run: python scripts/load_test.py"
        )

    data = pd.read_csv(LOG_FILE)

    required_columns = [
        "text_length",
        "word_count",
        "prediction",
        "latency_seconds"
    ]

    missing_columns = [column for column in required_columns if column not in data.columns]

    if missing_columns:
        raise ValueError(f"Missing columns in logs/predictions.csv: {missing_columns}")

    data = data[required_columns].copy()

    data["text_length"] = pd.to_numeric(data["text_length"], errors="coerce")
    data["word_count"] = pd.to_numeric(data["word_count"], errors="coerce")
    data["latency_seconds"] = pd.to_numeric(data["latency_seconds"], errors="coerce")
    data["prediction"] = data["prediction"].astype(str)

    data = data.dropna()

    if len(data) < 20:
        raise ValueError(
            "Not enough prediction logs for drift report. "
            "Run: python scripts/load_test.py several times."
        )

    return data


def split_reference_current(data: pd.DataFrame):
    """
    Reference data = older prediction logs.
    Current data = newer prediction logs.

    This allows us to simulate production monitoring:
    we compare recent model inputs and predictions with previous behavior.
    """
    middle = len(data) // 2

    reference_data = data.iloc[:middle].copy()
    current_data = data.iloc[middle:].copy()

    return reference_data, current_data


def generate_report_new_api(reference_data: pd.DataFrame, current_data: pd.DataFrame):
    """
    Evidently newer API.
    """
    from evidently import Dataset
    from evidently import DataDefinition
    from evidently import Report
    from evidently.presets import DataDriftPreset

    schema = DataDefinition(
        numerical_columns=[
            "text_length",
            "word_count",
            "latency_seconds"
        ],
        categorical_columns=[
            "prediction"
        ]
    )

    reference_dataset = Dataset.from_pandas(
        reference_data,
        data_definition=schema
    )

    current_dataset = Dataset.from_pandas(
        current_data,
        data_definition=schema
    )

    report = Report([
        DataDriftPreset()
    ])

    evaluation = report.run(
        current_data=current_dataset,
        reference_data=reference_dataset
    )

    if hasattr(evaluation, "save_html"):
        evaluation.save_html(str(REPORT_FILE))
    elif hasattr(report, "save_html"):
        report.save_html(str(REPORT_FILE))
    else:
        raise RuntimeError("Could not save Evidently HTML report with the new API.")


def generate_report_old_api(reference_data: pd.DataFrame, current_data: pd.DataFrame):
    """
    Evidently older API fallback.
    """
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset
    from evidently.pipeline.column_mapping import ColumnMapping

    column_mapping = ColumnMapping()
    column_mapping.numerical_features = [
        "text_length",
        "word_count",
        "latency_seconds"
    ]
    column_mapping.categorical_features = [
        "prediction"
    ]
    column_mapping.prediction = "prediction"

    report = Report(
        metrics=[
            DataDriftPreset()
        ]
    )

    report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping
    )

    report.save_html(str(REPORT_FILE))


def main():
    REPORT_DIR.mkdir(exist_ok=True)

    data = load_prediction_logs()
    reference_data, current_data = split_reference_current(data)

    try:
        generate_report_new_api(reference_data, current_data)
        api_version = "new Evidently API"
    except Exception as new_api_error:
        print(f"New Evidently API failed: {new_api_error}")
        print("Trying old Evidently API...")
        generate_report_old_api(reference_data, current_data)
        api_version = "old Evidently API"

    print("Evidently drift report generated successfully.")
    print(f"API used: {api_version}")
    print(f"Report path: {REPORT_FILE}")
    print(f"Reference rows: {len(reference_data)}")
    print(f"Current rows: {len(current_data)}")


if __name__ == "__main__":
    main()