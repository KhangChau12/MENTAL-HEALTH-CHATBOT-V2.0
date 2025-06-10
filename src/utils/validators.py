"""
Validation utilities for mental health chatbot
"""

import re
import logging
from typing import Dict, Any, Optional
from .constants import VALIDATION_PATTERNS, AssessmentTypes, Languages, ExportFormats

logger = logging.getLogger(__name__)

def validate_message(message: str) -> bool:
    """
    Validate user message
    
    Args:
        message: User's message string
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not message or not isinstance(message, str):
        return False
    
    # Check message length
    message = message.strip()
    if len(message) < 1:
        return False
    
    if len(message) > 2000:  # Reasonable limit
        return False
    
    # Check for basic content (not just whitespace/special chars)
    if not re.search(r'[a-zA-ZÀ-ỹ0-9]', message):
        return False
    
    return True

def validate_chat_state(state: Dict[str, Any]) -> bool:
    """
    Validate chat state structure
    
    Args:
        state: Chat state dictionary
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(state, dict):
        return False
    
    # Required fields
    required_fields = ['current_phase']
    for field in required_fields:
        if field not in state:
            return False
    
    # Validate phase
    valid_phases = ['chat', 'assessment', 'results', 'completed']
    if state.get('current_phase') not in valid_phases:
        return False
    
    # Validate session_id format if present
    session_id = state.get('session_id')
    if session_id:
        if not re.match(VALIDATION_PATTERNS['session_id'], session_id):
            logger.warning(f"Invalid session ID format: {session_id}")
            # Don't fail validation for this - just warn
    
    # Validate language if present
    language = state.get('language')
    if language:
        if not re.match(VALIDATION_PATTERNS['language_code'], language):
            return False
    
    # Validate scores structure if present
    scores = state.get('scores')
    if scores and not isinstance(scores, dict):
        return False
    
    return True

def validate_assessment_response(response: str, question_type: str = 'likert_scale') -> bool:
    """
    Validate assessment question response
    
    Args:
        response: User's response
        question_type: Type of question being answered
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not response or not isinstance(response, str):
        return False
    
    response = response.strip().lower()
    
    if question_type == 'likert_scale':
        # Check for numeric response (0-4)
        if re.match(VALIDATION_PATTERNS['assessment_score'], response):
            return True
        
        # Check for valid text responses
        valid_responses = [
            # Vietnamese
            'không bao giờ', 'hiếm khi', 'thỉnh thoảng', 'thường xuyên', 'luôn luôn',
            'không', 'ít', 'vừa', 'nhiều', 'rất nhiều',
            # English
            'never', 'rarely', 'sometimes', 'often', 'always',
            'not at all', 'several days', 'more than half', 'nearly every day'
        ]
        
        if any(valid in response for valid in valid_responses):
            return True
    
    elif question_type == 'binary':
        # Yes/No questions
        binary_responses = ['yes', 'no', 'có', 'không', 'đúng', 'sai', '1', '0']
        if any(resp in response for resp in binary_responses):
            return True
    
    # If it's a reasonable length text response, accept it
    if 1 <= len(response) <= 500:
        return True
    
    return False

def validate_assessment_type(assessment_type: str) -> bool:
    """
    Validate assessment type
    
    Args:
        assessment_type: Assessment type string
        
    Returns:
        bool: True if valid, False otherwise
    """
    valid_types = [
        AssessmentTypes.INITIAL,
        AssessmentTypes.PHQ9,
        AssessmentTypes.GAD7,
        AssessmentTypes.DASS21_STRESS,
        AssessmentTypes.SUICIDE_RISK
    ]
    
    return assessment_type in valid_types

def validate_export_request(assessment_data: Dict, export_format: str) -> bool:
    """
    Validate export request data
    
    Args:
        assessment_data: Assessment data to export
        export_format: Requested export format
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(assessment_data, dict):
        return False
    
    # Validate export format
    if export_format not in [ExportFormats.PDF, ExportFormats.JSON]:
        return False
    
    # Check for required assessment data
    assessment = assessment_data.get('assessment')
    if not assessment or not isinstance(assessment, dict):
        return False
    
    # Check for assessment type
    if not assessment.get('type'):
        return False
    
    # Check for results (for completed assessments)
    results = assessment.get('results')
    if results:
        # If results exist, validate structure
        if not isinstance(results, dict):
            return False
        
        required_result_fields = ['total_score', 'severity']
        for field in required_result_fields:
            if field not in results:
                return False
    
    # Check for responses
    responses = assessment.get('responses')
    if responses and not isinstance(responses, dict):
        return False
    
    return True

def validate_language_code(language: str) -> bool:
    """
    Validate language code
    
    Args:
        language: Language code
        
    Returns:
        bool: True if valid, False otherwise
    """
    return language in [Languages.VIETNAMESE, Languages.ENGLISH]

def validate_score_range(score: int, assessment_type: str) -> bool:
    """
    Validate score within expected range for assessment type
    
    Args:
        score: Score value
        assessment_type: Type of assessment
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(score, int):
        return False
    
    # General range for most assessments (0-4 per question)
    max_scores = {
        AssessmentTypes.PHQ9: 27,  # 9 questions × 3 max score
        AssessmentTypes.GAD7: 21,  # 7 questions × 3 max score
        AssessmentTypes.DASS21_STRESS: 21,  # 7 questions × 3 max score
        AssessmentTypes.SUICIDE_RISK: 12,  # Variable questions
        AssessmentTypes.INITIAL: 20  # Variable questions
    }
    
    max_score = max_scores.get(assessment_type, 40)  # Default fallback
    
    return 0 <= score <= max_score

def validate_session_data(session_data: Dict) -> bool:
    """
    Validate complete session data structure
    
    Args:
        session_data: Complete session data
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(session_data, dict):
        return False
    
    # Check for session ID
    if not session_data.get('session_id'):
        return False
    
    # Validate timestamps if present
    timestamp_fields = ['started_at', 'last_updated']
    for field in timestamp_fields:
        timestamp = session_data.get(field)
        if timestamp:
            try:
                # Basic ISO format check
                if 'T' not in timestamp or 'Z' not in timestamp:
                    if not re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', timestamp):
                        logger.warning(f"Invalid timestamp format: {timestamp}")
            except Exception:
                return False
    
    return True

def sanitize_user_input(user_input: str) -> str:
    """
    Sanitize user input for safety
    
    Args:
        user_input: Raw user input
        
    Returns:
        str: Sanitized input
    """
    if not isinstance(user_input, str):
        return ""
    
    # Remove potentially harmful content
    sanitized = user_input.strip()
    
    # Remove HTML tags
    sanitized = re.sub(r'<[^>]+>', '', sanitized)
    
    # Remove script tags and content
    sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    # Limit length
    if len(sanitized) > 2000:
        sanitized = sanitized[:2000]
    
    return sanitized

def validate_api_request(request_data: Dict, required_fields: list) -> tuple[bool, str]:
    """
    Validate API request data
    
    Args:
        request_data: Request data dictionary
        required_fields: List of required field names
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(request_data, dict):
        return False, "Invalid request format"
    
    # Check required fields
    for field in required_fields:
        if field not in request_data:
            return False, f"Missing required field: {field}"
        
        # Check for empty values
        value = request_data[field]
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"Empty value for required field: {field}"
    
    return True, ""