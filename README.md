Get started by customizing your environment (defined in the .idx/dev.nix file) with the tools and IDE extensions you'll need for your project!

Learn more at https://firebase.google.com/docs/studio/customize-workspace

# 🧠 ADK Hackathon - Multi-Agent AI Assistant Platform: UR Agent

## Features

- 🗂️ **GCS Bucket Management**: Create, list, and manage GCS buckets for file storage.
- 📄 **Extract Information**: 

## Architecture

The project follows a modular architecture based on the ADK framework:
![UR Agent Architecture](media/workflow.pdf)

## Prerequisites

- Python 3.11+ with uv
- Google Cloud project with Vertex AI API enabled
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- Access to Vertex AI and Cloud Storage

## Installation

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync # or uv pip install -r requirements.txt

# Configure your Google Cloud project
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"

# Enable required Google Cloud services
gcloud services enable aiplatform.googleapis.com --project=${GOOGLE_CLOUD_PROJECT}
gcloud services enable storage.googleapis.com --project=${GOOGLE_CLOUD_PROJECT}

# Set up IAM permissions
gcloud projects add-iam-policy-binding ${GOOGLE_CLOUD_PROJECT} \
    --member="user:YOUR_EMAIL@domain.com" \
    --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding ${GOOGLE_CLOUD_PROJECT} \
    --member="user:YOUR_EMAIL@domain.com" \
    --role="roles/storage.objectAdmin"

# Set up Gemini API key
# Get your API key from Google AI Studio: https://ai.google.dev/
export GOOGLE_API_KEY=your_gemini_api_key_here

# Set up authentication credentials
# Option 1: Use gcloud application-default credentials (recommended for development)
gcloud auth application-default login

# Option 2: Use a service account key (for production or CI/CD environments)
# Download your service account key from GCP Console and set the environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
```

## Usage

### Running the Agent

There are many ways to run the agent:

```bash
# Option 1: Use ADK web interface (recommended for interactive usage)
adk web 

# Option 2: Run the agent directly in the terminal
adk run rag

# Option 3:
adk api_server
```

The web interface provides a chat-like experience for interacting with the agent, while the direct run option is suitable for scripting and automated workflows.

## Configuration

Edit `src/config/__init__.py` to customize your settings:

- `PROJECT_ID`: Your Google Cloud project ID
- `LOCATION`: Default location for Vertex AI and GCS resources
- `GCS_DEFAULT_*`: Defaults for GCS operations
- `AGENT_*`: Settings for the agent

## Supported File Types

The engine supports various document types, including:
- PDF
- TXT
- DOC/DOCX
- XLS/XLSX
- PPT/PPTX
- CSV
- JSON
- HTML
- Markdown

## Troubleshooting

### Common Issues

- **403 Errors**: Make sure you've authenticated with `gcloud auth application-default login`
- **Resource Exhausted**: Check your quota limits in the GCP Console
- **Upload Issues**: Ensure your file format is supported and file size is within limits

## References

- [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- [Google Cloud Storage](https://cloud.google.com/storage)
- [Prompt Engineering](https://www.kaggle.com/whitepaper-prompt-engineering)
- [Foundational LLMs and Text Generation](https://www.kaggle.com/whitepaper-foundational-llm-and-text-generation)
- [Agents](https://www.kaggle.com/whitepaper-agents)
- [Agents Companion](https://www.kaggle.com/whitepaper-agent-companion)
- [Embeddings & Vector Stores](https://www.kaggle.com/whitepaper-embeddings-and-vector-stores)
- [Operationalizing GenAI on Vertex AI using MLOps](https://www.kaggle.com/whitepaper-operationalizing-generative-ai-on-vertex-ai-using-mlops)
- [Solving Domain-Specific Problems using LLMs](https://www.kaggle.com/whitepaper-solving-domains-specific-problems-using-llms)


## Example Commands

Below is a complete example workflow showing how to set up the entire environment:

### 1. List all GCS buckets

```text
List all GCS buckets and its information.
```

### 2. Create a bucket for Foundation LLMs

```text
Create a GCS bucket named "ur-agent-data-source".
```

### 3. Upload a document

```text
Upload the file "RFP.pdf" to GCS bucket "gs://ur-agent-data-source/" and keep the same destination blob name. Do not ask for confirmation.
```

### 4. Create a RAG corpus
```text
Create a RAG corpus named "ur-agent-knowledge-base" with the same description.
```

### 5. Import a document into RAG corpus
```text
Import all the files in "gs://ur-agent-data-source/" into the RAG corpus "ur-agent-knowledge-base".
```