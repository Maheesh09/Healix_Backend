from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Path, Query
from app.services.upload_service import upload_pdf_to_bucket, get_normalized_json, get_raw_json, list_user_reports
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
    """
    Upload a medical report PDF for OCR processing and normalization.
    
    Args:
        nic: Patient's National Identity Card number
        file: PDF file of medical report
        
    Returns:
        Status and file_id for tracking
    """
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
        "message": "Report uploaded and processing started",
        "file_id": upload_info["file_id"]
    }


@router.get("/report/{nic}/{file_id}/normalized")
async def get_normalized_report(
    nic: str = Path(..., description="Patient's National Identity Card number"),
    file_id: str = Path(..., description="Unique file identifier")
):
    """
    Retrieve the normalized medical report JSON.
    
    Args:
        nic: Patient's NIC
        file_id: File identifier returned from upload
        
    Returns:
        Normalized medical report as JSON
        
    Raises:
        404: If report not found or not yet processed
    """
    try:
        normalized_data = get_normalized_json(nic, file_id)
        return {
            "status": "success",
            "data": normalized_data
        }
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Normalized report not found. It may still be processing. {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving report: {str(e)}"
        )


@router.get("/report/{nic}/{file_id}/raw")
async def get_raw_report(
    nic: str = Path(..., description="Patient's National Identity Card number"),
    file_id: str = Path(..., description="Unique file identifier")
):
    """
    Retrieve the raw OCR data (for debugging).
    
    Args:
        nic: Patient's NIC
        file_id: File identifier returned from upload
        
    Returns:
        Raw OCR data as JSON
        
    Raises:
        404: If report not found
    """
    try:
        raw_data = get_raw_json(nic, file_id)
        return {
            "status": "success",
            "data": raw_data
        }
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Report not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving report: {str(e)}"
        )


@router.get("/reports/{nic}")
async def list_reports(
    nic: str = Path(..., description="Patient's National Identity Card number")
):
    """
    List all processed reports for a patient.
    
    Args:
        nic: Patient's NIC
        
    Returns:
        List of available reports with metadata
    """
    try:
        reports = list_user_reports(nic)
        return {
            "status": "success",
            "count": len(reports),
            "reports": reports
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing reports: {str(e)}"
        )

