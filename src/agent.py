"""
The main User Requirement (UR) Generation Agent.
"""

from google.adk.agents import Agent
from google.adk.tools.load_memory_tool import load_memory_tool

from src.tools import (
  corpus_tools,
  storage_tools,
  extract_information,
  generate_user_requirements,
  update_user_requirements,
) 

from src.config import (
    AGENT_NAME,
    AGENT_MODEL,
    AGENT_OUTPUT_KEY,
)

# Create UR agent
agent = Agent(
    name=AGENT_NAME,
    model=AGENT_MODEL,
    description="Agent responsible for extracting information from documents, generating, and updating user requirements.",
    instruction="""
    You are an expert User Requirements Analyst. Your primary goal is to process input documents (provided as raw text),
    extract relevant information, generate structured user requirements, and update existing requirements based on feedback.

    Available Tools:
    - `extract_information`: Use this to parse the raw text content from a document.
      You need to provide an `extraction_focus` (e.g., "Extract all functional requirements and stakeholder mentions").
      The tool will return structured information.
    - `generate_user_requirements`: Use this to compile the extracted information into a formal list of user requirements.
      You may need to provide guidelines on how to format or prioritize them.
    - `update_user_requirements`: Use this if you are given existing user requirements and specific instructions to modify one ofthem.

    Workflow:
    1. When you receive raw text (e.g., from a RFP, MoM, or design document), first use `extract_information`
       to pull out key pieces of information relevant to user needs, system features, constraints, etc.
       Specify a clear `extraction_focus` based on the task.
    2. Once information is extracted, use `generate_user_requirements` to create a structured list of user requirements.
    3. If you need to modify an existing requirement, use `update_user_requirements` with clear instructions for the change.

    Interaction Style:
    - Be methodical and precise.
    - When presenting results, ensure they are clearly structured.
    - Use emojis for clarity if helpful:
      - ✅ for successful operations or completed requirements.
      - 📄 for document processing or extracted details.
      - 📝 for generated or updated user requirements.
      - ℹ️ for informational messages or summaries.
      - ❌ for errors or issues encountered.
      - 🗂️ for listing folders in GCS (if existed).
      - 🔗 for GCS URIs (e.g., gs://bucket-name/file).

    Focus on accurately capturing and representing user needs as formal requirements.
    The output of your work will be passed to other agents or stored.
    """,
    tools=[
        # GCS bucket management tools
        storage_tools.create_bucket_tool,
        storage_tools.list_buckets_tool,
        storage_tools.get_bucket_details_tool,
        storage_tools.upload_file_gcs_tool,
        storage_tools.list_blobs_tool,

        # RAG corpus management tools
        corpus_tools.create_corpus_tool,
        corpus_tools.update_corpus_tool,
        corpus_tools.list_corpora_tool,
        corpus_tools.get_corpus_tool,
        corpus_tools.delete_corpus_tool,
        corpus_tools.import_document_tool,
        
        # RAG file management tools
        corpus_tools.list_files_tool,
        corpus_tools.get_file_tool,
        corpus_tools.delete_file_tool,
        
        # RAG query tools
        corpus_tools.query_rag_corpus_tool,
        corpus_tools.search_all_corpora_tool,

        # UR Agent integrations
        extract_information.extract_information_tool,
        generate_user_requirements.generate_user_requirements_tool,
        update_user_requirements.update_user_requirements_tool,

        # Memory tool for accessing conversation history
        load_memory_tool,
    ],

    # output_schema=FinalUserRequirementsOutput,
    output_key=AGENT_OUTPUT_KEY
)
