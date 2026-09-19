"""
Continuous monitoring: compares what the credit-risk model predicted
at loan origination against what's actually happening as the loan
plays out, and computes an adjusted "dynamic" risk score from real
repayment behavior.

Deliberately rule-based, not a retrained model — there isn't yet
enough real repayment-outcome data from this app's own users to
retrain the credit model on (it's still trained on the historical
Kaggle dataset). A transparent adjustment formula is honest about
that; a "retrained" model with a handful of real repayments behind
it would not be.

DUE_SOON_WINDOW_DAYS = how many days before a due date counts as an
early warning worth surfacing, before it's actually overdue.
"""

from datetime import datetime, timedelta

DUE_SOON_WINDOW_DAYS = 3
OVERDUE_PENALTY_PER_DAY = 3
OVERDUE_PENALTY_CAP = 40
LATE_PENALTY_PER_DAY = 2
LATE_PENALTY_CAP = 15
ON_TIME_REWARD = 5


def compute_loan_health(due_date: datetime, is_paid: bool, paid_at: datetime | None, now: datetime | None = None) -> dict:
    now = now or datetime.utcnow()

    if is_paid:
        if paid_at and paid_at <= due_date:
            return {"status": "paid_on_time", "days_late": 0}
        days_late = (paid_at - due_date).days if paid_at else 0
        return {"status": "paid_late", "days_late": max(days_late, 0)}

    if now > due_date:
        days_overdue = (now - due_date).days
        return {"status": "overdue", "days_overdue": days_overdue}

    days_until_due = (due_date - now).days
    if days_until_due <= DUE_SOON_WINDOW_DAYS:
        return {"status": "due_soon", "days_until_due": days_until_due}
    return {"status": "on_track", "days_until_due": days_until_due}


def compute_dynamic_risk_score(original_risk_score: float, health: dict) -> float:
    status = health["status"]

    if status == "overdue":
        penalty = min(health["days_overdue"] * OVERDUE_PENALTY_PER_DAY, OVERDUE_PENALTY_CAP)
        return round(min(100, original_risk_score + penalty), 1)

    if status == "paid_late":
        penalty = min(health["days_late"] * LATE_PENALTY_PER_DAY, LATE_PENALTY_CAP)
        return round(min(100, original_risk_score + penalty), 1)

    if status == "paid_on_time":
        return round(max(0, original_risk_score - ON_TIME_REWARD), 1)

    return round(original_risk_score, 1)


def _band(score: float) -> str:
    if score < 30:
        return "Low"
    if score < 60:
        return "Medium"
    return "High"


def assess_loan(original_risk_score: float, original_risk_band: str, due_date: datetime, is_paid: bool, paid_at: datetime | None, now: datetime | None = None) -> dict:
    health = compute_loan_health(due_date, is_paid, paid_at, now)
    dynamic_score = compute_dynamic_risk_score(original_risk_score, health)
    dynamic_band = _band(dynamic_score)

    return {
        "health_status": health["status"],
        "health_detail": {k: v for k, v in health.items() if k != "status"},
        "predicted_risk_score": original_risk_score,
        "predicted_risk_band": original_risk_band,
        "dynamic_risk_score": dynamic_score,
        "dynamic_risk_band": dynamic_band,
        "prediction_diverged": dynamic_band != original_risk_band,
        "is_alert": health["status"] in ("overdue", "due_soon"),
    }