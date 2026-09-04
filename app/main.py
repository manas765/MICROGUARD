from fastapi import FastAPI
from app.routers import auth, business, loans

app = FastAPI(title="MICROGUARD API")

app.include_router(auth.router)
app.include_router(business.router)
app.include_router(loans.router)


@app.get("/")
def root():
    return {"message": "MICROGUARD API is running"}