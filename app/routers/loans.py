import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from datetime import datetime, timedelta

from app.database import get_db
from app.models.models import LoanApplication, BusinessProfile, User, Loan, RepaymentSchedule
from app.dependencies import get_current_user
from app.ml.inference import score_application
from app.finance.stress_calc import calculate_stress

router = APIRouter(prefix="/loans", tags=["loans"])


class LoanApplicationRequest(BaseModel):
    requested_amount: float
    purpose: str
    term_days: int
    has_guarantor: bool = False


class LoanApplicationResponse(BaseModel):
    id: int
    requested_amount: float
    purpose: str
    status: str
    term_days: int
    has_guarantor: bool
    risk_score: float | None
    risk_band: str | None
    risk_reasons: list[str] | None
    risk_confidence: str | None
    stress_score: float | None
    stress_band: str | None
    stress_reasons: list[str] | None

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if hasattr(obj, "risk_reasons") and isinstance(obj.risk_reasons, str):
            obj.risk_reasons = json.loads(obj.risk_reasons)
        if hasattr(obj, "stress_reasons") and isinstance(obj.stress_reasons, str):
            obj.stress_reasons = json.loads(obj.stress_reasons)
        return super().model_validate(obj, **kwargs)


@router.post("/apply")
def apply_for_loan(
    request: LoanApplicationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="You must create a business profile before applying for a loan")

    result = score_application(
        requested_amount=request.requested_amount,
        term_days=request.term_days,
        age=current_user.age,
        gender=current_user.gender,
        education=current_user.education,
        has_guarantor=request.has_guarantor,
    )

    stress_result = calculate_stress(
        monthly_income_estimate=profile.monthly_income_estimate,
        years_operating=profile.years_operating,
        requested_amount=request.requested_amount,
        term_days=request.term_days,
    )

    application = LoanApplication(
        business_profile_id=profile.id,
        requested_amount=request.requested_amount,
        purpose=request.purpose,
        term_days=request.term_days,
        has_guarantor=request.has_guarantor,
        risk_score=result["risk_score"],
        risk_band=result["risk_band"],
        risk_reasons=json.dumps(result["reasons"]),
        risk_confidence=result["confidence"],
        model_version=result["model_version"],
        stress_score=stress_result["stress_score"],
        stress_band=stress_result["stress_band"],
        stress_reasons=json.dumps(stress_result["reasons"]),
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "message": "Loan application submitted",
        "application_id": application.id,
        "risk_score": result["risk_score"],
        "risk_band": result["risk_band"],
        "reasons": result["reasons"],
        "stress_score": stress_result["stress_score"],
        "stress_band": stress_result["stress_band"],
        "stress_reasons": stress_result["reasons"],
    }


@router.get("/my-applications", response_model=List[LoanApplicationResponse])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        return []

    return db.query(LoanApplication).filter(LoanApplication.business_profile_id == profile.id).all()


@router.get("/all", response_model=List[LoanApplicationResponse])
def get_all_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("loan_officer", "admin"):
        raise HTTPException(status_code=403, detail="Only loan officers or admins can view all applications")

    return db.query(LoanApplication).all()


# Advisory only — a starting point for negotiation, not an enforced
# rule. The loan officer sets the actual rate when approving; this
# just gives them a reasonable range to anchor the conversation,
# informed by the risk score without being dictated by it.
SUGGESTED_RATE_RANGES = {
    "Low": (10, 14),
    "Medium": (16, 20),
    "High": (22, 28),
}


@router.get("/{application_id}/suggested-terms")
def get_suggested_terms(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("loan_officer", "admin"):
        raise HTTPException(status_code=403, detail="Only loan officers or admins can view suggested terms")

    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    rate_range = SUGGESTED_RATE_RANGES.get(application.risk_band, (14, 20))

    return {
        "application_id": application.id,
        "risk_band": application.risk_band,
        "stress_band": application.stress_band,
        "requested_term_days": application.term_days,
        "suggested_interest_rate_range": {"min": rate_range[0], "max": rate_range[1]},
        "note": "Suggested range only — the final rate and term are negotiated between borrower and loan officer.",
    }


class DecisionRequest(BaseModel):
    decision: str  # "approved" or "rejected"
    interest_rate: float | None = None  # required when approving — the loan officer's final agreed rate
    final_term_days: int | None = None  # optional — defaults to what the borrower originally requested


@router.post("/{application_id}/decision")
def decide_application(
    application_id: int,
    request: DecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("loan_officer", "admin"):
        raise HTTPException(status_code=403, detail="Only loan officers or admins can approve/reject applications")

    if request.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Decision must be 'approved' or 'rejected'")

    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = request.decision

    if request.decision == "approved":
        if request.interest_rate is None:
            raise HTTPException(
                status_code=400,
                detail="interest_rate is required to approve an application — set the final negotiated rate",
            )

        final_term_days = request.final_term_days or application.term_days

        loan = Loan(
            application_id=application.id,
            principal=application.requested_amount,
            interest_rate=request.interest_rate,
            term_days=final_term_days,
            start_date=datetime.utcnow(),
            status="active",
        )
        db.add(loan)
        db.commit()
        db.refresh(loan)

        amount_due = application.requested_amount * (1 + (request.interest_rate / 100) * (final_term_days / 365))
        schedule = RepaymentSchedule(
            loan_id=loan.id,
            due_date=loan.start_date + timedelta(days=final_term_days),
            amount_due=round(amount_due, 2),
            is_paid=False,
        )
        db.add(schedule)
        db.commit()

        return {
            "message": f"Application {application_id} approved",
            "loan_id": loan.id,
            "principal": loan.principal,
            "interest_rate": loan.interest_rate,
            "term_days": loan.term_days,
            "amount_due": schedule.amount_due,
            "due_date": schedule.due_date.isoformat(),
        }

    db.commit()
    return {"message": f"Application {application_id} marked as {request.decision}"}