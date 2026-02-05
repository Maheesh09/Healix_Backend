# Healix Backend

AI-powered medical record digitization system for Sri Lankan healthcare facilities.

## Features

### 🔍 OCR Document Processing
- PDF upload via FastAPI endpoints
- Google Document AI integration for medical document OCR
- Automatic table and entity extraction
- Cloud storage integration with Google Cloud Storage

### 🧹 Medical Document Normalization
- **Smart OCR noise removal** - Removes Korean characters, symbols, and artifacts
- **Patient information extraction** - Automatically parses name, age, gender from unstructured text
- **Date normalization** - Converts to ISO-8601 format for database storage
- **Biomarker standardization** - Maps lab-specific names to standard medical terminology
- **Unit normalization** - Standardizes units (e.g., "Per Cumm" → "per cu mm")
- **Reference range parsing** - Extracts numeric ranges for clinical validation
- **Auto-detection** - Automatically identifies report type and applies appropriate normalization

### 📊 Supported Report Types

#### Full Blood Count (FBC)
Automated processing of FBC reports with extraction of:
- White Blood Cell counts and differential (WBC, Neutrophils, Lymphocytes, Eosinophils, Monocytes, Basophils)
- Red Blood Cell parameters (Hemoglobin, RBC, MCV, MCH, MCHC, PCV)
- Platelet counts
- Reference ranges for all biomarkers

#### Serum Lipid Profile
Comprehensive lipid panel analysis including:
- Total Cholesterol
- Triglycerides
- HDL Cholesterol (High-Density Lipoprotein)
- LDL Cholesterol (Low-Density Lipoprotein)
- VLDL Cholesterol (Very-Low-Density Lipoprotein)
- Non-HDL Cholesterol
- Cholesterol/HDL and LDL/HDL ratios
- Clinical flags (High/Low indicators)

#### Fasting Plasma Glucose (FBS)
Glucose monitoring with support for:
- Fasting Plasma Glucose levels
- Multiple format variations (FBS, Fasting Glucose, Plasma Glucose)
- Reference ranges and clinical interpretation

## Project Structure

```
Healix_Backend/
├── app/
│   ├── api/
│   │   ├── v1/              # API v1 endpoints
│   │   │   └── reports.py   # Upload and processing endpoints
│   │   └── v2/              # API v2 (reserved for future)
│   ├── config/              # Configuration files
│   │   └── biomarker_config.py  # Medical terminology mappings for all report types
│   ├── services/            # Business logic
│   │   ├── ocr_service.py              # Document AI integration
│   │   ├── normalization_service.py    # Main normalization orchestrator
│   │   ├── fbs_normalization.py        # Fasting Plasma Glucose normalization
│   │   ├── lipid_normalization.py      # Serum Lipid Profile normalization
│   │   ├── upload_service.py           # Cloud storage integration
│   │   └── nlp_service.py              # Data assembly
│   ├── workers/             # Background tasks
│   │   └── ocr_worker.py    # Document processing pipeline
│   ├── core/                # Core configurations
│   ├── db/                  # Database models & connections
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   └── utils/               # Utilities
├── tests/                   # Test scripts
├── docs/                    # Comprehensive documentation
│   ├── API_ENDPOINTS.md                      # API reference
│   ├── API_INTEGRATION_GUIDE.md              # Integration guide
│   ├── NORMALIZATION.md                      # Normalization guide
│   ├── NORMALIZATION_EXAMPLE.md              # FBC examples
│   ├── ADDING_NEW_REPORT_TYPES.md            # Developer guide
│   ├── FBS_IMPLEMENTATION.md                 # FBS implementation details
│   ├── LIPID_PROFILE_IMPLEMENTATION.md       # Lipid profile details
│   └── LIPID_PROFILE_NORMALIZATION_EXAMPLE.md  # Lipid examples
├── requirements.txt         # Python dependencies
└── key.json                # Google Cloud service account key
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

### Processing Pipeline

1. **Upload** → User uploads PDF via `/api/v1/ocr/upload` endpoint
2. **OCR Extraction** → Google Document AI extracts:
   - Raw text (unstructured)
   - Tables (structured data)
   - Entities (key-value pairs)
   - Page metadata
3. **Report Type Detection** → System automatically identifies report type by scanning for keywords:
   - Checks for "FASTING PLASMA GLUCOSE" → FBS report
   - Checks for "SERUM LIPID PROFILE" → Lipid Profile
   - Defaults to Full Blood Count
4. **Normalization** → Appropriate normalizer processes the data:
   - **Patient Info**: Extracts name, age, gender using regex patterns
   - **Report Metadata**: Parses dates/times to ISO-8601 format
   - **Biomarkers**: 
     - Maps test names to standardized terminology
     - Cleans OCR noise from numeric values
     - Normalizes units (e.g., "Per Cumm" → "per cu mm")
     - Parses reference ranges into [min, max] arrays
     - Extracts clinical flags (High/Low) for lipid profiles
5. **Storage** → Both raw and normalized JSON saved to Google Cloud Storage
6. **Retrieval** → Clients can fetch:
   - `/normalized` endpoint: Clean, structured data
   - `/raw` endpoint: Original OCR output

### Architecture Highlights

- **Extensible Design**: New report types can be added by creating a normalization module
- **Configuration-Driven**: All biomarker mappings in `biomarker_config.py`
- **Noise-Resistant**: Handles Korean characters, OCR artifacts, and formatting inconsistencies
- **Type-Safe**: Uses Pydantic schemas for validation

See [docs/NORMALIZATION.md](docs/NORMALIZATION.md) for detailed documentation.  
See [docs/ADDING_NEW_REPORT_TYPES.md](docs/ADDING_NEW_REPORT_TYPES.md) for developer guide.

## Sample Output

### Full Blood Count (FBC)

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
    },
    {
      "name": "Hemoglobin",
      "value": 13.5,
      "unit": "g/dL",
      "ref_range": [13.0, 17.0]
    }
  ]
}
```

### Serum Lipid Profile

```json
{
  "patient": {
    "name": "MS PERERA",
    "age_years": 45,
    "gender": "Female"
  },
  "report": {
    "type": "Serum Lipid Profile",
    "sample_collected_at": "2025-06-15T08:30:00"
  },
  "biomarkers": [
    {
      "name": "Total Cholesterol",
      "value": 220.0,
      "unit": "mg/dL",
      "flag": "High",
      "ref_range": [125.0, 200.0]
    },
    {
      "name": "HDL Cholesterol",
      "value": 45.0,
      "unit": "mg/dL",
      "flag": "Low",
      "ref_range": [40.0, 60.0]
    }
  ]
}
```

### Fasting Plasma Glucose (FBS)

```json
{
  "patient": {
    "name": "MR FERNANDO",
    "age_years": 58,
    "gender": "Male"
  },
  "report": {
    "type": "Fasting Plasma Glucose",
    "sample_collected_at": "2025-06-20T07:00:00"
  },
  "biomarkers": [
    {
      "name": "Fasting Plasma Glucose",
      "value": 110.0,
      "unit": "mg/dL",
      "ref_range": [70.0, 100.0]
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

- [ ] Support for additional report types
  - [ ] Liver Function Test (LFT)
  - [ ] Renal Function Test (RFT/U&E)
  - [ ] Thyroid Function Test (TFT)
  - [ ] HbA1c (Glycated Hemoglobin)
  - [ ] Urinalysis
- [ ] Multi-language support (Sinhala, Tamil)
- [ ] Trend analysis and visualization
- [ ] Patient dashboard
- [ ] Mobile app integration
- [ ] Real-time report processing notifications
- [ ] Batch processing for multiple reports

## Contributing

This project is part of the Healix digital health platform for Sri Lanka.

## License

Proprietary - All rights reserved