"""
OpenRouter API client wrapper.
"""

from openai import OpenAI
from typing import Optional
from config import Config


class GenerativeModel:
    """Model wrapper"""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        """
        Initialize generative model.
        
        Args:
            model_name: Name of the model to use
            api_key: Optional API key (defaults to Config.OPENROUTER_API_KEY)
        """
        self.model_name = model_name
        self.api_key = api_key or Config.OPENROUTER_API_KEY
        
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not set. "
                "Please set it in your .env file or pass it to the constructor."
            )
        
        self._client = OpenAI(
            base_url=Config.OPENROUTER_BASE_URL,
            api_key=self.api_key
        )
    
    def generate_content(self, prompt: str, **kwargs):
        """
        Generate content from prompt.
        
        Args:
            prompt: The text prompt
            **kwargs: Additional parameters (temperature, max_tokens, top_p, frequency_penalty, etc.)
            
        Returns:
            Response object with .text attribute
        """
        try:
            temperature = kwargs.get('temperature', Config.MODEL_TEMPERATURE)
            max_tokens = kwargs.get('max_tokens', Config.MAX_TOKENS)
            top_p = kwargs.get('top_p', 1.0)
            frequency_penalty = kwargs.get('frequency_penalty', 0.0)
            
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty
            )

            class Response:
                def __init__(self, content):
                    self.text = content
                def __str__(self):
                    return self.text
            
            return Response(response.choices[0].message.content)
            
        except Exception as e:

            error_msg = str(e)
            if "429" in error_msg or "rate" in error_msg.lower():
                raise Exception(f"ResourceExhausted: 429 Rate limit exceeded. {error_msg}")
            elif "401" in error_msg or "invalid" in error_msg.lower():
                raise Exception(f"InvalidAPIKey: {error_msg}")
            else:
                raise