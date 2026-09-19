"""
Fraud detection for loan applications, combining three complementary
approaches:

1. Rule-based flags — transparent, explainable checks (rapid repeat
   applications, requested amount wildly inconsistent with income, a
   guarantor already linked to a defaulted loan). Same philosophy as
   stress_calc.py: no fabricated ML model where a plain rule is more
   honest and just as effective.

2. Graph-based shared-attribute clustering (NetworkX) — connects
   applications that share a signup IP or guarantor phone number.
   A cluster larger than expected is a classic sign of a fraud ring
   (one person or group running multiple fake identities).

3. Isolation Forest anomaly detection — the one genuinely unsupervised
   ML piece here, and deliberately so: there's no historical
   "labeled fraud" dataset to train a real fraud classifier on, so
   claiming one would be dishonest. Isolation Forest needs no fraud
   labels at all — it just flags applications that look statistically
   unusual relative to everything else seen so far, which is a
   legitimate first-layer signal real fraud systems actually use.

None of this is a verdict — every flag is advisory, meant to prompt a
human loan officer to look closer, not to auto-reject anyone.
"""

from datetime import datetime, timedelta

import networkx as nx
import numpy as np
from sklearn.ensemble import IsolationForest


def check_rapid_applications(recent_application_times: list[datetime], window_minutes: int = 60, max_allowed: int = 2) -> str | None:
    if not recent_application_times:
        return None
    cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
    recent_count = sum(1 for t in recent_application_times if t >= cutoff)
    if recent_count > max_allowed:
        return f"{recent_count} applications submitted in the last {window_minutes} minutes (unusually rapid)"
    return None


def check_amount_vs_income(requested_amount: float, monthly_income_estimate: float, threshold: float = 5.0) -> str | None:
    if monthly_income_estimate <= 0:
        return "No income on record to compare against the requested amount"
    ratio = requested_amount / monthly_income_estimate
    if ratio > threshold:
        return f"Requested amount is {ratio:.1f}x declared monthly income (implausibly high)"
    return None


def check_guarantor_history(guarantor_phone: str | None, defaulted_guarantor_phones: set[str]) -> str | None:
    if guarantor_phone and guarantor_phone in defaulted_guarantor_phones:
        return "This guarantor is already linked to a defaulted loan elsewhere"
    return None


def build_shared_attribute_graph(edges: list[tuple[str, str, int]]) -> nx.Graph:
    graph = nx.Graph()
    by_attribute = {}
    for attr_type, attr_value, app_id in edges:
        graph.add_node(app_id)
        key = (attr_type, attr_value)
        by_attribute.setdefault(key, []).append(app_id)

    for app_ids in by_attribute.values():
        for i in range(len(app_ids)):
            for j in range(i + 1, len(app_ids)):
                graph.add_edge(app_ids[i], app_ids[j])

    return graph


def check_cluster_size(graph: nx.Graph, application_id: int, size_threshold: int = 3) -> str | None:
    if application_id not in graph:
        return None
    cluster = nx.node_connected_component(graph, application_id)
    if len(cluster) >= size_threshold:
        return f"Linked to a cluster of {len(cluster)} applications sharing an IP or guarantor"
    return None


def compute_anomaly_flag(
    historical_features: list[list[float]],
    new_features: list[float],
    min_samples: int = 10,
    contamination: float = 0.1,
) -> str | None:
    if len(historical_features) < min_samples:
        return None

    X = np.array(historical_features)
    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(X)

    prediction = model.predict([new_features])[0]
    if prediction == -1:
        return "Statistically unusual compared to other applications on file (amount, term, age combination)"
    return None


def assess_fraud(
    recent_application_times: list[datetime],
    requested_amount: float,
    monthly_income_estimate: float,
    guarantor_phone: str | None,
    defaulted_guarantor_phones: set[str],
    graph: nx.Graph,
    application_id: int,
    historical_features: list[list[float]],
    new_features: list[float],
) -> dict:
    flags = []

    for flag in (
        check_rapid_applications(recent_application_times),
        check_amount_vs_income(requested_amount, monthly_income_estimate),
        check_guarantor_history(guarantor_phone, defaulted_guarantor_phones),
        check_cluster_size(graph, application_id),
        compute_anomaly_flag(historical_features, new_features),
    ):
        if flag:
            flags.append(flag)

    if len(flags) == 0:
        risk_level = "none"
    elif len(flags) == 1:
        risk_level = "low"
    elif len(flags) == 2:
        risk_level = "medium"
    else:
        risk_level = "high"

    return {"flags": flags, "risk_level": risk_level}