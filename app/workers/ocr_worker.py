from app.services.ocr_service import process_with_document_ai
from app.services.upload_service import store_json
from app.services.nlp_service import build_report_json
from app.utils.text_utils import extract_tables, extract_entities

def process_document_worker(gcs_uri: str, nic: str, file_id: str):
    document = process_with_document_ai(gcs_uri)

    tables = extract_tables(document)
    entities = extract_entities(document)

    final_json = build_report_json(document, tables, entities)

    store_json(nic, file_id, final_json)
