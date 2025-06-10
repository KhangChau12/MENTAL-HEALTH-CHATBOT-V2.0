"""
Together AI Service - Enhanced API integration with error handling
"""

import logging
from typing import Dict, List, Optional
from together import Together
from config import Config

logger = logging.getLogger(__name__)

# Global client instance
client = None

def initialize_together_client() -> bool:
    """
    Initialize Together AI client
    
    Returns:
        bool: True if successful, False otherwise
    """
    global client
    
    try:
        if not Config.TOGETHER_API_KEY:
            logger.error("Together API key not provided")
            return False
        
        client = Together(api_key=Config.TOGETHER_API_KEY)
        
        # Test the connection with a simple request
        test_response = client.chat.completions.create(
            model=Config.TOGETHER_MODEL,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        
        if test_response:
            logger.info("Together AI client initialized successfully")
            return True
        else:
            logger.error("Together AI test request failed")
            return False
            
    except Exception as e:
        logger.error(f"Failed to initialize Together AI client: {e}")
        return False

def generate_chat_completion(
    messages: List[Dict], 
    contextual_prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None
) -> Optional[Dict]:
    """
    Generate chat completion using Together AI
    
    Args:
        messages: List of conversation messages
        contextual_prompt: Optional system prompt override
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        API response or None if failed
    """
    global client
    
    try:
        # Initialize client if not already done
        if client is None:
            if not initialize_together_client():
                return None
        
        # Prepare messages
        api_messages = []
        
        # Add system prompt if provided
        if contextual_prompt:
            api_messages.append({
                "role": "system",
                "content": contextual_prompt
            })
        
        # Process conversation messages
        for msg in messages:
            role = msg.get("role", "user")
            
            # Convert 'bot' to 'assistant' for API compatibility
            if role == "bot":
                role = "assistant"
            
            api_messages.append({
                "role": role,
                "content": msg.get("content", "")
            })
        
        # Set parameters with defaults from config
        params = {
            "model": Config.TOGETHER_MODEL,
            "messages": api_messages,
            "max_tokens": max_tokens or Config.AI_MAX_TOKENS,
            "temperature": temperature or Config.AI_TEMPERATURE,
            "top_p": Config.AI_TOP_P,
            "top_k": Config.AI_TOP_K,
            "repetition_penalty": Config.AI_REPETITION_PENALTY,
            "stop": Config.AI_STOP
        }
        
        # Make API call
        response = client.chat.completions.create(**params)
        
        logger.info("Together AI request completed successfully")
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

def check_api_health() -> Dict:
    """
    Check Together AI API health status
    
    Returns:
        Dictionary with health status information
    """
    try:
        if client is None:
            return {
                'status': 'error',
                'message': 'Client not initialized',
                'available': False
            }
        
        # Make a minimal test request
        test_response = client.chat.completions.create(
            model=Config.TOGETHER_MODEL,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        
        if test_response:
            return {
                'status': 'healthy',
                'message': 'API is responding',
                'available': True,
                'model': Config.TOGETHER_MODEL
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
    Get information about the current model
    
    Returns:
        Dictionary with model information
    """
    return {
        'model_name': Config.TOGETHER_MODEL,
        'provider': 'Together AI',
        'max_tokens': Config.AI_MAX_TOKENS,
        'temperature': Config.AI_TEMPERATURE,
        'top_p': Config.AI_TOP_P,
        'top_k': Config.AI_TOP_K
    }