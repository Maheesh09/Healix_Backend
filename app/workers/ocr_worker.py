from app.services.ocr_service import process_with_document_ai
from app.services.upload_service import store_json
from app.services.nlp_service import build_report_json
from app.services.normalization_service import normalize_fbc_report
from app.utils.text_utils import extract_tables, extract_entities

def process_document_worker(gcs_uri: str, nic: str, file_id: str):
    """
    Process medical document: extract OCR data and normalize to structured JSON.
    
    Args:
        gcs_uri: Google Cloud Storage URI of the document
        nic: Patient's National Identity Card number
        file_id: Unique file identifier
    """
    # Extract raw OCR data using Document AI
    document = process_with_document_ai(gcs_uri)

    # Extract tables and entities from OCR
    tables = extract_tables(document)
    entities = extract_entities(document)

    # Build raw JSON (for debugging/archival)
    raw_json = build_report_json(document, tables, entities)
    
    # Normalize to clean, structured medical JSON
    normalized_json = normalize_fbc_report(raw_json)

    # Store both raw and normalized versions
    store_json(nic, file_id, raw_json)  # Store raw OCR output
    store_json(nic, f"{file_id}_normalized", normalized_json)  # Store normalized output
    
