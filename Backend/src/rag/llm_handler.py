import os
import logging
import json
import requests
import time
from typing import Optional, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LLMHandler:
    # Define supported models for each provider
    SUPPORTED_MODELS = {
        "openai": [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo"
        ],
        "anthropic": [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        "ollama": [
            "llama3.1",
            "deepseek-r1",
            "nomic-embed-text"
        ]
    }

    def __init__(self, provider: str = "openai", model_name: Optional[str] = None):
        """Initialize the LLM handler with specified provider and model
        
        Args:
            provider (str): The model provider - "openai", "anthropic", or "ollama"
            model_name (str): Name of the specific model to use
        """
        try:
            self.provider = provider.lower()
            if self.provider not in self.SUPPORTED_MODELS:
                raise ValueError(f"Unsupported provider: {self.provider}. Supported providers: {list(self.SUPPORTED_MODELS.keys())}")

            # Initialize provider-specific client and model
            self._initialize_client(model_name)
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM handler: {e}")
            raise

    def _initialize_client(self, model_name: Optional[str]) -> None:
        """Initialize the appropriate client based on provider"""
        if self.provider == "openai":
            self._init_openai(model_name)
        elif self.provider == "anthropic":
            self._init_anthropic(model_name)
        elif self.provider == "ollama":
            self._init_ollama(model_name)

    def _init_openai(self, model_name: Optional[str]) -> None:
        """Initialize OpenAI client"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model_name or os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        
        # Validate model
        if self.model not in self.SUPPORTED_MODELS["openai"]:
            logger.warning(f"Model {self.model} not in supported list: {self.SUPPORTED_MODELS['openai']}")
        
        # Test connection
        try:
            self.client.models.list()
            logger.info(f"OpenAI LLM handler initialized with model: {self.model}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to OpenAI API: {e}")

    def _init_anthropic(self, model_name: Optional[str]) -> None:
        """Initialize Anthropic client"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = model_name or os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
        
        # Validate model
        if self.model not in self.SUPPORTED_MODELS["anthropic"]:
            logger.warning(f"Model {self.model} not in supported list: {self.SUPPORTED_MODELS['anthropic']}")
        
        logger.info(f"Anthropic LLM handler initialized with model: {self.model}")

    def _init_ollama(self, model_name: Optional[str]) -> None:
        """Initialize Ollama connection"""
        self.model = model_name or os.getenv('OLLAMA_MODEL', 'llama3.1')
        
        # Get available models and validate
        try:
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code != 200:
                raise ConnectionError("Ollama service not available")
            
            available_models = [model["name"].split(":")[0] for model in response.json().get("models", [])]
            if self.model not in available_models:
                raise ValueError(f"Model {self.model} not available in Ollama. Available models: {available_models}")
            
            logger.info(f"Ollama LLM handler initialized with model: {self.model}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Ollama service: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, query: str, context_docs: list, max_tokens: int = 500) -> str:
        """Generate a response using the configured LLM with retry logic
        
        Args:
            query (str): The user's query
            context_docs (list): List of relevant documents from vector store
            max_tokens (int): Maximum number of tokens in the response
            
        Returns:
            str: Generated response from the LLM
        """
        try:
            # Prepare the prompt with context
            context_text = "\n".join([doc['text'] for doc in context_docs])
            
            prompt = f"""Based on the following traffic incident information, please answer the query.

Context information:
{context_text}

Query: {query}

Please provide a clear and concise response based only on the information provided in the context."""

            if self.provider == "openai":
                return self._generate_openai(prompt, max_tokens)
            elif self.provider == "anthropic":
                return self._generate_anthropic(prompt, max_tokens)
            elif self.provider == "ollama":
                return self._generate_ollama(prompt, max_tokens)
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise

    def _generate_openai(self, prompt: str, max_tokens: int) -> str:
        """Generate response using OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides information about traffic incidents."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content

    def _generate_anthropic(self, prompt: str, max_tokens: int) -> str:
        """Generate response using Anthropic"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=0.7,
            system="You are a helpful assistant that provides information about traffic incidents.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def _generate_ollama(self, prompt: str, max_tokens: int) -> str:
        """Generate response using Ollama"""
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': self.model,
                'prompt': prompt,
                'system': "You are a helpful assistant that provides information about traffic incidents.",
                'options': {
                    'temperature': 0.7,
                    'num_predict': max_tokens
                }
            },
            stream=False
        )
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            raise Exception(f"Ollama API error: {response.text}")

    def is_configured(self) -> bool:
        """Check if the LLM handler is properly configured"""
        try:
            if self.provider == "openai":
                self.client.models.list()
                return True
            elif self.provider == "anthropic":
                return bool(self.api_key)
            elif self.provider == "ollama":
                response = requests.get('http://localhost:11434/api/tags')
                return response.status_code == 200
            return False
        except Exception as e:
            logger.error(f"Configuration check failed: {e}")
            return False 