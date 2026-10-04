from app.audit.audit_log import record_event, verify_chain, _compute_hash, GENESIS_HASH
from app.models.models import AuditLog


def test_first_event_chains_from_genesis(db_session):
    entry = record_event(db_session, "loan_approved", {"application_id": 1})
    assert entry.prev_hash == GENESIS_HASH
    assert entry.this_hash != GENESIS_HASH


def test_second_event_chains_from_first(db_session):
    first = record_event(db_session, "loan_approved", {"application_id": 1})
    second = record_event(db_session, "repayment_marked_paid", {"schedule_id": 1})
    assert second.prev_hash == first.this_hash


def test_verify_chain_valid_for_untouched_log(db_session):
    record_event(db_session, "loan_approved", {"application_id": 1})
    record_event(db_session, "loan_rejected", {"application_id": 2})
    result = verify_chain(db_session)
    assert result["valid"] is True
    assert result["total_entries"] == 2


def test_verify_chain_detects_tampering(db_session):
    entry = record_event(db_session, "loan_approved", {"application_id": 1})
    record_event(db_session, "loan_rejected", {"application_id": 2})

    # simulate someone editing a past record directly in the DB
    entry.event_data = '{"application_id": 999}'
    db_session.commit()

    result = verify_chain(db_session)
    assert result["valid"] is False
    assert result["broken_at_id"] == entry.id


def test_empty_log_is_valid(db_session):
    result = verify_chain(db_session)
    assert result["valid"] is True
    assert result["total_entries"] == 0