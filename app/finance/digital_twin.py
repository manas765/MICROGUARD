from datetime import datetime, timedelta


def project_cash_flow(
    monthly_income: float,
    loan_repayments: list[tuple[datetime, float]],
    horizon_months: int = 12,
    income_growth_rate: float = 0.0,
    shock_month: int | None = None,
    shock_pct: float = 0.0,
    extra_monthly_expense: float = 0.0,
    start_date: datetime | None = None,
) -> list[dict]:
    start_date = start_date or datetime.utcnow()
    months = []
    cumulative_balance = 0.0

    for m in range(1, horizon_months + 1):
        month_start = start_date + timedelta(days=30 * (m - 1))
        month_end = start_date + timedelta(days=30 * m)

        projected_income = monthly_income * ((1 + income_growth_rate) ** (m - 1))
        if shock_month == m:
            projected_income *= (1 - shock_pct)

        repayment_due_this_month = sum(
            amount for due_date, amount in loan_repayments if month_start <= due_date < month_end
        )

        net_cash_flow = projected_income - extra_monthly_expense - repayment_due_this_month
        cumulative_balance += net_cash_flow

        months.append(
            {
                "month": m,
                "projected_income": round(projected_income, 2),
                "loan_repayment_due": round(repayment_due_this_month, 2),
                "extra_expense": round(extra_monthly_expense, 2),
                "net_cash_flow": round(net_cash_flow, 2),
                "cumulative_balance": round(cumulative_balance, 2),
            }
        )

    return months


def run_scenarios(
    monthly_income: float,
    loan_repayments: list[tuple[datetime, float]],
    horizon_months: int,
    scenarios: list[dict],
) -> dict:
    results = {}
    for scenario in scenarios:
        name = scenario.get("name", "unnamed")
        results[name] = project_cash_flow(
            monthly_income=monthly_income,
            loan_repayments=loan_repayments,
            horizon_months=horizon_months,
            income_growth_rate=scenario.get("income_growth_rate", 0.0),
            shock_month=scenario.get("shock_month"),
            shock_pct=scenario.get("shock_pct", 0.0),
            extra_monthly_expense=scenario.get("extra_monthly_expense", 0.0),
        )
    return results