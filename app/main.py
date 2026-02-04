from fastapi import FastAPI

from app.api.v1.endpoints import doctor

app = FastAPI(title="Healix Backend API")

app.include_router(doctor.router)
