from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from app.services.upload_service import upload_pdf_to_bucket
import os
import tempfile
from app.workers.ocr_worker import process_document_worker

router = APIRouter()

@router.post("/upload")
async def upload_report(
    nic: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        upload_info = upload_pdf_to_bucket(temp_path, nic)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    background_tasks.add_task(
        process_document_worker,
        upload_info["gcs_uri"],
        nic,
        upload_info["file_id"]
    )

    return {
        "status": "uploaded",
        "file_id": upload_info["file_id"]
    }
