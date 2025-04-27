import os
import chromadb
from sentence_transformers import SentenceTransformer
import logging
from llm_handler import LLMHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGInferencePipeline:
    def __init__(self, persist_directory=None, llm_provider="openai", model_name=None):
        """Initialize the RAG pipeline
        
        Args:
            persist_directory (str): Directory to persist vector store
            llm_provider (str): The LLM provider to use - "openai", "anthropic", or "ollama"
            model_name (str): Specific model name to use (optional)
        """
        self.persist_directory = persist_directory
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.client = None
        self.collection = None
        self.encoder = None
        self.llm_handler = None
        self._initialize_pipeline()

    def _initialize_pipeline(self):
        """Initialize the RAG pipeline with ChromaDB and SentenceTransformer"""
        try:
            logger.info("Initializing RAG pipeline...")
            
            # Initialize ChromaDB client - use in-memory client for testing
            self.client = chromadb.Client()
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="traffic_incidents",
                metadata={"description": "Traffic incidents from Austin"}
            )
            
            # Initialize sentence transformer
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize LLM handler with specified provider
            self.llm_handler = LLMHandler(provider=self.llm_provider, model_name=self.model_name)
            
            logger.info(f"RAG pipeline initialized successfully with {self.llm_provider} provider")
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            raise

    def query(self, query_text, top_k=5):
        """
        Query the RAG system and generate a response
        
        Args:
            query_text (str): The query text
            top_k (int): Number of top results to return
            
        Returns:
            dict: Query results with relevant documents, scores, and generated response
        """
        try:
            logger.info(f"Processing query: {query_text}")
            
            # Encode query
            query_embedding = self.encoder.encode(query_text).tolist()
            
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'score': results['distances'][0][i],
                    'id': results['ids'][0][i]
                })
            
            # Generate response using LLM if available
            llm_response = None
            if self.llm_handler and self.llm_handler.is_configured():
                try:
                    llm_response = self.llm_handler.generate_response(
                        query_text,
                        formatted_results
                    )
                except Exception as llm_error:
                    logger.error(f"LLM response generation failed: {llm_error}")
                    llm_response = "Error: Unable to generate LLM response"
            
            response = {
                'documents': formatted_results,
                'llm_response': llm_response
            }
            
            logger.info(f"Query completed. Found {len(formatted_results)} relevant documents")
            return response
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    def add_documents(self, documents, ids=None):
        """
        Add new documents to the RAG system
        
        Args:
            documents (list): List of document texts to add
            ids (list): Optional list of IDs for the documents
        """
        try:
            logger.info(f"Adding {len(documents)} documents to the RAG system")
            
            # Generate embeddings
            embeddings = self.encoder.encode(documents).tolist()
            
            # Generate IDs if not provided
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(documents))]
            
            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                ids=ids
            )
            
            logger.info("Documents added successfully")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

def main():
    # Example usage
    persist_dir = "/app/vector_index"
    
    # Initialize with different providers
    providers = {
        "openai": "gpt-4-turbo-preview",
        "anthropic": "claude-3-opus-20240229",
        "ollama": "llama2"  # or any other model you have pulled
    }
    
    for provider, model in providers.items():
        try:
            print(f"\nTesting {provider} provider with {model}")
            rag_pipeline = RAGInferencePipeline(persist_dir, llm_provider=provider, model_name=model)
            
            # Example query
            query = "What traffic incidents happened recently?"
            results = rag_pipeline.query(query)
            
            print("\nResults:")
            for i, result in enumerate(results['documents'], 1):
                print(f"\nResult {i}:")
                print(f"Document: {result['id']}")
                print(f"Score: {result['score']}")
                print(f"Text: {result['text'][:300]}...")
            
            if results['llm_response']:
                print(f"\n{provider.capitalize()} Response:")
                print(results['llm_response'])
                
        except Exception as e:
            print(f"Error with {provider}: {e}")
            continue

if __name__ == "__main__":
    main() 