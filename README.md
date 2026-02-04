# Healix Backend

AI-powered medical record digitization system for Sri Lankan healthcare facilities.

## Features

### 🔍 OCR Document Processing
- PDF upload via FastAPI endpoints
- Google Document AI integration for medical document OCR
- Automatic table and entity extraction

### 🧹 Medical Document Normalization
- **Smart OCR noise removal** - Removes Korean characters, symbols, and artifacts
- **Patient information extraction** - Automatically parses name, age, gender from unstructured text
- **Date normalization** - Converts to ISO-8601 format for database storage
- **Biomarker standardization** - Maps lab-specific names to standard medical terminology
- **Unit normalization** - Standardizes units (e.g., "Per Cumm" → "per cu mm")
- **Reference range parsing** - Extracts numeric ranges for clinical validation

### 📊 Full Blood Count (FBC) Support
Currently supports automated processing of FBC reports with extraction of:
- White Blood Cell counts and differential
- Red Blood Cell parameters (Hemoglobin, RBC, MCV, MCH, MCHC, PCV)
- Platelet counts
- Reference ranges for all biomarkers

## Project Structure

```
Healix_Backend/
├── app/
│   ├── api/v1/          # API endpoints
│   │   └── reports.py   # Upload and processing endpoints
│   ├── config/          # Configuration files
│   │   └── biomarker_config.py  # Medical terminology mappings
│   ├── services/        # Business logic
│   │   ├── ocr_service.py           # Document AI integration
│   │   ├── normalization_service.py # Medical data normalization
│   │   ├── upload_service.py        # Cloud storage
│   │   └── nlp_service.py          # Data assembly
│   ├── workers/         # Background tasks
│   │   └── ocr_worker.py  # Document processing pipeline
│   ├── utils/           # Utilities
│   ├── models/          # Database models
│   └── schemas/         # Pydantic schemas
├── tests/               # Test scripts
├── docs/                # Documentation
│   ├── NORMALIZATION.md         # Normalization guide
│   └── NORMALIZATION_EXAMPLE.md # Before/after examples
└── requirements.txt
```

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Test Normalization

```bash
python tests/simple_test.py
```

View output in `tests/normalized_output.json`


## API Endpoints

### 1. Upload Medical Report

```
POST /api/v1/ocr/upload
```

**Parameters:**
- `nic` (string) - Patient's National Identity Card number
- `file` (file) - PDF file of medical report

**Response:**
```json
{
  "status": "uploaded",
  "message": "Report uploaded and processing started",
  "file_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 2. Get Normalized Report

```
GET /api/v1/ocr/report/{nic}/{file_id}/normalized
```

Returns clean, structured medical report JSON ready for use.

**Example:**
```bash
curl http://localhost:8080/api/v1/ocr/report/123456789V/abc-123/normalized
```

**Response:** See [Sample Output](#sample-output) below

### 3. Get Raw OCR Data

```
GET /api/v1/ocr/report/{nic}/{file_id}/raw
```

Returns raw OCR extraction (for debugging).

### 4. List Patient Reports

```
GET /api/v1/ocr/reports/{nic}
```

Returns list of all processed reports for a patient.

**Full Documentation:** [docs/API_ENDPOINTS.md](docs/API_ENDPOINTS.md)  
**Integration Guide:** [docs/API_INTEGRATION_GUIDE.md](docs/API_INTEGRATION_GUIDE.md)


## How It Works

1. **Upload** - User uploads PDF via API
2. **OCR** - Document AI extracts text, tables, entities
3. **Normalization** - Raw data is cleaned and structured
4. **Storage** - Both raw and normalized JSON saved to Cloud Storage

See [NORMALIZATION.md](docs/NORMALIZATION.md) for detailed documentation.

## Sample Output

```json
{
  "patient": {
    "name": "MR S KUMAR",
    "age_years": 62,
    "gender": "Male",
    "service_ref_no": "CHL000735039"
  },
  "report": {
    "type": "Full Blood Count",
    "sample_collected_at": "2025-06-03T09:10:00"
  },
  "biomarkers": [
    {
      "name": "WBC",
      "value": 7970.0,
      "unit": "per cu mm",
      "ref_range": [4000.0, 11000.0]
    }
  ]
}
```

## Technologies

- **FastAPI** - Modern Python web framework
- **Google Document AI** - OCR and document understanding
- **Google Cloud Storage** - File and JSON storage
- **Python 3.8+** - Core language

## Future Enhancements

- [ ] Support for additional report types (Lipid Panel, Liver Function, etc.)
- [ ] Multi-language support (Sinhala, Tamil)
- [ ] Trend analysis and visualization
- [ ] Patient dashboard
- [ ] Mobile app integration

## Contributing

This project is part of the Healix digital health platform for Sri Lanka.

## License

Proprietary - All rights reserved