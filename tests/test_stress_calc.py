from app.finance.stress_calc import calculate_stress


def test_low_stress_for_healthy_business():
    result = calculate_stress(
        monthly_income_estimate=50000,
        years_operating=5,
        requested_amount=20000,
        term_days=365,
    )
    assert result["stress_band"] == "Low"
    assert result["stress_score"] < 30


def test_high_stress_for_overleveraged_request():
    result = calculate_stress(
        monthly_income_estimate=10000,
        years_operating=0.5,
        requested_amount=100000,
        term_days=30,
    )
    assert result["stress_band"] == "High"
    assert result["stress_score"] >= 60


def test_zero_income_treated_as_maximal_stress():
    result = calculate_stress(
        monthly_income_estimate=0,
        years_operating=3,
        requested_amount=10000,
        term_days=180,
    )
    assert "No monthly income reported" in result["reasons"][0]
    assert result["stress_score"] > 0


def test_short_term_does_not_crash():
    # term_days=0 would divide-by-zero without the max(months, 0.1) guard
    result = calculate_stress(
        monthly_income_estimate=10000,
        years_operating=2,
        requested_amount=5000,
        term_days=0,
    )
    assert isinstance(result["stress_score"], float)


def test_established_business_gets_no_maturity_penalty():
    result = calculate_stress(
        monthly_income_estimate=50000,
        years_operating=10,
        requested_amount=10000,
        term_days=365,
    )
    assert "established track record" in result["reasons"][1]