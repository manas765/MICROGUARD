from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import LoanApplication, User
from app.dependencies import get_current_user
from app.fraud.fraud_detection import build_shared_attribute_graph

router = APIRouter(prefix="/fraud", tags=["fraud"])


@router.get("/graph")
def get_fraud_graph(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("loan_officer", "admin"):
        raise HTTPException(status_code=403, detail="Only loan officers or admins can view the fraud graph")

    all_apps = db.query(LoanApplication).all()

    edges = []
    for a in all_apps:
        if a.guarantor_phone:
            edges.append(("phone", a.guarantor_phone, a.id))
        owner = a.business_profile.owner if a.business_profile else None
        if owner and owner.signup_ip:
            edges.append(("ip", owner.signup_ip, a.id))

    graph = build_shared_attribute_graph(edges)

    app_lookup = {a.id: a for a in all_apps}

    nodes = [
        {
            "id": app_id,
            "business_name": app_lookup[app_id].business_profile.business_name
            if app_lookup[app_id].business_profile else None,
            "requested_amount": app_lookup[app_id].requested_amount,
            "fraud_risk_level": app_lookup[app_id].fraud_risk_level,
            "status": app_lookup[app_id].status,
        }
        for app_id in graph.nodes
        if app_id in app_lookup
    ]

    links = [
        {
            "source": u,
            "target": v,
            "weight": data.get("weight", 1),
            "shared_attributes": data.get("shared_attributes", []),
        }
        for u, v, data in graph.edges(data=True)
    ]

    return {
        "nodes": nodes,
        "links": links,
        "flagged_clusters": sum(1 for comp in _connected_components(graph) if len(comp) >= 3),
    }


def _connected_components(graph):
    import networkx as nx
    return list(nx.connected_components(graph))