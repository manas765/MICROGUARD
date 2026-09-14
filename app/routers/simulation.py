from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.models import BusinessProfile, User
from app.dependencies import get_current_user
from app.finance.digital_twin import project_cash_flow, run_scenarios

router = APIRouter(prefix="/simulation", tags=["simulation"])


def _get_profile_and_repayments(db: Session, current_user: User):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="You must create a business profile before running a forecast")

    repayments = []
    for application in profile.applications:
        if application.loan:
            for schedule in application.loan.repayment_schedule:
                if not schedule.is_paid:
                    repayments.append((schedule.due_date, schedule.amount_due))

    return profile, repayments


@router.get("/forecast")
def get_forecast(
    horizon_months: int = 12,
    income_growth_rate: float = 0.0,
    shock_month: int | None = None,
    shock_pct: float = 0.0,
    extra_monthly_expense: float = 0.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile, repayments = _get_profile_and_repayments(db, current_user)

    months = project_cash_flow(
        monthly_income=profile.monthly_income_estimate,
        loan_repayments=repayments,
        horizon_months=horizon_months,
        income_growth_rate=income_growth_rate,
        shock_month=shock_month,
        shock_pct=shock_pct,
        extra_monthly_expense=extra_monthly_expense,
    )

    return {
        "business_name": profile.business_name,
        "horizon_months": horizon_months,
        "months": months,
    }


class ScenarioSpec(BaseModel):
    name: str
    income_growth_rate: float = 0.0
    shock_month: int | None = None
    shock_pct: float = 0.0
    extra_monthly_expense: float = 0.0


class CompareScenariosRequest(BaseModel):
    horizon_months: int = 12
    scenarios: list[ScenarioSpec]


@router.post("/compare")
def compare_scenarios(
    request: CompareScenariosRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile, repayments = _get_profile_and_repayments(db, current_user)

    results = run_scenarios(
        monthly_income=profile.monthly_income_estimate,
        loan_repayments=repayments,
        horizon_months=request.horizon_months,
        scenarios=[s.model_dump() for s in request.scenarios],
    )

    return {
        "business_name": profile.business_name,
        "horizon_months": request.horizon_months,
        "scenarios": results,
    }