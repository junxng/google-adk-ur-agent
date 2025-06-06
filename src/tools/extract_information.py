from google.api_core.client_options import ClientOptions
from google.cloud.documentai_v1.types import Document, ProcessOptions, OcrConfig
from google.cloud import documentai_v1 as documentai
from google.cloud import storage
from google.adk.tools import FunctionTool
import logging
import os
from typing import Dict, Any, List

from src.config import (
    PROJECT_ID,
    PROCESSOR_ID,
    LOG_LEVEL,
    LOG_FORMAT,
    GCS_DEFAULT_LOCATION,
    GCS_DEFAULT_CONTENT_TYPE,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)

def extract_information(
    gcs_uri: str,
    project_id: str = PROJECT_ID,
    location: str = GCS_DEFAULT_LOCATION,
    processor_id: str = PROCESSOR_ID,
    mime_type: str = GCS_DEFAULT_CONTENT_TYPE,
    page_chunk_size: int = 14
) -> Dict[str, str]:
    """
    Processes a PDF document from a GCS bucket using Document AI and extracts its text.
    Handles large documents by processing them in chunks of pages and enables native PDF parsing.

    Args:
        gcs_uri: The GCS URI of the file to process (e.g., "gs://your-bucket/your-file.pdf").
        project_id: The Google Cloud Project ID containing the processor.
        location: The location of the Document AI processor (e.g., "us"). This is crucial for the API endpoint.
        processor_id: The ID of the Document AI processor to use.
        mime_type: The MIME type of the document. Defaults to "application/pdf".
        page_chunk_size: The number of pages to process in each API call. Should be <= 30 for native PDF parsing.

    Returns:
        A dictionary containing the extracted text of the document under the key "extracted_text",
        or an error message under the key "error".
    """
    print(f"Starting PDF extraction for: {gcs_uri} with page_chunk_size: {page_chunk_size}, location: {location}")

    # 1. Input validation
    if project_id is None or processor_id is None:
        return {"error": "Project ID or Processor ID are not configured. Please provide them as arguments or set the defaults."}
    if not gcs_uri.startswith("gs://"):
        return {"error": "Invalid GCS URI. It must start with 'gs://'."}
    if page_chunk_size <= 0:
        return {"error": "page_chunk_size must be a positive integer."}


    # 2. Initialize Document AI Client with the correct regional endpoint
    try:
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
    except Exception as e:
        logging.error(f"Failed to initialize Document AI client: {e}", exc_info=True)
        return {"error": f"Failed to initialize Document AI client: {e}"}

    # 3. Construct the full processor resource name
    processor_name = client.processor_path(project_id, location, processor_id)
    print(f"Using processor: {processor_name}")

    all_extracted_text = []
    current_page_start = 1  # Document AI pages are 1-indexed

    while True:
        page_end = current_page_start + page_chunk_size - 1
        print(f"Processing pages: {current_page_start} to {page_end}")

        # 4. Configure ProcessOptions for page range and native PDF parsing
        pages_to_process = list(range(current_page_start, page_end + 1))
        process_options = ProcessOptions(
            individual_page_selector=ProcessOptions.IndividualPageSelector(
                pages=pages_to_process
            ),
            ocr_config=OcrConfig(
                enable_native_pdf_parsing=True
            )
        )
        
        # 5. Configure the GCS document source
        gcs_document = documentai.GcsDocument(gcs_uri=gcs_uri, mime_type=mime_type)

        # 6. Create the ProcessRequest
        request = documentai.ProcessRequest(
            name=processor_name,
            gcs_document=gcs_document,
            skip_human_review=True,
            process_options=process_options
        )

        # 7. Call the Document AI API and handle potential errors
        try:
            print(f"Sending request to Document AI for pages {current_page_start}-{page_end}...")
            result = client.process_document(request=request)
            document = result.document

            if not document.text and not document.pages:
                print("No text or pages returned for this chunk, assuming end of document or irrelevant pages.")
                break

            if document.text:
                all_extracted_text.append(document.text)
                print(f"Successfully processed {len(document.pages)} pages in this chunk.")
            else:
                print("No text extracted from this chunk of pages.")

            if not document.pages or len(document.pages) < page_chunk_size:
                print("Reached the end of the document (or fewer pages returned than chunk size).")
                break
            
            current_page_start = page_end + 1

        except Exception as e:
            if "page range" in str(e).lower() or "out of range" in str(e).lower():
                print(f"Reached the end of the document (API error indicates invalid page range): {e}")
                break
            logging.error(f"Error during Document AI processing for pages {current_page_start}-{page_end}: {e}", exc_info=True)
            return {"error": f"An API error occurred during document processing for pages {current_page_start}-{page_end}: {e}"}

    if not all_extracted_text:
        print("No text was extracted from any part of the document.")
        return {"extracted_text": ""}

    print("Successfully processed all chunks.")
    return {"extracted_text": "".join(all_extracted_text)}

# Create a FunctionTool that the agent can use
extract_information_tool = FunctionTool(extract_information)
