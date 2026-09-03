from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="borrower")  # borrower, loan_officer, admin
    created_at = Column(DateTime, default=datetime.utcnow)

    business_profile = relationship("BusinessProfile", back_populates="owner", uselist=False)


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    monthly_income_estimate = Column(Float, nullable=False)
    years_operating = Column(Float, nullable=False)

    owner = relationship("User", back_populates="business_profile")
    applications = relationship("LoanApplication", back_populates="business_profile")


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    business_profile_id = Column(Integer, ForeignKey("business_profiles.id"), nullable=False)
    requested_amount = Column(Float, nullable=False)
    purpose = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, approved, rejected
    risk_score = Column(Float, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)

    business_profile = relationship("BusinessProfile", back_populates="applications")
    loan = relationship("Loan", back_populates="application", uselist=False)


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("loan_applications.id"), unique=True, nullable=False)
    principal = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    term_days = Column(Integer, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")  # active, closed, defaulted

    application = relationship("LoanApplication", back_populates="loan")
    repayment_schedule = relationship("RepaymentSchedule", back_populates="loan")
    repayments = relationship("Repayment", back_populates="loan")


class RepaymentSchedule(Base):
    __tablename__ = "repayment_schedule"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    due_date = Column(DateTime, nullable=False)
    amount_due = Column(Float, nullable=False)
    is_paid = Column(Boolean, default=False)

    loan = relationship("Loan", back_populates="repayment_schedule")


class Repayment(Base):
    __tablename__ = "repayments"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    amount_paid = Column(Float, nullable=False)
    paid_at = Column(DateTime, default=datetime.utcnow)

    loan = relationship("Loan", back_populates="repayments")