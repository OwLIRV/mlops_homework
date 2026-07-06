import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("sqlite:///mlflow.db")

client = MlflowClient()

models = client.search_registered_models()

if not models:
    print("No registered models found in MLflow Model Registry.")
else:
    for model in models:
        print(f"\nRegistered model: {model.name}")

        versions = client.search_model_versions(f"name = '{model.name}'")

        for version in versions:
            print(f"  version: {version.version}")
            print(f"  stage: {version.current_stage}")
            print(f"  status: {version.status}")
            print(f"  source: {version.source}")
            print("-" * 40)