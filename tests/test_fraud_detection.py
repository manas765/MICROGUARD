from datetime import datetime, timedelta

from app.fraud.fraud_detection import (
    check_rapid_applications,
    check_amount_vs_income,
    check_guarantor_history,
    build_shared_attribute_graph,
    check_cluster_size,
    compute_anomaly_flag,
    assess_fraud,
)


def test_no_flag_for_empty_application_history():
    assert check_rapid_applications([]) is None


def test_flags_rapid_repeat_applications():
    now = datetime.utcnow()
    recent = [now, now - timedelta(minutes=5), now - timedelta(minutes=10)]
    result = check_rapid_applications(recent, window_minutes=60, max_allowed=2)
    assert result is not None
    assert "3 applications" in result


def test_does_not_flag_normal_application_pace():
    now = datetime.utcnow()
    recent = [now - timedelta(days=30), now - timedelta(days=60)]
    assert check_rapid_applications(recent, window_minutes=60, max_allowed=2) is None


def test_flags_implausible_amount_vs_income():
    result = check_amount_vs_income(requested_amount=100000, monthly_income_estimate=5000, threshold=5.0)
    assert result is not None
    assert "x declared monthly income" in result


def test_no_flag_for_reasonable_amount():
    assert check_amount_vs_income(requested_amount=10000, monthly_income_estimate=5000, threshold=5.0) is None


def test_no_income_on_record_flagged():
    result = check_amount_vs_income(requested_amount=10000, monthly_income_estimate=0, threshold=5.0)
    assert "No income on record" in result


def test_flags_guarantor_linked_to_default():
    result = check_guarantor_history("9999999999", {"9999999999", "8888888888"})
    assert result is not None


def test_no_flag_for_clean_guarantor():
    assert check_guarantor_history("1234567890", {"9999999999"}) is None


def test_no_flag_when_no_guarantor_given():
    assert check_guarantor_history(None, {"9999999999"}) is None


def test_shared_attribute_graph_clusters_applications():
    edges = [
        ("phone", "1234567890", 1),
        ("phone", "1234567890", 2),
        ("phone", "1234567890", 3),
        ("ip", "1.2.3.4", 4),
    ]
    graph = build_shared_attribute_graph(edges)
    result = check_cluster_size(graph, application_id=1, size_threshold=3)
    assert result is not None
    assert "cluster of 3" in result


def test_no_cluster_flag_for_isolated_application():
    edges = [("ip", "1.2.3.4", 1)]
    graph = build_shared_attribute_graph(edges)
    assert check_cluster_size(graph, application_id=1, size_threshold=3) is None


def test_weighted_edges_track_shared_attribute_count():
    edges = [
        ("phone", "1234567890", 1),
        ("phone", "1234567890", 2),
        ("ip", "1.2.3.4", 1),
        ("ip", "1.2.3.4", 2),
    ]
    graph = build_shared_attribute_graph(edges)
    edge_data = graph.get_edge_data(1, 2)
    assert edge_data["weight"] == 2
    assert set(edge_data["shared_attributes"]) == {"phone", "ip"}


def test_anomaly_detection_skipped_with_too_few_samples():
    result = compute_anomaly_flag(
        historical_features=[[100, 30, 30]] * 5,
        new_features=[100000, 400, 90],
        min_samples=10,
    )
    assert result is None


def test_anomaly_detection_flags_clear_outlier():
    historical = [[1000 + i, 90, 30 + (i % 5)] for i in range(20)]
    outlier = [500000, 5, 99]
    result = compute_anomaly_flag(historical, outlier, min_samples=10, contamination=0.1)
    assert result is not None


def test_assess_fraud_risk_level_scales_with_flag_count():
    now = datetime.utcnow()
    result_none = assess_fraud(
        recent_application_times=[],
        requested_amount=5000,
        monthly_income_estimate=10000,
        guarantor_phone=None,
        defaulted_guarantor_phones=set(),
        graph=build_shared_attribute_graph([]),
        application_id=1,
        historical_features=[],
        new_features=[5000, 90, 30],
    )
    assert result_none["risk_level"] == "none"
    assert result_none["flags"] == []

    result_high = assess_fraud(
        recent_application_times=[now, now, now],
        requested_amount=1000000,
        monthly_income_estimate=1000,
        guarantor_phone="9999999999",
        defaulted_guarantor_phones={"9999999999"},
        graph=build_shared_attribute_graph([]),
        application_id=1,
        historical_features=[],
        new_features=[1000000, 90, 30],
    )
    assert result_high["risk_level"] == "high"
    assert len(result_high["flags"]) >= 3