from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import RepaymentSchedule, Loan, LoanApplication, BusinessProfile, User
from app.dependencies import get_current_user
from app.monitoring.monitoring import assess_loan

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


def _get_schedule_or_404(db: Session, schedule_id: int) -> RepaymentSchedule:
    schedule = db.query(RepaymentSchedule).filter(RepaymentSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Repayment not found")
    return schedule


def _build_alert_entry(schedule: RepaymentSchedule) -> dict:
    loan = schedule.loan
    application = loan.application
    assessment = assess_loan(
        original_risk_score=application.risk_score or 0,
        original_risk_band=application.risk_band or "Medium",
        due_date=schedule.due_date,
        is_paid=schedule.is_paid,
        paid_at=schedule.paid_at,
    )
    return {
        "schedule_id": schedule.id,
        "loan_id": loan.id,
        "application_id": application.id,
        "business_name": application.business_profile.business_name if application.business_profile else None,
        "purpose": application.purpose,
        "amount_due": schedule.amount_due,
        "due_date": schedule.due_date.isoformat(),
        "is_paid": schedule.is_paid,
        **assessment,
    }


@router.post("/repay/{schedule_id}")
def mark_repaid(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule = _get_schedule_or_404(db, schedule_id)
    application = schedule.loan.application

    is_owner = (
        application.business_profile
        and application.business_profile.owner
        and application.business_profile.owner.id == current_user.id
    )
    is_staff = current_user.role in ("loan_officer", "admin")
    if not (is_owner or is_staff):
        raise HTTPException(status_code=403, detail="You do not have permission to update this repayment")

    if schedule.is_paid:
        raise HTTPException(status_code=400, detail="This repayment is already marked as paid")

    schedule.is_paid = True
    schedule.paid_at = datetime.utcnow()
    db.commit()

    return _build_alert_entry(schedule)


@router.get("/alerts")
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("loan_officer", "admin"):
        raise HTTPException(status_code=403, detail="Only loan officers or admins can view monitoring alerts")

    schedules = db.query(RepaymentSchedule).all()
    entries = [_build_alert_entry(s) for s in schedules]

    severity_order = {"overdue": 0, "due_soon": 1, "paid_late": 2, "on_track": 3, "paid_on_time": 4}
    entries.sort(key=lambda e: severity_order.get(e["health_status"], 5))

    return {
        "total": len(entries),
        "alert_count": sum(1 for e in entries if e["is_alert"]),
        "diverged_count": sum(1 for e in entries if e["prediction_diverged"]),
        "loans": entries,
    }


@router.get("/my-loans")
def get_my_loan_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        return {"loans": []}

    entries = []
    for application in profile.applications:
        if application.loan:
            for schedule in application.loan.repayment_schedule:
                entries.append(_build_alert_entry(schedule))

    return {"loans": entries}