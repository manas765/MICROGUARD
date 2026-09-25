from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import BusinessProfile, User
from app.dependencies import get_current_user
from app.assistant.context_builder import build_borrower_context, build_officer_context
from app.assistant.llm_client import ask_assistant
from app.routers.loans import LoanApplicationResponse, get_my_applications
from app.routers.monitoring import get_my_loan_health, get_alerts

router = APIRouter(prefix="/assistant", tags=["assistant"])


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
def ask(
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role in ("loan_officer", "admin"):
        alerts_summary = get_alerts(db=db, current_user=current_user)
        context = build_officer_context(alerts_summary)
    else:
        profile_obj = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
        profile = (
            {
                "business_name": profile_obj.business_name,
                "sector": profile_obj.sector,
                "monthly_income_estimate": profile_obj.monthly_income_estimate,
                "years_operating": profile_obj.years_operating,
            }
            if profile_obj
            else None
        )

        raw_applications = get_my_applications(db=db, current_user=current_user)
        applications = [
            LoanApplicationResponse.model_validate(a, from_attributes=True).model_dump() for a in raw_applications
        ]

        loan_health_response = get_my_loan_health(db=db, current_user=current_user)
        loan_health = loan_health_response["loans"]

        user_dict = {
            "name": current_user.name,
            "age": current_user.age,
            "gender": current_user.gender,
            "education": current_user.education,
        }

        context = build_borrower_context(user_dict, profile, applications, loan_health)

    answer = ask_assistant(request.question, context)
    return {"answer": answer}