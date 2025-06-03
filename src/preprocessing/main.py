# This code would typically reside in a main.py for a Google Cloud Function.
# It needs google-cloud-storage and PyMuPDF (fitz) in its requirements.txt.

import fitz  # PyMuPDF
from google.cloud import storage
import os

# Configuration (can be environment variables in Cloud Function)
KB_BUCKET_NAME = os.environ.get("KB_BUCKET_NAME", "ur-agent-knowledge-base")

def process_uploaded_pdf(event, context):
    """
    Triggered by a change in a GCS bucket (PDF upload).
    Extracts raw text from the PDF and stores it in the Knowledge Base GCS bucket.
    """
    storage_client = storage.Client()

    source_bucket_name = event['bucket']
    file_name = event['name']

    if not file_name.lower().endswith(".pdf"):
        print(f"File {file_name} is not a PDF. Skipping.")
        return

    print(f"Processing PDF file: gs://{source_bucket_name}/{file_name}")

    source_bucket = storage_client.bucket(source_bucket_name)
    source_blob = source_bucket.blob(file_name)

    # Download PDF to a temporary location in the Cloud Function's environment
    temp_pdf_path = f"/tmp/{os.path.basename(file_name)}"
    source_blob.download_to_filename(temp_pdf_path)

    raw_text = ""
    try:
        doc = fitz.open(temp_pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            raw_text += page.get_text("text") # Extract plain text
        doc.close()

        # Basic cleaning
        raw_text = "\n".join([line for line in raw_text.splitlines() if line.strip()]) # Remove empty lines
        raw_text = " ".join(raw_text.split()) # Normalize multiple spaces to a single space

        # Store the extracted raw text to the Knowledge Base bucket
        kb_blob_name = f"processed_raw_text/{os.path.splitext(os.path.basename(file_name))[0]}.txt"
        kb_bucket = storage_client.bucket(KB_BUCKET_NAME)
        kb_blob = kb_bucket.blob(kb_blob_name)
        kb_blob.upload_from_string(raw_text, content_type="text/plain")

        print(f"Successfully extracted text from {file_name} and saved to gs://{KB_BUCKET_NAME}/{kb_blob_name}")

    except Exception as e:
        print(f"Error processing {file_name}: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

# To deploy this as a Cloud Function, you'd also have a requirements.txt:
# google-cloud-storage
# PyMuPDF