from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from google.adk.tools import ToolContext, FunctionTool
from enum import Enum

# Define Enums for controlled vocabularies
class RequirementTypeEnum(str, Enum):
    ORIGINAL = "Original"
    CHANGE_REQUEST = "Change Request"

class RequirementScopeEnum(str, Enum):
    IN_SCOPE = "In-Scope"
    OUT_OF_SCOPE = "Out-Scope"

class RequirementPriorityEnum(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class RequirementCoverageEnum(str, Enum):
    YES = "Yes"
    NO = "No"

class UserRequirement(BaseModel):
    id: str = Field(..., description="Unique identifier for the user requirement (e.g., USR0150).")
    name: str = Field(..., description="A concise overview or name for the user requirement (VARCHAR).")
    source: str = Field(..., description="The identifier (e.g., GCS URI) of the source file from which this requirement was derived.")
    type: RequirementTypeEnum = Field(..., description="Categorizes the origin or nature of the requirement.")
    scope: RequirementScopeEnum = Field(..., description="Defines whether the requirement is part of the current project.")
    detail: str = Field(..., description="The detailed description of the user requirement.")
    priority: RequirementPriorityEnum = Field(..., description="The relative importance of this user requirement.")
    covered_usr: RequirementCoverageEnum = Field(..., description="Indicates coverage by another existing requirement.")

class FinalUserRequirementsOutput(BaseModel):
    document_id: Optional[str] = Field(None, description="Identifier (e.g., GCS URI) for the source document, supplied by the agent.")
    extracted_document_content: Optional[str] = Field(None, description="The text content extracted from the source document (supplied by the agent after using an extraction tool).")
    requirements_list: List[UserRequirement] = Field(..., description="A list of user requirements. The calling LLM is responsible for populating this based on the extracted_document_content.")
    generation_summary: Optional[str] = Field(None, description="Summary of the UR generation process. The calling LLM is responsible for generating this.")
    error_message: Optional[str] = Field(None, description="Optional field for the LLM to indicate any issues encountered during its generation process based on the provided content.")

def generate_user_requirements(
    document_content: str,
    document_id: Optional[str],
    generation_guidelines: Optional[str] = "Generate comprehensive user requirements based on the document content, ensuring all fields of the UserRequirement model are considered."
) -> FinalUserRequirementsOutput:
    """
    Structures input document content and ID to facilitate user requirement generation by an LLM.

    Workflow Expectation:
    1. The agent first calls an extraction tool (e.g., 'extract_information') to get 'extracted_text' from a GCS URI.
    2. The agent then calls this tool ('generate_user_requirements'), passing the 'extracted_text' as 'document_content'
       and the GCS URI as 'document_id'.
    3. This tool returns a structure containing this 'document_content' and 'document_id' along with placeholders.
    4. The agent uses this output to perform detailed analysis and formulate the actual 'requirements_list'
       and 'generation_summary'.
    """
    print(f"Tool 'generate_user_requirements' invoked.")
    print(f"Document ID received: {document_id if document_id else 'N/A'}")
    # Log first 100 chars for tracing, full content is available in 'document_content' variable
    print(f"Document Content received (first 100 chars): {document_content[:100]}...")
    print(f"Guidelines: {generation_guidelines}")

    # Example placeholder requirement. The LLM agent will replace this.
    example_req_list = [
        UserRequirement(
            id="USR_LLM_GENERATED_001",
            name="Placeholder: LLM to define requirement name",
            source=document_id if document_id else "Unknown_Source",
            type=RequirementTypeEnum.ORIGINAL,
            scope=RequirementScopeEnum.IN_SCOPE,
            detail="Placeholder: LLM to provide detailed requirement based on the 'extracted_document_content'.",
            priority=RequirementPriorityEnum.MEDIUM,
            covered_usr=RequirementCoverageEnum.NO
        )
    ]
    
    summary = (
        "Placeholder summary: The LLM should replace this. "
        "Analyze the 'extracted_document_content' (which is the 'document_content' argument passed to this tool) "
        "to generate a list of UserRequirement objects and a meaningful summary. "
        "Describe how the content was used, the number of requirements, and any observations."
    )

    return FinalUserRequirementsOutput(
        document_id=document_id,
        extracted_document_content=document_content,
        requirements_list=example_req_list, # LLM (Agent) is responsible for generating the actual list
        generation_summary=summary, # LLM (Agent) is responsible for generating the actual summary
        error_message=None # LLM can populate this in its subsequent processing if needed
    )

generate_user_requirements_tool = FunctionTool(generate_user_requirements)
