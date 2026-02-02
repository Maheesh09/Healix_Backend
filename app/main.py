from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import reports as ocr

app = FastAPI(
    title="Healix Backend API",
    description="AI-powered medical record system",
    version="1.0.0"
)

app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])

