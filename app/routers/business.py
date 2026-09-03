from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.models import BusinessProfile, User
from app.dependencies import get_current_user

router = APIRouter(prefix="/business", tags=["business"])


class BusinessProfileRequest(BaseModel):
    business_name: str
    sector: str
    monthly_income_estimate: float
    years_operating: float


@router.post("/profile")
def create_business_profile(
    request: BusinessProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Business profile already exists for this user")

    profile = BusinessProfile(
        user_id=current_user.id,
        business_name=request.business_name,
        sector=request.sector,
        monthly_income_estimate=request.monthly_income_estimate,
        years_operating=request.years_operating,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"message": "Business profile created", "profile_id": profile.id}


@router.get("/profile/me")
def get_my_business_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="No business profile found")
    return {
        "id": profile.id,
        "business_name": profile.business_name,
        "sector": profile.sector,
        "monthly_income_estimate": profile.monthly_income_estimate,
        "years_operating": profile.years_operating,
    }