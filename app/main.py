
from fastapi import FastAPI
from app.api.v1 import users
from app.db.session import engine
from app.db.base_class import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healix Backend API")

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

@app.get("/")
def health_check():
    return {"status": "Healix backend running"}
