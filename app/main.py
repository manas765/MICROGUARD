from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, business, loans
from app.database import engine, Base
from app.models import models

app = FastAPI(title="MICROGUARD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(business.router)
app.include_router(loans.router)


@app.get("/setup/create-tables")
def setup_create_tables():
    Base.metadata.create_all(bind=engine)
    return {"message": "Tables created successfully"}


@app.get("/")
def root():
    return {"message": "MICROGUARD API is running"}