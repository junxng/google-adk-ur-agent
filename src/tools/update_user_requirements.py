from typing import List, Dict, Any, Optional
from google.adk.tools import ToolContext, FunctionTool
from pydantic import BaseModel, Field
from src.tools.generate_user_requirements import (
    UserRequirement,
    RequirementTypeEnum,
    RequirementScopeEnum,
    RequirementPriorityEnum,
    RequirementCoverageEnum
)

class UpdateInstructions(BaseModel):
    """
    Instructions for how to update existing user requirements.
    The LLM should specify which fields of the UserRequirement are to be changed.
    """
    requirement_id_to_update: str = Field(..., description="The ID of the user requirement to update (e.g., USR0150).")
    # Instead of a generic 'changes_requested', prompt LLM to specify changes per field
    # This can be done by making the fields in UserRequirement optional in an "UpdatePayload"
    # or by having the LLM generate the full new UserRequirement object based on changes.
    # For simplicity here, we'll assume the LLM can be instructed to provide values for fields to change.
    updated_fields: Dict[str, Any] = Field(..., description="A dictionary where keys are UserRequirement field names "
                                                            "(e.g., 'detail', 'priority', 'scope') and values are "
                                                            "the new values for those fields.")
    reason_for_update: Optional[str] = Field(None, description="Reason or justification for the update.")

class UpdatedUserRequirementsOutput(BaseModel):
    """
    Defines the structured output after updating user requirements.
    """
    updated_requirement: UserRequirement = Field(..., description="The user requirement after applying updates.")
    update_summary: str = Field(..., description="Summary of the updates made.")
    previous_version_snapshot: Optional[UserRequirement] = Field(None, description="A snapshot of the requirement before this update.")


def update_user_requirements(
    current_requirements_list: List[Dict[str, Any]], # Could be List[UserRequirement] if passed as model instances
    update_instructions: UpdateInstructions
) -> UpdatedUserRequirementsOutput:
    """
    Updates an existing user requirement based on provided instructions.

    The calling LLM Agent identifies the requirement to update from 'current_requirements_list'
    using 'update_instructions.requirement_id_to_update'. It then applies the changes specified in
    'update_instructions.updated_fields' to formulate the updated requirement.
    The 'updated_fields' dictionary should contain key-value pairs for the fields of the
    UserRequirement model that need to be changed.
    ADK handles parsing the LLM's JSON output into UpdatedUserRequirementsOutput.

    Args:
        current_requirements_list: A list of existing user requirements (e.g., from Final UR or Knowledge Base).
                                   Each item should be a dictionary representation of a UserRequirement.
        update_instructions: A Pydantic model containing the ID of the requirement to update
                             and a dictionary of fields with their new values.

    Returns:
        An UpdatedUserRequirementsOutput object.
    """
    print(f"Tool 'update_user_requirements' invoked.")
    print(f"Updating requirement ID: {update_instructions.requirement_id_to_update}")
    print(f"Changes requested via updated_fields: {update_instructions.updated_fields}")

    found_req_dict = None
    original_req_index = -1

    for i, req_dict in enumerate(current_requirements_list):
        if req_dict.get("id") == update_instructions.requirement_id_to_update:
            found_req_dict = req_dict
            original_req_index = i
            break
    
    if not found_req_dict:
        raise ValueError(f"Requirement ID {update_instructions.requirement_id_to_update} not found in current requirements list.")

    # Create a snapshot of the original requirement
    try:
        previous_requirement = UserRequirement(**found_req_dict)
    except Exception as e:
        print(f"Warning: Could not parse original requirement into UserRequirement model: {e}")
        previous_requirement = None # Or handle error more strictly

    # Placeholder logic for update: The LLM is expected to generate the complete `updated_fields`
    # dictionary with values that are compliant with the UserRequirement model's field types (including enums).
    # ADK's LLM integration handles passing the schema, so the LLM knows about enum constraints.
    
    updated_data = found_req_dict.copy()
    # Validate and apply updates from updated_fields
    for field_name, new_value in update_instructions.updated_fields.items():
        if field_name not in UserRequirement.model_fields:
            print(f"Warning: Field '{field_name}' is not a valid UserRequirement field. Skipping.")
            continue
        
        # Potentially add more specific type/enum validation here if needed,
        # though the LLM should get it right based on schema.
        # Example for enum conversion (if LLM sends string for enum):
        field_type = UserRequirement.model_fields[field_name].annotation
        if hasattr(field_type, '__members__') and isinstance(new_value, str): # Check if it's an Enum and value is string
            try:
                new_value = field_type(new_value) # Attempt to convert string to Enum member
            except ValueError:
                print(f"Warning: Invalid value '{new_value}' for enum field '{field_name}'. LLM should provide a valid enum member. Skipping this field.")
                continue # Skip this field if conversion fails
        updated_data[field_name] = new_value

    try:
        updated_requirement_model = UserRequirement(**updated_data)
    except Exception as e:
        # This indicates the LLM provided data that doesn't match the UserRequirement schema
        # even after potential conversions.
        print(f"Error: Failed to create UserRequirement model from updated data: {e}")
        print(f"Data provided by LLM (for updated_fields merged with original): {updated_data}")
        raise ValueError(f"LLM generated invalid data for updated requirement. Details: {e}")


    return UpdatedUserRequirementsOutput(
        updated_requirement=updated_requirement_model,
        update_summary=f"Successfully processed update for requirement ID: {update_instructions.requirement_id_to_update}. "
                       f"Reason: {update_instructions.reason_for_update or 'Not specified'}.",
        previous_version_snapshot=previous_requirement
    )

# Create FunctionTools from the functions
update_user_requirements_tool = FunctionTool(update_user_requirements)
