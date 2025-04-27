# Traffic API to RAG Component

This component of the River Hackathon project fetches data from traffic APIs, processes it, and converts it to PDFs for ingestion into a RAG (Retrieval Augmented Generation) system.

## Installation

Install dependencies:
```
pip install -r requirements.txt
```

## Usage

Run the script to fetch traffic data and convert it to PDFs:

```bash
python traffic_api_to_rag.py
```

The script will:
1. Fetch the latest traffic incident data from the Austin Traffic API
2. Process and clean the data
3. Create individual PDFs for each incident
4. Create a summary PDF with all incidents
5. Generate a metadata JSON file

## Output

All generated files are stored in the `traffic_pdfs` directory:
- `incident_[ID].pdf`: Individual PDF for each traffic incident
- `all_incidents_summary.pdf`: Summary PDF containing all incidents
- `traffic_incidents_metadata.json`: Metadata file with information about all incidents

## Integration with RAG System

After running this script, you can ingest the generated PDFs into your RAG system. This typically involves:

1. Pointing your document processor to the `traffic_pdfs` directory
2. Processing and indexing the documents
3. Saving the index for use with your chat system

Example for RAG integration (see `rag_integration_example.py`):

```python
from webai import DocumentProcessor, RAGPipeline

# Initialize the RAG document processor
doc_processor = DocumentProcessor()

# Point to the directory with PDFs
pdf_directory = "./traffic_pdfs/"

# Process and index the documents
rag_pipeline = RAGPipeline()
rag_pipeline.ingest_documents(
    directory=pdf_directory,
    file_types=[".pdf"],
    chunk_size=1000,
    chunk_overlap=200
)

# Save the index for future use
rag_pipeline.save_index("traffic_incidents_index")
```

## Configuration

You can modify the following constants in the `traffic_api_to_rag.py` script:
- `API_URL`: The URL for the traffic incident API
- `API_LIMIT`: Maximum number of records to fetch
- `PDF_OUTPUT_DIR`: Directory to save generated PDFs
- `RAG_INDEX_NAME`: Name for the RAG index (used in examples)

## Integration with Dashboard

This component serves as the first step in the RAG pipeline for the River Hackathon project. The output PDFs can be consumed by the dashboard's chat widget to provide intelligent responses to queries about traffic incidents.

### Dashboard Chat Widget Implementation

After the PDFs are ingested into the RAG system, you can implement a chat widget in the dashboard that connects to the RAG system API. The chat widget will:

1. Take user queries about traffic incidents
2. Send them to the RAG system
3. Retrieve relevant information from the indexed documents
4. Display the results to the user in a conversational format

For more details on implementing the chat widget, refer to the dashboard documentation.
