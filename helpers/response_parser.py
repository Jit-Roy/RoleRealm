"""
Helper utilities for parsing LLM responses.
"""

import json
from typing import Dict, Any


def parse_json_response(response_text: str) -> Dict[str, Any]:
    """
    Parse JSON response from LLM, handling markdown code blocks.
    
    Args:
        response_text: Raw response text from the model
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        json.JSONDecodeError: If the response cannot be parsed as JSON
    """
    response_text = response_text.strip()
    
    # Remove markdown code blocks
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]
    
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    response_text = response_text.strip()
    
    return json.loads(response_text)
