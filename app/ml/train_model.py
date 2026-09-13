"""
Trains MICROGUARD's credit-risk model.

Run this any time you have new/updated historical loan outcome data
(e.g. once you have real loans from the live app that have actually
been paid off or defaulted). Just re-run this file — it will retrain
from scratch and overwrite the saved model artifacts.

Usage:
    python -m app.ml.train_model
"""

import json
import os
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.utils.class_weight import compute_sample_weight

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "MF Bank loan Dataset.xlsx",
)

# Education has a natural order — encoding it as an ordinal (0,1,2,3)
# instead of one-hot lets the model learn "more education = ..." as a
# single smooth relationship instead of four unrelated categories.
EDUCATION_ORDER = ["High School or Below", "college", "Bachelor Degree", "Master or Above"]

FEATURE_COLUMNS = ["requested_amount", "term_days", "age", "gender", "education", "has_guarantor"]


def load_and_prepare_data() -> pd.DataFrame:
    """Load the historical dataset and map it onto the same feature
    names/shapes that the live app's signup + loan application forms
    produce, so training and inference are consistent."""
    df = pd.read_excel(DATASET_PATH)

    prepared = pd.DataFrame()
    prepared["requested_amount"] = df["Principal"]
    prepared["term_days"] = df["terms"]
    prepared["age"] = df["age"]
    prepared["gender"] = df["Gender"].str.lower()
    prepared["education"] = df["Highest Education"]

    # 15 rows have a missing Guarantor value. The app's own loan
    # application form defaults has_guarantor to False when the
    # applicant doesn't provide one, so treating missing historical
    # values the same way keeps training and live behavior consistent.
    prepared["has_guarantor"] = (df["Guarantor"].fillna("No") == "Yes").astype(int)

    # Lenient "good loan" definition (matches project decision):
    # only COLLECTION counts as risky; PAIDOFF and COLLECTION_PAIDOFF
    # both count as good, since the borrower did eventually pay.
    prepared["is_risky"] = (df["loan_status"] == "COLLECTION").astype(int)

    return prepared


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "education",
                OrdinalEncoder(categories=[EDUCATION_ORDER]),
                ["education"],
            ),
            (
                "gender",
                OneHotEncoder(drop="if_binary", handle_unknown="ignore"),
                ["gender"],
            ),
        ],
        remainder="passthrough",  # requested_amount, term_days, age, has_guarantor pass through unchanged
    )

    model = GradientBoostingClassifier(
        n_estimators=150,
        max_depth=3,
        learning_rate=0.05,
        random_state=42,
    )

    return Pipeline(steps=[("preprocess", preprocessor), ("model", model)])


def cross_validate(df: pd.DataFrame) -> dict:
    """Stratified 5-fold CV. With only ~500 rows, a single train/test
    split would give a noisy, unreliable performance estimate — CV
    averages over 5 different splits so the reported numbers actually
    mean something."""
    X = df[FEATURE_COLUMNS]
    y = df["is_risky"]

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    metrics = {"accuracy": [], "precision": [], "recall": [], "f1": [], "roc_auc": []}

    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        pipeline = build_pipeline()
        sample_weight = compute_sample_weight("balanced", y_train)
        pipeline.fit(X_train, y_train, model__sample_weight=sample_weight)

        preds = pipeline.predict(X_test)
        probs = pipeline.predict_proba(X_test)[:, 1]

        metrics["accuracy"].append(accuracy_score(y_test, preds))
        metrics["precision"].append(precision_score(y_test, preds, zero_division=0))
        metrics["recall"].append(recall_score(y_test, preds, zero_division=0))
        metrics["f1"].append(f1_score(y_test, preds, zero_division=0))
        metrics["roc_auc"].append(roc_auc_score(y_test, probs))

    return {k: {"mean": float(np.mean(v)), "std": float(np.std(v))} for k, v in metrics.items()}


def train_final_model(df: pd.DataFrame) -> Pipeline:
    X = df[FEATURE_COLUMNS]
    y = df["is_risky"]
    sample_weight = compute_sample_weight("balanced", y)

    pipeline = build_pipeline()
    pipeline.fit(X, y, model__sample_weight=sample_weight)
    return pipeline


def build_explainer(pipeline: Pipeline, df: pd.DataFrame):
    """SHAP explainer built on the final model's preprocessed training
    data, so at inference time we can say *why* a specific application
    got its score, not just what the score is."""
    preprocessor = pipeline.named_steps["preprocess"]
    model = pipeline.named_steps["model"]
    X_transformed = preprocessor.transform(df[FEATURE_COLUMNS])
    explainer = shap.TreeExplainer(model)
    return explainer, X_transformed


def main():
    print("Loading and preparing historical loan data...")
    df = load_and_prepare_data()
    print(f"  {len(df)} rows, {df['is_risky'].mean():.1%} flagged risky")

    print("\nRunning stratified 5-fold cross-validation...")
    cv_metrics = cross_validate(df)
    for name, stats in cv_metrics.items():
        print(f"  {name:>10}: {stats['mean']:.3f} (+/- {stats['std']:.3f})")

    print("\nTraining final model on full dataset...")
    pipeline = train_final_model(df)

    print("Building SHAP explainer...")
    explainer, _ = build_explainer(pipeline, df)

    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    joblib.dump(pipeline, os.path.join(ARTIFACT_DIR, "model.pkl"))
    joblib.dump(explainer, os.path.join(ARTIFACT_DIR, "explainer.pkl"))

    metadata = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_training_rows": len(df),
        "feature_columns": FEATURE_COLUMNS,
        "education_order": EDUCATION_ORDER,
        "cv_metrics": cv_metrics,
    }
    with open(os.path.join(ARTIFACT_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved model, explainer, and metadata to {ARTIFACT_DIR}")


if __name__ == "__main__":
    main()