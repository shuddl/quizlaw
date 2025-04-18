import logging
from typing import Optional, Dict, Any, List

from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from app.core.config import settings

# Set up logger
logger = logging.getLogger(__name__)


class OpenAIServiceError(Exception):
    """Base exception for OpenAI service errors."""
    pass


class OpenAIService:
    """Service for interacting with OpenAI APIs."""
    
    def __init__(self):
        """Initialize the OpenAI service with API key from settings."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(OpenAIServiceError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def generate_text(
        self,
        prompt: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 500,
        system_message: Optional[str] = None,
    ) -> str:
        """
        Generate text using OpenAI's chat completions API.
        
        Args:
            prompt: The user prompt to send to the model
            model: The model to use (default: gpt-4-turbo-preview)
            temperature: Controls randomness (0-1, lower is more deterministic)
            max_tokens: Maximum number of tokens to generate
            system_message: Optional system message to guide model behavior
            
        Returns:
            Generated text as a string
        """
        try:
            messages = []
            
            # Add system message if provided
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            # Add user prompt
            messages.append({"role": "user", "content": prompt})
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract and return the generated text
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise OpenAIServiceError(f"Error calling OpenAI API: {str(e)}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(OpenAIServiceError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def generate_json(
        self,
        prompt: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 500,
        system_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON using OpenAI's chat completions API.
        
        Args:
            prompt: The user prompt to send to the model
            model: The model to use (default: gpt-4-turbo-preview)
            temperature: Controls randomness (0-1, lower is more deterministic)
            max_tokens: Maximum number of tokens to generate
            system_message: Optional system message to guide model behavior
            
        Returns:
            Generated response as a dictionary
        """
        try:
            messages = []
            
            # Add system message if provided
            if system_message:
                messages.append({"role": "system", "content": system_message})
            else:
                # Default system message for JSON generation
                messages.append({
                    "role": "system", 
                    "content": "You are a helpful assistant that responds with valid JSON."
                })
            
            # Add user prompt
            messages.append({"role": "user", "content": prompt})
            
            # Call OpenAI API with JSON mode
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            
            # Parse and return the JSON response
            import json
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            logger.error(f"Error calling OpenAI API for JSON: {str(e)}")
            raise OpenAIServiceError(f"Error calling OpenAI API for JSON: {str(e)}") from e