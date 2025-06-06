import copy
from typing import List, Dict, Any, Optional
from google.adk.tools import ToolContext, FunctionTool
from pydantic import BaseModel, Field, ValidationError
from enum import Enum
from src.tools.generate_user_requirements import UserRequirement

class UpdateInstructions(BaseModel):
    """
    Instructions for how to update existing user requirements.
    The LLM should specify which fields of the UserRequirement are to be changed.
    """
    requirement_id_to_update: str = Field(..., description="The ID of the user requirement to update (e.g., USR0150).")
    updated_fields: Dict[str, Any] = Field(..., description="A dictionary where keys are UserRequirement field names "
                                                            "(e.g., 'detail', 'priority', 'scope') and values are "
                                                            "the new values for those fields. The values should be "
                                                            "compatible with the target field types (e.g., 'High' for priority).")
    reason_for_update: Optional[str] = Field(None, description="Reason or justification for the update.")

class UpdatedUserRequirementsOutput(BaseModel):
    """
    Defines the structured output after updating user requirements.
    """
    updated_requirement: UserRequirement = Field(..., description="The user requirement after applying updates.")
    update_summary: str = Field(..., description="Summary of the updates made, including which fields were changed.")
    previous_version_snapshot: UserRequirement = Field(..., description="A snapshot of the requirement before this update.")

def update_user_requirements(
    tool_context: ToolContext,
    current_requirements_list: List[Dict[str, Any]], 
    update_instructions: UpdateInstructions
) -> UpdatedUserRequirementsOutput:
    """
    Updates an existing user requirement based on provided instructions.
    Only fields specified in 'update_instructions.updated_fields' are modified.

    The calling LLM Agent identifies the requirement to update from 'current_requirements_list'
    using 'update_instructions.requirement_id_to_update'. It then applies the changes specified in
    'update_instructions.updated_fields' to formulate the updated requirement.
    ADK handles parsing the LLM's JSON output into UpdatedUserRequirementsOutput.

    Args:
        tool_context: The ADK tool context.
        current_requirements_list: A list of existing user requirements.
                                   Each item MUST be a dictionary representation of a UserRequirement.
        update_instructions: Instructions detailing which requirement to update and what fields to change.

    Returns:
        An UpdatedUserRequirementsOutput object.

    Raises:
        ValueError: If the requirement ID is not found, if the original requirement data is malformed,
                    or if the LLM-provided updates result in an invalid UserRequirement.
    """
    print(f"Tool 'update_user_requirements' invoked for requirement ID: {update_instructions.requirement_id_to_update}")
    print(f"Attempting to apply updates: {update_instructions.updated_fields}")

    found_req_dict_original = None
    for req_dict in current_requirements_list:
        if req_dict.get("id") == update_instructions.requirement_id_to_update:
            found_req_dict_original = copy.deepcopy(req_dict) 
            break
    
    if not found_req_dict_original:
        raise ValueError(f"Requirement ID '{update_instructions.requirement_id_to_update}' not found in current requirements list.")

    try:
        previous_requirement_model = UserRequirement(**found_req_dict_original)
    except ValidationError as e:
        error_detail = e.errors()
        print(f"Critical Error: Original data for requirement ID '{update_instructions.requirement_id_to_update}' is malformed and cannot be parsed into UserRequirement model: {error_detail}")
        print(f"Original data: {found_req_dict_original}")
        raise ValueError(f"Original requirement data for ID '{update_instructions.requirement_id_to_update}' is invalid: {error_detail}")

    updated_data = copy.deepcopy(found_req_dict_original)
    changed_fields_log = []

    for field_name, new_value in update_instructions.updated_fields.items():
        if field_name not in UserRequirement.model_fields:
            print(f"Warning: Field '{field_name}' provided in updated_fields is not a valid UserRequirement field. Skipping this field.")
            continue
        
        updated_data[field_name] = new_value
        
        old_value_display = previous_requirement_model.model_dump().get(field_name)
        if isinstance(old_value_display, Enum):
            old_value_display = old_value_display.value
        
        new_value_display = new_value
        if isinstance(new_value_display, Enum):
             new_value_display = new_value_display.value

        changed_fields_log.append(f"'{field_name}' from '{old_value_display}' to '{new_value_display}'")

    if not update_instructions.updated_fields:
        print("No fields specified for update in 'updated_fields'. Requirement will be based on its original state.")

    try:
        updated_requirement_model = UserRequirement(**updated_data)
    except ValidationError as e:
        error_detail = e.errors()
        print(f"Error: Failed to create UserRequirement model from updated data due to validation errors: {error_detail}")
        print(f"Data provided by LLM (merged with original) that caused failure: {updated_data}")
        print(f"Original updates requested: {update_instructions.updated_fields}")
        raise ValueError(f"LLM-provided updates for requirement ID '{update_instructions.requirement_id_to_update}' resulted in invalid data. Details: {error_detail}")

    if changed_fields_log:
        summary_changes_str = ", ".join(changed_fields_log)
    elif update_instructions.updated_fields:
        summary_changes_str = "Updates were specified but may not have resulted in changes (e.g., invalid field names skipped, or new value matched old value)."
    else:
        summary_changes_str = "No fields were specified for update."

    update_summary_message = (
        f"Update processed for requirement ID: {update_instructions.requirement_id_to_update}. "
        f"Changes: {summary_changes_str}. "
        f"Reason: {update_instructions.reason_for_update or 'Not specified'}."
    )
    print(update_summary_message)

    return UpdatedUserRequirementsOutput(
        updated_requirement=updated_requirement_model,
        update_summary=update_summary_message,
        previous_version_snapshot=previous_requirement_model 
    )

update_user_requirements_tool = FunctionTool(update_user_requirements)
