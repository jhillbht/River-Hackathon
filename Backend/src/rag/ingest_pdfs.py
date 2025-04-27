import os
import glob
import fitz  # PyMuPDF
from rag_inference import RAGInferencePipeline
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        return None

def main():
    # Initialize RAG pipeline
    persist_dir = "/app/vector_index"
    rag_pipeline = RAGInferencePipeline(persist_dir)
    
    # Get list of PDFs
    pdf_dir = "traffic_pdfs"
    pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    # Process PDFs
    documents = []
    ids = []
    for pdf_file in pdf_files:
        logger.info(f"Processing {pdf_file}")
        text = extract_text_from_pdf(pdf_file)
        if text:
            documents.append(text)
            ids.append(os.path.basename(pdf_file))
    
    # Add documents to vector store
    if documents:
        logger.info(f"Adding {len(documents)} documents to vector store")
        rag_pipeline.add_documents(documents, ids)
        logger.info("Documents added successfully")
        
        # Test query
        query = "What are the recent traffic incidents in Austin?"
        results = rag_pipeline.query(query)
        
        print("\nTest Query Results:")
        if results['documents']:
            for i, result in enumerate(results['documents'], 1):
                print(f"\nResult {i}:")
                print(f"Document: {result['id']}")
                print(f"Score: {result['score']}")
                print(f"Text: {result['text'][:200]}...")
            
            if results['llm_response']:
                print("\nLLM Response:")
                print(results['llm_response'])
        else:
            print("No relevant documents found")
    else:
        logger.warning("No documents were processed successfully")

if __name__ == "__main__":
    main() 