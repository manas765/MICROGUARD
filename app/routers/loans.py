import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.models import LoanApplication, BusinessProfile, User
from app.dependencies import get_current_user
from app.ml.inference import score_application

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

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if hasattr(obj, "risk_reasons") and isinstance(obj.risk_reasons, str):
            obj.risk_reasons = json.loads(obj.risk_reasons)
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


@router.post("/{application_id}/decision")
def decide_application(
    application_id: int,
    decision: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("loan_officer", "admin"):
        raise HTTPException(status_code=403, detail="Only loan officers or admins can approve/reject applications")

    if decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Decision must be 'approved' or 'rejected'")

    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = decision
    db.commit()

    return {"message": f"Application {application_id} marked as {decision}"}