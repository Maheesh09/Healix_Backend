import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET_NAME = os.getenv("GCS_BUCKET")
DOC_AI_LOCATION = os.getenv("DOCAI_LOCATION", "us")
DOC_AI_PROCESSOR_ID = os.getenv("DOCAI_PROCESSOR_ID")

# Set credentials path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, "key.json")
