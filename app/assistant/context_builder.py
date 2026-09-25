"""
Builds the factual context the AI assistant answers from.

The whole point of this module: the assistant should never invent a
number. Every figure it can reference — risk scores, stress scores,
fraud flags, loan health, forecasts — has to come from here, built
directly from real database records. If something isn't in this
context, the assistant is instructed (in app/assistant/llm_client.py's
system prompt) to say it doesn't have that information rather than
guess.
"""


def build_borrower_context(user: dict, profile: dict | None, applications: list[dict], loan_health: list[dict]) -> str:
    lines = [f"Borrower: {user['name']} (age {user.get('age')}, {user.get('gender')}, {user.get('education')})"]

    if profile:
        lines.append(
            f"Business: {profile['business_name']} ({profile['sector']}), "
            f"monthly income estimate {profile['monthly_income_estimate']}, "
            f"operating for {profile['years_operating']} years."
        )
    else:
        lines.append("No business profile has been created yet.")

    if applications:
        lines.append(f"\nLoan applications ({len(applications)} total):")
        for app in applications:
            lines.append(
                f"- Application #{app['id']}: {app['requested_amount']} for '{app['purpose']}', "
                f"{app['term_days']} days, status={app['status']}. "
                f"Risk: {app.get('risk_score')} ({app.get('risk_band')}) - reasons: {app.get('risk_reasons')}. "
                f"Stress: {app.get('stress_score')} ({app.get('stress_band')}) - reasons: {app.get('stress_reasons')}. "
                f"Fraud flags: {app.get('fraud_flags') or 'none'}."
            )
    else:
        lines.append("\nNo loan applications on file.")

    if loan_health:
        lines.append(f"\nActive/past loans ({len(loan_health)} total):")
        for loan in loan_health:
            lines.append(
                f"- Loan #{loan['loan_id']}: {loan['amount_due']} due {loan['due_date']}, "
                f"paid={loan['is_paid']}, health={loan['health_status']}. "
                f"Predicted risk at origination: {loan['predicted_risk_band']} ({loan['predicted_risk_score']}). "
                f"Current dynamic risk: {loan['dynamic_risk_band']} ({loan['dynamic_risk_score']})."
            )

    return "\n".join(lines)


def build_officer_context(alerts_summary: dict) -> str:
    lines = [
        f"Portfolio overview: {alerts_summary['total']} total loans, "
        f"{alerts_summary['alert_count']} active alerts, "
        f"{alerts_summary['diverged_count']} loans where the prediction has diverged from reality."
    ]

    lines.append("\nLoans:")
    for loan in alerts_summary["loans"]:
        lines.append(
            f"- Loan #{loan['loan_id']} ({loan['business_name']}, {loan['purpose']}): "
            f"{loan['amount_due']} due {loan['due_date']}, health={loan['health_status']}. "
            f"Predicted: {loan['predicted_risk_band']} ({loan['predicted_risk_score']}). "
            f"Now: {loan['dynamic_risk_band']} ({loan['dynamic_risk_score']}). "
            f"{'ALERT' if loan['is_alert'] else ''}"
        )

    return "\n".join(lines)