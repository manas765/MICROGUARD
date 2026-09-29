import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import AuditLog, User
from app.dependencies import get_current_user
from app.audit.audit_log import verify_chain

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/log")
def get_audit_log(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("loan_officer", "admin"):
        raise HTTPException(status_code=403, detail="Only loan officers or admins can view the audit log")

    entries = db.query(AuditLog).order_by(AuditLog.id.desc()).all()
    return {
        "total": len(entries),
        "entries": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "event_data": json.loads(e.event_data),
                "timestamp": e.timestamp.isoformat(),
                "prev_hash": e.prev_hash,
                "this_hash": e.this_hash,
            }
            for e in entries
        ],
    }


@router.get("/verify")
def verify_audit_log(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("loan_officer", "admin"):
        raise HTTPException(status_code=403, detail="Only loan officers or admins can verify the audit log")

    return verify_chain(db)