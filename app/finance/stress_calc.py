"""
Calculates a financial stress score for a loan application, based on
a transparent formula rather than a trained model.

Why a formula instead of ML: the historical dataset has labeled loan
*outcomes* (paid off vs. collection), which is what the credit-risk
model in app/ml/ is trained on. It has no label for "financial
stress" as a concept — there's nothing to train or validate a model
against. A rule-based formula here is more honest than dressing up
a guess as a trained model, and it has the side benefit of being
fully transparent by construction: every number in the score can be
traced back to a specific, explainable step.

Call calculate_stress(...) with the applicant's business profile and
the loan being applied for.
"""

REPAYMENT_RATIO_CAP = 0.6  # a monthly repayment at or above 60% of income is treated as maximally stressful
MATURITY_YEARS_THRESHOLD = 2.0  # businesses operating 2+ years get no maturity penalty


def _stress_band(score: float) -> str:
    if score < 30:
        return "Low"
    if score < 60:
        return "Medium"
    return "High"


def calculate_stress(
    monthly_income_estimate: float,
    years_operating: float,
    requested_amount: float,
    term_days: int,
) -> dict:
    """Returns a 0-100 financial stress score, a Low/Medium/High band,
    and plain-language reasons — all derived from a fixed formula, not
    a trained model."""
    reasons = []

    months = max(term_days / 30, 0.1)  # avoid divide-by-zero on a same-day term
    monthly_repayment_estimate = requested_amount / months

    if monthly_income_estimate <= 0:
        repayment_ratio = 1.0
        reasons.append("No monthly income reported, so repayment burden cannot be confirmed as manageable")
    else:
        repayment_ratio = monthly_repayment_estimate / monthly_income_estimate

    repayment_component = min(repayment_ratio / REPAYMENT_RATIO_CAP, 1.0) * 70
    reasons.append(
        f"Estimated monthly repayment (~{monthly_repayment_estimate:.0f}) is "
        f"{repayment_ratio * 100:.0f}% of estimated monthly income"
    )

    maturity_fraction = max(0.0, (MATURITY_YEARS_THRESHOLD - years_operating) / MATURITY_YEARS_THRESHOLD)
    maturity_component = maturity_fraction * 30
    if maturity_component > 0:
        reasons.append(f"Business has been operating for {years_operating:.1f} years, which adds some fragility risk")
    else:
        reasons.append(f"Business has been operating for {years_operating:.1f} years, an established track record")

    score = round(min(repayment_component + maturity_component, 100), 1)

    return {
        "stress_score": score,
        "stress_band": _stress_band(score),
        "reasons": reasons,
    }