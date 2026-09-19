import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, business, loans, simulation, monitoring
from app.database import engine, Base
from app.models import models

app = FastAPI(title="MICROGUARD API")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_origin_regex=r"https://frontend-.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/setup/reset-tables")
def reset_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return {"message": "Tables reset successfully"}

app.include_router(auth.router)
app.include_router(business.router)
app.include_router(loans.router)
app.include_router(simulation.router)
app.include_router(monitoring.router)


@app.get("/")
def root():
    return {"message": "MICROGUARD API is running"}