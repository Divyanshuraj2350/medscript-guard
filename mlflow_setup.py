import os
import mlflow

os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
mlflow.set_tracking_uri("./mlflow_runs")
mlflow.set_experiment("medscript-guard")
