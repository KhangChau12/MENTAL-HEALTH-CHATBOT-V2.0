"""
Validation utilities for Mental Health Chatbot
Complete validation functions for all data types
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

# Validation patterns
PATTERNS = {
    'session_id': r'^[a-f0-9-]{20,50}$',
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone': r'^[0-9+\-\s()]{10,15}$',
    'language_code': r'^(vi|en)$'
}

# Valid assessment types
VALID_ASSESSMENT_TYPES = [
    'phq9', 'gad7', 'dass21_stress', 'suicide_risk', 'initial_screening'
]

# Valid answer ranges for different assessment types
ANSWER_RANGES = {
    'phq9': {'min': 0, 'max': 3, 'question_count': 9},
    'gad7': {'min': 0, 'max': 3, 'question_count': 7},
    'dass21_stress': {'min': 0, 'max': 3, 'question_count': 7},
    'suicide_risk': {'min': 0, 'max': 3, 'question_count': 5},
    'initial_screening': {'min': 0, 'max': 3, 'question_count': 5}
}

def validate_message(message: str) -> bool:
    """
    Validate user message content
    
    Args:
        message: User message to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(message, str):
        return False
    
    # Check length
    if len(message.strip()) < 1 or len(message) > 2000:
        return False
    
    # Check for only whitespace or special characters
    if not re.search(r'[a-zA-Z0-9\u00C0-\u024F\u1E00-\u1EFF]', message):
        return False
    
    return True

def validate_chat_state(state: Dict) -> bool:
    """
    Validate chat state structure
    
    Args:
        state: Chat state dictionary
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(state, dict):
        return False
    
    # Check required fields
    required_fields = ['current_phase']
    for field in required_fields:
        if field not in state:
            return False
    
    # Validate phase
    valid_phases = ['chat', 'assessment', 'completed']
    if state.get('current_phase') not in valid_phases:
        return False
    
    # Validate optional fields if present
    if 'message_count' in state:
        if not isinstance(state['message_count'], int) or state['message_count'] < 0:
            return False
    
    if 'language' in state:
        if not re.match(PATTERNS['language_code'], state['language']):
            return False
    
    return True

def validate_assessment_type(assessment_type: str) -> bool:
    """
    Validate assessment type
    
    Args:
        assessment_type: Assessment type to validate
        
    Returns:
        True if valid, False otherwise
    """
    return assessment_type in VALID_ASSESSMENT_TYPES

def validate_assessment_data(assessment_data: Dict) -> bool:
    """
    Validate complete assessment data structure
    
    Args:
        assessment_data: Assessment data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(assessment_data, dict):
        return False
    
    # Check required fields
    required_fields = ['assessment_type', 'session_id']
    for field in required_fields:
        if field not in assessment_data:
            logger.warning(f"Missing required field: {field}")
            return False
    
    # Validate assessment type
    if not validate_assessment_type(assessment_data['assessment_type']):
        logger.warning(f"Invalid assessment type: {assessment_data['assessment_type']}")
        return False
    
    # Validate session ID
    if not validate_session_id(assessment_data['session_id']):
        logger.warning(f"Invalid session ID: {assessment_data['session_id']}")
        return False
    
    # Validate optional fields if present
    if 'answers' in assessment_data:
        if not validate_answers(assessment_data['answers'], assessment_data['assessment_type']):
            return False
    
    if 'completed_at' in assessment_data:
        if not validate_datetime_string(assessment_data['completed_at']):
            return False
    
    return True

def validate_answers(answers: Dict, assessment_type: str) -> bool:
    """
    Validate assessment answers
    
    Args:
        answers: Dictionary of question_id -> answer_value
        assessment_type: Type of assessment
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(answers, dict):
        return False
    
    if not assessment_type in ANSWER_RANGES:
        logger.warning(f"Unknown assessment type for validation: {assessment_type}")
        return False
    
    answer_config = ANSWER_RANGES[assessment_type]
    min_val = answer_config['min']
    max_val = answer_config['max']
    expected_count = answer_config['question_count']
    
    # Check answer count (allow partial completion for validation)
    if len(answers) > expected_count:
        logger.warning(f"Too many answers: {len(answers)} > {expected_count}")
        return False
    
    # Validate each answer
    for question_id, answer_value in answers.items():
        # Validate question ID format
        if not isinstance(question_id, str) or len(question_id) < 3:
            logger.warning(f"Invalid question ID: {question_id}")
            return False
        
        # Validate answer value
        if not isinstance(answer_value, (int, float)):
            logger.warning(f"Invalid answer type for {question_id}: {type(answer_value)}")
            return False
        
        if not (min_val <= answer_value <= max_val):
            logger.warning(f"Answer out of range for {question_id}: {answer_value}")
            return False
    
    return True

def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(session_id, str):
        return False
    
    if len(session_id) < 10 or len(session_id) > 100:
        return False
    
    # Allow alphanumeric, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        return False
    
    return True

def validate_datetime_string(dt_string: str) -> bool:
    """
    Validate datetime string in ISO format
    
    Args:
        dt_string: Datetime string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(dt_string, str):
        return False
    
    try:
        datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return True
    except (ValueError, TypeError):
        return False

def validate_export_format(export_format: str) -> bool:
    """
    Validate export format
    
    Args:
        export_format: Export format to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_formats = ['pdf', 'json', 'csv']
    return export_format in valid_formats

def validate_language_code(language: str) -> bool:
    """
    Validate language code
    
    Args:
        language: Language code to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(language, str):
        return False
    
    return re.match(PATTERNS['language_code'], language) is not None

def validate_conversation_history(history: List[Dict]) -> bool:
    """
    Validate conversation history structure
    
    Args:
        history: List of conversation messages
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(history, list):
        return False
    
    # Check length limit
    if len(history) > 100:  # Reasonable limit
        return False
    
    for message in history:
        if not isinstance(message, dict):
            return False
        
        # Check required fields
        if 'role' not in message or 'content' not in message:
            return False
        
        # Validate role
        if message['role'] not in ['user', 'bot', 'assistant']:
            return False
        
        # Validate content
        if not isinstance(message['content'], str) or len(message['content']) > 5000:
            return False
        
        # Validate timestamp if present
        if 'timestamp' in message:
            if not validate_datetime_string(message['timestamp']):
                return False
    
    return True

def validate_user_input(user_input: Dict) -> Dict[str, Any]:
    """
    Comprehensive validation of user input with detailed results
    
    Args:
        user_input: User input dictionary
        
    Returns:
        Validation result with details
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'sanitized_data': {}
    }
    
    try:
        # Validate message if present
        if 'message' in user_input:
            if not validate_message(user_input['message']):
                result['errors'].append('Invalid message content')
                result['valid'] = False
            else:
                result['sanitized_data']['message'] = user_input['message'].strip()
        
        # Validate history if present
        if 'history' in user_input:
            if not validate_conversation_history(user_input['history']):
                result['errors'].append('Invalid conversation history')
                result['valid'] = False
            else:
                result['sanitized_data']['history'] = user_input['history']
        
        # Validate state if present
        if 'state' in user_input:
            if not validate_chat_state(user_input['state']):
                result['warnings'].append('Invalid or incomplete chat state')
                # Don't mark as invalid, just warn
            else:
                result['sanitized_data']['state'] = user_input['state']
        
        # Validate assessment data if present
        if 'assessment_data' in user_input:
            if not validate_assessment_data(user_input['assessment_data']):
                result['errors'].append('Invalid assessment data')
                result['valid'] = False
            else:
                result['sanitized_data']['assessment_data'] = user_input['assessment_data']
        
        # Validate answers if present
        if 'answers' in user_input and 'assessment_type' in user_input:
            if not validate_answers(user_input['answers'], user_input['assessment_type']):
                result['errors'].append('Invalid assessment answers')
                result['valid'] = False
            else:
                result['sanitized_data']['answers'] = user_input['answers']
                result['sanitized_data']['assessment_type'] = user_input['assessment_type']
    
    except Exception as e:
        logger.error(f"Validation error: {e}")
        result['valid'] = False
        result['errors'].append('Validation process failed')
    
    return result

def sanitize_string(input_string: str, max_length: int = 1000) -> str:
    """
    Sanitize string input
    
    Args:
        input_string: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(input_string, str):
        return ""
    
    # Strip whitespace
    sanitized = input_string.strip()
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Remove potentially dangerous characters (basic XSS protection)
    dangerous_chars = ['<script', '</script', 'javascript:', 'onload=', 'onerror=']
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized

def sanitize_assessment_answers(answers: Dict) -> Dict:
    """
    Sanitize assessment answers
    
    Args:
        answers: Raw answers dictionary
        
    Returns:
        Sanitized answers dictionary
    """
    sanitized = {}
    
    for question_id, answer in answers.items():
        # Sanitize question ID
        clean_id = sanitize_string(str(question_id), 50)
        
        # Sanitize and validate answer
        try:
            clean_answer = int(float(answer))
            # Clamp to reasonable range
            clean_answer = max(0, min(clean_answer, 10))
            sanitized[clean_id] = clean_answer
        except (ValueError, TypeError):
            # Skip invalid answers
            logger.warning(f"Skipping invalid answer for {clean_id}: {answer}")
            continue
    
    return sanitized

def validate_file_upload(file_data: Dict) -> Dict[str, Any]:
    """
    Validate file upload data
    
    Args:
        file_data: File upload data
        
    Returns:
        Validation result
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check required fields
    if 'filename' not in file_data:
        result['errors'].append('Missing filename')
        result['valid'] = False
    
    if 'content' not in file_data:
        result['errors'].append('Missing file content')
        result['valid'] = False
    
    # Validate filename
    if 'filename' in file_data:
        filename = file_data['filename']
        if not isinstance(filename, str) or len(filename) > 255:
            result['errors'].append('Invalid filename')
            result['valid'] = False
        
        # Check for dangerous extensions
        dangerous_extensions = ['.exe', '.bat', '.sh', '.php', '.js']
        if any(filename.lower().endswith(ext) for ext in dangerous_extensions):
            result['errors'].append('Dangerous file type')
            result['valid'] = False
    
    # Validate content size
    if 'content' in file_data:
        content = file_data['content']
        if isinstance(content, str) and len(content) > 10 * 1024 * 1024:  # 10MB limit
            result['errors'].append('File too large')
            result['valid'] = False
    
    return result

# Utility functions for common validations

def is_valid_email(email: str) -> bool:
    """Check if email format is valid"""
    if not isinstance(email, str):
        return False
    return re.match(PATTERNS['email'], email) is not None

def is_valid_phone(phone: str) -> bool:
    """Check if phone number format is valid"""
    if not isinstance(phone, str):
        return False
    return re.match(PATTERNS['phone'], phone) is not None

def is_safe_string(text: str) -> bool:
    """Check if string is safe (no malicious content)"""
    if not isinstance(text, str):
        return False
    
    # Check for common XSS patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    
    return True

def validate_export_request(export_data: Dict) -> Dict[str, Any]:
    """
    Validate export request data
    
    Args:
        export_data: Export request data
        
    Returns:
        Validation result with details
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'sanitized_data': {}
    }
    
    try:
        # Check required fields
        required_fields = ['assessment_data', 'format']
        for field in required_fields:
            if field not in export_data:
                result['errors'].append(f'Missing required field: {field}')
                result['valid'] = False
        
        # Validate export format
        if 'format' in export_data:
            if not validate_export_format(export_data['format']):
                result['errors'].append('Invalid export format')
                result['valid'] = False
            else:
                result['sanitized_data']['format'] = export_data['format'].lower()
        
        # Validate assessment data
        if 'assessment_data' in export_data:
            assessment_data = export_data['assessment_data']
            if not isinstance(assessment_data, dict):
                result['errors'].append('Assessment data must be a dictionary')
                result['valid'] = False
            else:
                # Check for essential fields in assessment data
                essential_fields = ['assessment_type', 'total_score']
                for field in essential_fields:
                    if field not in assessment_data:
                        result['warnings'].append(f'Assessment data missing {field}')
                
                result['sanitized_data']['assessment_data'] = assessment_data
        
        # Validate optional fields
        if 'include_chat_history' in export_data:
            include_chat = export_data['include_chat_history']
            if isinstance(include_chat, bool):
                result['sanitized_data']['include_chat_history'] = include_chat
            else:
                result['warnings'].append('include_chat_history should be boolean')
                result['sanitized_data']['include_chat_history'] = bool(include_chat)
        
        # Validate filename if provided
        if 'filename' in export_data:
            filename = export_data['filename']
            if isinstance(filename, str) and len(filename) <= 255:
                # Sanitize filename
                safe_filename = sanitize_string(filename, 255)
                result['sanitized_data']['filename'] = safe_filename
            else:
                result['warnings'].append('Invalid filename provided')
    
    except Exception as e:
        logger.error(f"Export validation error: {e}")
        result['valid'] = False
        result['errors'].append('Export validation failed')
    
    return result

def normalize_assessment_type(assessment_type: str) -> Optional[str]:
    """
    Normalize assessment type to standard format
    
    Args:
        assessment_type: Assessment type to normalize
        
    Returns:
        Normalized assessment type or None if invalid
    """
    if not isinstance(assessment_type, str):
        return None
    
    # Convert to lowercase and strip
    normalized = assessment_type.lower().strip()
    
    # Handle common variations
    type_mapping = {
        'phq-9': 'phq9',
        'phq_9': 'phq9',
        'gad-7': 'gad7',
        'gad_7': 'gad7',
        'dass-21': 'dass21_stress',
        'dass_21': 'dass21_stress',
        'dass21': 'dass21_stress',
        'suicide': 'suicide_risk',
        'risk': 'suicide_risk',
        'initial': 'initial_screening',
        'screening': 'initial_screening'
    }
    
    if normalized in type_mapping:
        return type_mapping[normalized]
    
    if normalized in VALID_ASSESSMENT_TYPES:
        return normalized
    
    return None