"""
Scores a single loan application using the trained credit-risk model.

Import and call `score_application(...)` from wherever a loan
application is created or re-evaluated (e.g. app/routers/loans.py).
The model, explainer, and metadata are loaded once at import time and
reused for every call — retraining (train_model.py) and restarting
the API is how you pick up a new model version.
"""

import json
import os

import joblib
import numpy as np

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

_model = joblib.load(os.path.join(ARTIFACT_DIR, "model.pkl"))
_explainer = joblib.load(os.path.join(ARTIFACT_DIR, "explainer.pkl"))
with open(os.path.join(ARTIFACT_DIR, "metadata.json")) as f:
    _metadata = json.load(f)

FEATURE_COLUMNS = _metadata["feature_columns"]
MODEL_VERSION = _metadata["trained_at"]
EDUCATION_ORDER = _metadata["education_order"]
VALID_GENDERS = {"male", "female"}

FEATURE_LABELS = {
    "requested_amount": "the requested loan amount",
    "term_days": "the loan term length",
    "age": "applicant age",
    "gender": "applicant gender",
    "education": "applicant education level",
    "has_guarantor": "having a guarantor",
}


def _risk_band(score: float) -> str:
    if score < 30:
        return "Low"
    if score < 60:
        return "Medium"
    return "High"


def _confidence(row: dict) -> str:
    """A rough, honest signal for how much the loan officer should
    trust this particular score, given the model was trained on only
    ~500 historical rows."""
    age = row["age"]
    amount = row["requested_amount"]

    if age < 18 or age > 55 or amount > 1200:
        return "low"
    if age < 22 or age > 48 or amount > 1000:
        return "medium"
    return "high"


def _describe_feature_value(base_feature: str, row: dict) -> str:
    """Build a phrase that reflects the applicant's *actual* value for
    this feature, so the reason reads correctly regardless of which
    direction it pushed the score."""
    if base_feature == "has_guarantor":
        return "Having a guarantor" if row["has_guarantor"] else "Not having a guarantor"
    if base_feature == "age":
        return f"Applicant age ({row['age']})"
    if base_feature == "education":
        return f"Education level ({row['education']})"
    if base_feature == "gender":
        return f"Applicant gender ({row['gender']})"
    if base_feature == "requested_amount":
        return f"Requested amount ({row['requested_amount']})"
    if base_feature == "term_days":
        return f"Loan term ({row['term_days']} days)"
    return FEATURE_LABELS.get(base_feature, base_feature).capitalize()


def _plain_language_reasons(shap_values: np.ndarray, feature_names: list, row: dict, top_n: int = 3) -> list:
    """Take SHAP's raw per-feature contribution values for one
    prediction and turn the top contributors into short, readable
    sentences."""
    contributions = list(zip(feature_names, shap_values))
    contributions.sort(key=lambda x: abs(x[1]), reverse=True)

    reasons = []
    for name, value in contributions[:top_n]:
        base_feature = next((f for f in FEATURE_LABELS if f in name), name)
        phrase = _describe_feature_value(base_feature, row)
        direction = "increases" if value > 0 else "decreases"
        reasons.append(f"{phrase} {direction} the risk score")

    return reasons


def _sanitize_inputs(age, gender: str, education: str) -> tuple[dict, bool]:
    """Guards against values the model was never trained on — most
    likely from data entered before validation was added, or from
    direct API calls that bypass the frontend's dropdowns. Falls back
    to a safe default and reports it via the fallback_used flag rather
    than crashing the whole request with a 500."""
    fallback_used = False

    gender_clean = (gender or "").strip().lower()
    if gender_clean not in VALID_GENDERS:
        gender_clean = "male"  # majority class in training data
        fallback_used = True

    education_clean = (education or "").strip()
    matched = next((e for e in EDUCATION_ORDER if e.lower() == education_clean.lower()), None)
    if matched is None:
        matched = "college"  # most common category in training data
        fallback_used = True

    age_clean = age
    if age_clean is None or age_clean < 0:
        age_clean = 30  # median-ish age in training data
        fallback_used = True

    return {"age": age_clean, "gender": gender_clean, "education": matched}, fallback_used


def score_application(
    requested_amount: float,
    term_days: int,
    age: int,
    gender: str,
    education: str,
    has_guarantor: bool,
) -> dict:
    """Returns a dict with a 0-100 risk score, a Low/Medium/High band,
    a confidence level, and plain-language reasons for the score."""
    import pandas as pd

    clean, fallback_used = _sanitize_inputs(age, gender, education)

    row = {
        "requested_amount": requested_amount,
        "term_days": term_days,
        "age": clean["age"],
        "gender": clean["gender"],
        "education": clean["education"],
        "has_guarantor": int(has_guarantor),
    }
    X = pd.DataFrame([row])[FEATURE_COLUMNS]

    probability = _model.predict_proba(X)[0, 1]
    score = round(float(probability) * 100, 1)

    preprocessor = _model.named_steps["preprocess"]
    X_transformed = preprocessor.transform(X)
    feature_names = preprocessor.get_feature_names_out()

    shap_values = _explainer.shap_values(X_transformed)
    reasons = _plain_language_reasons(shap_values[0], feature_names, row)

    confidence = _confidence(row)
    if fallback_used:
        confidence = "low"
        reasons.insert(0, "Some profile details were missing or unrecognized, so this score used default assumptions")

    return {
        "risk_score": score,
        "risk_band": _risk_band(score),
        "confidence": confidence,
        "reasons": reasons,
        "model_version": MODEL_VERSION,
    }