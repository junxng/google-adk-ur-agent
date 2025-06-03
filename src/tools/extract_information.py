from typing import List, Dict, Any, Optional
from google.adk.tools import ToolContext, FunctionTool
from pydantic import BaseModel, Field

class ExtractedDetail(BaseModel):
    """
    Represents a single piece of structured information extracted from the text.
    """
    category: str = Field(..., description="The category of the extracted information (e.g., 'Requirement', 'Decision', 'Action Item', 'Key Assumption').")
    statement: str = Field(..., description="The specific statement or piece of information extracted.")
    page_reference: Optional[int] = Field(None, description="Optional page number or section where this information was found if discernible.")
    confidence_score: Optional[float] = Field(None, description="An optional confidence score (0.0 to 1.0) if the extraction method provides one.")

class ExtractionOutput(BaseModel):
    """
    Defines the structured output for the information extraction tool.
    The LLM agent is expected to populate this model based on its analysis.
    """
    source_document_id: Optional[str] = Field(None, description="An identifier for the source document from which information was extracted.")
    extracted_details: List[ExtractedDetail] = Field(..., description="A list of structured details extracted from the provided text content.")
    summary_of_extraction: Optional[str] = Field(None, description="A brief summary of what was focused on during this extraction pass.")

def extract_information(
    raw_text_content: str,
    extraction_focus: str,
    document_id: Optional[str] = None
) -> ExtractionOutput:
    """
    Processes raw text content to extract specific, structured details based on a given focus.

    This tool is intended to be called by an LLM Agent (like Google ADK's LlmAgent).
    The agent's primary LLM performs the actual natural language understanding and extraction.
    This function defines the contract: the expected inputs and, critically, the
    structured format (ExtractionOutput) that the LLM's output should conform to
    when it decides to use this tool.

    The calling LLM agent should be instructed on how to interpret the 'extraction_focus'
    to guide its extraction process from the 'raw_text_content'.

    Args:
        raw_text_content: The substantial block of text from which to extract information.
        extraction_focus: A natural language instruction specifying what kind of information
                          to prioritize or look for. For example:
                          - "Extract all functional and non-functional requirements."
                          - "Identify all stakeholders and their roles mentioned."
                          - "List all decisions made and their justifications."
        document_id: An optional identifier for the source document.

    Returns:
        An ExtractionOutput object. The calling LLM agent is responsible for generating
        the content that will populate this Pydantic model. ADK handles parsing the
        LLM's JSON output into this model.
    """

    print(f"Tool 'extract_information' invoked for document_id: {document_id}")
    print(f"Extraction focus: '{extraction_focus}'")
    print(f"Processing text of length: {len(raw_text_content)} characters.")

    return ExtractionOutput(
        source_document_id=document_id,
        extracted_details=[
            # ExtractedDetail(category="Placeholder", statement="LLM to provide actual extracted data.")
        ],
        summary_of_extraction=f"Placeholder summary for focus: {extraction_focus}. LLM to provide."
    )

# Create FunctionTools from the functions
extract_information_tool = FunctionTool(extract_information)
