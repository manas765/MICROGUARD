import hashlib
import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import AuditLog

GENESIS_HASH = "0" * 64


def _compute_hash(prev_hash: str, event_type: str, event_data: str, timestamp: datetime) -> str:
    payload = f"{prev_hash}|{event_type}|{event_data}|{timestamp.isoformat()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record_event(db: Session, event_type: str, event_data: dict) -> AuditLog:
    last_entry = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    prev_hash = last_entry.this_hash if last_entry else GENESIS_HASH

    timestamp = datetime.utcnow()
    event_data_str = json.dumps(event_data, default=str, sort_keys=True)
    this_hash = _compute_hash(prev_hash, event_type, event_data_str, timestamp)

    entry = AuditLog(
        event_type=event_type,
        event_data=event_data_str,
        timestamp=timestamp,
        prev_hash=prev_hash,
        this_hash=this_hash,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def verify_chain(db: Session) -> dict:
    entries = db.query(AuditLog).order_by(AuditLog.id.asc()).all()
    prev_hash = GENESIS_HASH

    for entry in entries:
        expected_hash = _compute_hash(prev_hash, entry.event_type, entry.event_data, entry.timestamp)
        if entry.prev_hash != prev_hash or entry.this_hash != expected_hash:
            return {"valid": False, "broken_at_id": entry.id, "event_type": entry.event_type}
        prev_hash = entry.this_hash

    return {"valid": True, "total_entries": len(entries)}