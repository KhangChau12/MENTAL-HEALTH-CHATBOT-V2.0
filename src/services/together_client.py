"""
Together AI Client - Service for interacting with Together AI API
Compatible with new AI-powered transition logic
"""

import logging
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

# Global client instance
_together_client = None
_client_initialized = False

def get_together_client():
    """
    Get Together AI client instance
    
    Returns:
        Together client or None if not available
    """
    global _together_client, _client_initialized
    
    if _client_initialized:
        return _together_client
    
    try:
        # Import Together client
        from together import Together
        
        # Get API key from environment or config
        api_key = os.getenv('TOGETHER_API_KEY')
        if not api_key:
            try:
                from config import TOGETHER_API_KEY
                api_key = TOGETHER_API_KEY
            except ImportError:
                logger.error("Together API key not found in environment or config")
                return None
        
        if not api_key:
            logger.error("Together API key is empty")
            return None
        
        # Initialize client
        _together_client = Together(api_key=api_key)
        _client_initialized = True
        
        logger.info("Together AI client initialized successfully")
        return _together_client
        
    except ImportError:
        logger.error("Together package not installed. Install with: pip install together")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Together AI client: {e}")
        return None

def test_together_connection() -> bool:
    """
    Test connection to Together AI API
    
    Returns:
        True if connection is working, False otherwise
    """
    try:
        client = get_together_client()
        if not client:
            return False
        
        # Get model from config
        model = os.getenv('TOGETHER_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free')
        
        # Make a minimal test request
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1,
            temperature=0.1
        )
        
        return response is not None
        
    except Exception as e:
        logger.error(f"Together AI connection test failed: {e}")
        return False

def generate_chat_completion(
    messages: List[Dict], 
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    **kwargs
) -> Optional[Any]:
    """
    Generate chat completion using Together AI
    
    Args:
        messages: List of conversation messages
        model: Model to use (defaults from config)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        **kwargs: Additional parameters
        
    Returns:
        API response or None if failed
    """
    try:
        client = get_together_client()
        if not client:
            logger.error("Together AI client not available")
            return None
        
        # Set defaults
        if model is None:
            model = os.getenv('TOGETHER_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free')
        if max_tokens is None:
            max_tokens = int(os.getenv('AI_MAX_TOKENS', '200'))
        if temperature is None:
            temperature = float(os.getenv('AI_TEMPERATURE', '0.7'))
        
        # Prepare API parameters
        params = {
            'model': model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature
        }
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Make API call
        response = client.chat.completions.create(**params)
        
        logger.debug(f"Together AI request completed: {len(messages)} messages")
        return response
        
    except Exception as e:
        logger.error(f"Together AI request failed: {e}")
        return None

def extract_text_from_response(response) -> str:
    """
    Extract text content from Together AI response
    
    Args:
        response: Together AI API response
        
    Returns:
        Extracted text or error message
    """
    try:
        if not response:
            return "Xin lỗi, tôi không thể phản hồi ngay bây giờ."
        
        # Extract content from response
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                content = choice.message.content
                if content:
                    return content.strip()
        
        logger.warning("Unexpected response format from Together AI")
        return "Tôi đang gặp khó khăn trong việc phản hồi. Vui lòng thử lại."
        
    except Exception as e:
        logger.error(f"Error extracting text from response: {e}")
        return "Đã xảy ra lỗi khi xử lý phản hồi."

def get_client_status() -> Dict:
    """
    Get status information about the Together AI client
    
    Returns:
        Dictionary with client status information
    """
    global _client_initialized, _together_client
    
    status = {
        'initialized': _client_initialized,
        'client_available': _together_client is not None,
        'api_key_configured': bool(os.getenv('TOGETHER_API_KEY')),
        'connection_tested': False
    }
    
    # Test connection if client is available
    if _together_client:
        try:
            status['connection_tested'] = test_together_connection()
        except:
            status['connection_tested'] = False
    
    return status

# Backward compatibility functions
def initialize_together_client() -> bool:
    """
    Initialize Together AI client (backward compatibility)
    
    Returns:
        True if successful, False otherwise
    """
    client = get_together_client()
    return client is not None

def check_api_health() -> Dict:
    """
    Check Together AI API health status
    
    Returns:
        Dictionary with health status information
    """
    try:
        client = get_together_client()
        if not client:
            return {
                'status': 'error',
                'message': 'Client not initialized',
                'available': False
            }
        
        # Test connection
        if test_together_connection():
            return {
                'status': 'healthy',
                'message': 'API is responding',
                'available': True,
                'model': os.getenv('TOGETHER_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free')
            }
        else:
            return {
                'status': 'error',
                'message': 'API not responding',
                'available': False
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Health check failed: {str(e)}',
            'available': False
        }

def get_model_info() -> Dict:
    """
    Get information about the current model configuration
    
    Returns:
        Dictionary with model information
    """
    return {
        'model_name': os.getenv('TOGETHER_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'),
        'provider': 'Together AI',
        'max_tokens': int(os.getenv('AI_MAX_TOKENS', '200')),
        'temperature': float(os.getenv('AI_TEMPERATURE', '0.7')),
        'api_key_configured': bool(os.getenv('TOGETHER_API_KEY'))
    }

# Module level convenience functions
def quick_chat_request(prompt: str, system_prompt: str = None) -> str:
    """
    Quick function to make a simple chat request
    
    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        
    Returns:
        Response text or error message
    """
    try:
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = generate_chat_completion(messages, max_tokens=200, temperature=0.7)
        
        return extract_text_from_response(response)
        
    except Exception as e:
        logger.error(f"Quick chat request failed: {e}")
        return f"Lỗi: {str(e)}"

# Auto-initialize on import (optional)
def _auto_initialize():
    """Auto-initialize client on module import"""
    try:
        get_together_client()
    except:
        pass  # Fail silently on import

# Uncomment next line to auto-initialize on import
_auto_initialize()