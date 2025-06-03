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
    """
    Represents a single generated user requirement with detailed attributes.
    Describes what a user needs to be able to *do* with a system, product, or service.
    """
    id: str = Field(..., description="Unique identifier for the user requirement (e.g., USR0150).", examples=["USR0150"])
    name: str = Field(..., description="A concise overview or name for the user requirement (VARCHAR).")
    source: str = Field(..., description="The name of the source file or document from which this requirement was derived (CHAR).")
    type: RequirementTypeEnum = Field(..., description="Categorizes the origin or nature of the requirement (Original or Change Request).")
    scope: RequirementScopeEnum = Field(..., description="Defines whether the requirement is part of the current project, release, or sprint (In-Scope or Out-Scope).")
    detail: str = Field(..., description="The actual detailed description of the user requirement – what the user needs to do.")
    priority: RequirementPriorityEnum = Field(..., description="The relative importance of this user requirement compared to others (High, Medium, Low).")
    covered_usr: RequirementCoverageEnum = Field(..., description="Indicates whether this requirement is covered by or duplicates another existing user requirement/story (Yes or No).")

class FinalUserRequirementsOutput(BaseModel):
    """
    Defines the structured output for the final set of user requirements.
    """
    document_id: Optional[str] = Field(None, description="Identifier for the source document(s) from which requirements were derived.")
    requirements_list: List[UserRequirement] = Field(..., description="A list of generated user requirements.")
    generation_summary: Optional[str] = Field(None, description="Summary of the UR generation process and any overall observations.")

def generate_user_requirements(
    extracted_information: Dict[str, Any], # This would typically be the output from extract_information_tool
    generation_guidelines: Optional[str] = "Generate comprehensive user requirements based on the extracted information, ensuring all fields of the UserRequirement model are considered."
) -> FinalUserRequirementsOutput:
    """
    Generates final user requirements based on previously extracted information and guidelines.

    The calling LLM Agent is responsible for using the extracted_information (likely from
    the extract_specific_details_from_text tool) and any guidelines to formulate
    the final user requirements, populating all fields of the UserRequirement model.
    ADK handles parsing the LLM's JSON output into this model.

    Args:
        extracted_information: A dictionary or Pydantic model instance containing structured
                               information previously extracted from source documents
                               (e.g., the output of `extract_specific_details_from_text`).
        generation_guidelines: Specific instructions or focus for generating the user requirements.
                               The LLM should be prompted to consider all new fields such as
                               'id', 'name', 'source', 'type', 'scope', 'detail', 'priority', and 'covered_usr'.

    Returns:
        A FinalUserRequirementsOutput object.
    """
    print(f"Tool 'generate_user_requirements' invoked.")
    print(f"Guidelines: {generation_guidelines}")
    print(f"Based on extracted info from document ID: {extracted_information.get('source_document_id', 'N/A')}, summary: {extracted_information.get('summary_of_extraction', 'N/A')}")

    # Placeholder: The LLM would generate this based on its understanding
    # of the extracted_information and guidelines, creating a list of UserRequirement instances.
    # Example placeholder for one requirement (LLM would generate the actual data and list):
    # example_req = UserRequirement(
    #     id="USR001",
    #     name="User Authentication Overview",
    #     source=extracted_information.get("source_document_id", "Unknown_Source.pdf"),
    #     type=RequirementTypeEnum.ORIGINAL,
    #     scope=RequirementScopeEnum.IN_SCOPE,
    #     detail="The system must allow users to authenticate using a username and password.",
    #     priority=RequirementPriorityEnum.HIGH,
    #     covered_usr=RequirementCoverageEnum.NO
    # )

    return FinalUserRequirementsOutput(
        document_id=extracted_information.get("source_document_id"),
        requirements_list=[
            # example_req # LLM would generate a list of such requirements.
            # For the tool's direct execution (without LLM filling it), it returns an empty list or example.
        ],
        generation_summary="Placeholder: LLM to provide summary of UR generation. Ensure all UserRequirement fields are populated."
    )

# Create FunctionTools from the functions
generate_user_requirements_tool = FunctionTool(generate_user_requirements)
