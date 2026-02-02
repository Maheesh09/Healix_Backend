import uuid
import json
from app.core.cloud import get_bucket
from app.core.config import BUCKET_NAME


def upload_pdf_to_bucket(local_pdf_path: str, user_nic: str):
    bucket = get_bucket(BUCKET_NAME)

    file_id = str(uuid.uuid4())
    gcs_path = f"users/{user_nic}/reports/{file_id}.pdf"

    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(
        local_pdf_path,
        content_type="application/pdf"
    )

    return {
        "file_id": file_id,
        "gcs_uri": f"gs://{BUCKET_NAME}/{gcs_path}"
    }


def store_json(user_nic: str, file_id: str, data: dict):
    bucket = get_bucket(BUCKET_NAME)
    path = f"users/{user_nic}/processed/{file_id}.json"

    blob = bucket.blob(path)
    blob.upload_from_string(
        json.dumps(data, indent=2),
        content_type="application/json"
    )

    return f"gs://{BUCKET_NAME}/{path}"
