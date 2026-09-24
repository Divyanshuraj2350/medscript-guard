def score(flags: list[dict]) -> dict:
    try:
        if flags is None or not isinstance(flags, list):
            flags = []

        n = len(flags)

        if any(isinstance(f, dict) and f.get("severity") == "CRITICAL" for f in flags):
            overall_risk = "CRITICAL"
        elif any(isinstance(f, dict) and f.get("severity") == "HIGH" for f in flags):
            overall_risk = "HIGH"
        elif any(isinstance(f, dict) and f.get("severity") == "MEDIUM" for f in flags):
            overall_risk = "MEDIUM"
        else:
            overall_risk = "LOW"

        if overall_risk == "CRITICAL":
            summary = f"CRITICAL: {n} issue(s) found. Do not dispense. Immediate physician review required."
        elif overall_risk == "HIGH":
            summary = f"{n} issue(s) found. Pharmacist review required before dispensing."
        elif overall_risk == "MEDIUM":
            summary = f"{n} issue(s) found. Review recommended."
        elif n > 0:
            summary = f"{n} issue(s) found. Low severity."
        else:
            summary = "No issues detected. Safe to dispense."

        output = {
            "overall_risk": overall_risk,
            "flags": flags,
            "summary": summary
        }

        import mlflow
        try:
            with mlflow.start_run(run_name="risk_scoring", nested=True):
                mlflow.log_metric("flags_count", len(flags))
                mlflow.set_tag("overall_risk", output["overall_risk"])
        except Exception as e:
            print(f"MLflow logging error: {e}")

        return output
    except Exception:
        return {
            "overall_risk": "LOW",
            "flags": [],
            "summary": "Scoring error. Manual review required."
        }
