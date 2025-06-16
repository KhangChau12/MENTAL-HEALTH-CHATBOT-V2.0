"""
Configuration - SỬA ĐỔI để thêm settings cho features mới
Updated config with AI-powered transition logic settings
"""

import os
from typing import Dict, List, Any

# === EXISTING CONFIG (KEEP UNCHANGED) ===

# Together AI Configuration
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY', '148568d44f2a7007651f0d3a035db1981348ccc61be4fb5470613d4599b85aff')
TOGETHER_MODEL = os.getenv('TOGETHER_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free')

# Flask Configuration
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'mental-health-chatbot-secret-key-change-in-production')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')

# Application Settings
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'vi')
SUPPORTED_LANGUAGES = os.getenv('SUPPORTED_LANGUAGES', 'vi,en').split(',')
MAX_CONVERSATION_LENGTH = int(os.getenv('MAX_CONVERSATION_LENGTH', '12'))
TRANSITION_CHECK_INTERVAL = int(os.getenv('TRANSITION_CHECK_INTERVAL', '3'))
MIN_MESSAGES_BEFORE_TRANSITION = int(os.getenv('MIN_MESSAGES_BEFORE_TRANSITION', '6'))

# Export Settings
EXPORT_FORMATS = os.getenv('EXPORT_FORMATS', 'pdf,json').split(',')
PDF_TEMPLATE_PATH = os.getenv('PDF_TEMPLATE_PATH', 'templates/export/')
JSON_EXPORT_INDENT = int(os.getenv('JSON_EXPORT_INDENT', '2'))

# Admin Settings
ADMIN_ENABLED = os.getenv('ADMIN_ENABLED', 'True').lower() == 'true'
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
STATISTICS_RETENTION_DAYS = int(os.getenv('STATISTICS_RETENTION_DAYS', '30'))

# Assessment Configuration
ASSESSMENT_TYPES = {
    'phq9': {
        'name': 'PHQ-9 Depression Scale',
        'questions': 9,
        'max_score': 27,
        'categories': {
            'minimal': (0, 4),
            'mild': (5, 9),
            'moderate': (10, 14),
            'moderately_severe': (15, 19),
            'severe': (20, 27)
        }
    },
    'gad7': {
        'name': 'GAD-7 Anxiety Scale',
        'questions': 7,
        'max_score': 21,
        'categories': {
            'minimal': (0, 4),
            'mild': (5, 9),
            'moderate': (10, 14),
            'severe': (15, 21)
        }
    },
    'dass21_stress': {
        'name': 'DASS-21 Stress Scale',
        'questions': 7,
        'max_score': 21,
        'categories': {
            'normal': (0, 7),
            'mild': (8, 9),
            'moderate': (10, 12),
            'severe': (13, 16),
            'extremely_severe': (17, 21)
        }
    },
    'suicide_risk': {
        'name': 'Suicide Risk Assessment',
        'questions': 5,
        'max_score': 15,
        'categories': {
            'low': (0, 3),
            'moderate': (4, 8),
            'high': (9, 15)
        }
    }
}

# === NEW CONFIG FOR AI-POWERED TRANSITION LOGIC ===

# Simplified Transition Settings
SIMPLIFIED_TRANSITION_THRESHOLDS = {
    'overall_threshold': float(os.getenv('TRANSITION_OVERALL_THRESHOLD', '0.65')),  # Tăng từ 0.4 hiện tại
    'ai_weight': float(os.getenv('TRANSITION_AI_WEIGHT', '0.5')),
    'depth_weight': float(os.getenv('TRANSITION_DEPTH_WEIGHT', '0.3')), 
    'duration_weight': float(os.getenv('TRANSITION_DURATION_WEIGHT', '0.2')),
    'minimum_messages': int(os.getenv('TRANSITION_MIN_MESSAGES', '4'))  # Tối thiểu 4 tin nhắn mới check transition
}

# AI Context Analysis Settings  
AI_ANALYSIS_SETTINGS = {
    'max_tokens': int(os.getenv('AI_ANALYSIS_MAX_TOKENS', '200')),
    'temperature': float(os.getenv('AI_ANALYSIS_TEMPERATURE', '0.3')),  # Thấp để có consistency
    'model': os.getenv('AI_ANALYSIS_MODEL', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'),
    'enable_caching': os.getenv('AI_ANALYSIS_ENABLE_CACHING', 'True').lower() == 'true',
    'cache_duration': int(os.getenv('AI_ANALYSIS_CACHE_DURATION', '300')),  # 5 minutes
    'retry_attempts': int(os.getenv('AI_ANALYSIS_RETRY_ATTEMPTS', '3')),
    'timeout_seconds': int(os.getenv('AI_ANALYSIS_TIMEOUT', '30'))
}

# Conversation Depth Analysis
CONVERSATION_DEPTH_WEIGHTS = {
    'message_length': float(os.getenv('DEPTH_MESSAGE_LENGTH_WEIGHT', '0.3')),
    'personal_sharing': float(os.getenv('DEPTH_PERSONAL_SHARING_WEIGHT', '0.4')),
    'emotional_expression': float(os.getenv('DEPTH_EMOTIONAL_EXPRESSION_WEIGHT', '0.3')),
    'recent_message_boost': float(os.getenv('DEPTH_RECENT_MESSAGE_BOOST', '1.5'))  # Recent messages được weight cao hơn
}

# AI Usage Control
AI_USAGE_CONTROL = {
    'min_messages_before_ai': int(os.getenv('AI_MIN_MESSAGES', '3')),  # Dùng AI sau message thứ 3
    'ai_analysis_interval': int(os.getenv('AI_ANALYSIS_INTERVAL', '2')),  # Mỗi 2 messages
    'max_ai_calls_per_session': int(os.getenv('MAX_AI_CALLS_PER_SESSION', '10')),
    'ai_cooldown_minutes': int(os.getenv('AI_COOLDOWN_MINUTES', '1'))  # 1 phút giữa các AI calls
}

# Response Generation Settings
RESPONSE_GENERATION = {
    'max_response_length': int(os.getenv('MAX_RESPONSE_LENGTH', '200')),
    'response_temperature': float(os.getenv('RESPONSE_TEMPERATURE', '0.7')),
    'include_followup_questions': os.getenv('INCLUDE_FOLLOWUP_QUESTIONS', 'True').lower() == 'true',
    'followup_threshold': float(os.getenv('FOLLOWUP_THRESHOLD', '0.5'))  # Threshold để add followup questions
}

# Logging and Monitoring
MONITORING_SETTINGS = {
    'log_ai_decisions': os.getenv('LOG_AI_DECISIONS', 'True').lower() == 'true',
    'log_transition_decisions': os.getenv('LOG_TRANSITION_DECISIONS', 'True').lower() == 'true',
    'log_conversation_depth': os.getenv('LOG_CONVERSATION_DEPTH', 'True').lower() == 'true',
    'performance_tracking': os.getenv('PERFORMANCE_TRACKING', 'True').lower() == 'true',
    'detailed_error_logging': os.getenv('DETAILED_ERROR_LOGGING', 'True').lower() == 'true'
}

# Safety and Fallback Settings
SAFETY_SETTINGS = {
    'suicide_risk_immediate_threshold': float(os.getenv('SUICIDE_RISK_THRESHOLD', '0.9')),
    'clinical_anxiety_threshold': float(os.getenv('CLINICAL_ANXIETY_THRESHOLD', '0.7')),
    'depression_signs_threshold': float(os.getenv('DEPRESSION_SIGNS_THRESHOLD', '0.7')),
    'enable_safety_overrides': os.getenv('ENABLE_SAFETY_OVERRIDES', 'True').lower() == 'true',
    'fallback_to_old_logic': os.getenv('FALLBACK_TO_OLD_LOGIC', 'True').lower() == 'true'  # Fallback nếu AI fails
}

# Performance Optimization
PERFORMANCE_SETTINGS = {
    'enable_response_caching': os.getenv('ENABLE_RESPONSE_CACHING', 'False').lower() == 'true',
    'cache_similar_responses': os.getenv('CACHE_SIMILAR_RESPONSES', 'False').lower() == 'true',
    'async_ai_analysis': os.getenv('ASYNC_AI_ANALYSIS', 'False').lower() == 'true',
    'batch_ai_requests': os.getenv('BATCH_AI_REQUESTS', 'False').lower() == 'true'
}

# Development and Testing
DEVELOPMENT_SETTINGS = {
    'mock_ai_responses': os.getenv('MOCK_AI_RESPONSES', 'False').lower() == 'true',
    'enable_debug_mode': os.getenv('ENABLE_DEBUG_MODE', 'False').lower() == 'true',
    'log_all_prompts': os.getenv('LOG_ALL_PROMPTS', 'False').lower() == 'true',
    'save_conversation_transcripts': os.getenv('SAVE_CONVERSATION_TRANSCRIPTS', 'False').lower() == 'true'
}

# === HELPER FUNCTIONS ===

def get_assessment_config(assessment_type: str) -> Dict[str, Any]:
    """Get configuration for specific assessment type"""
    return ASSESSMENT_TYPES.get(assessment_type, {})

def get_transition_threshold() -> float:
    """Get current transition threshold"""
    return SIMPLIFIED_TRANSITION_THRESHOLDS['overall_threshold']

def get_ai_model_config() -> Dict[str, Any]:
    """Get AI model configuration"""
    return {
        'model': AI_ANALYSIS_SETTINGS['model'],
        'max_tokens': AI_ANALYSIS_SETTINGS['max_tokens'],
        'temperature': AI_ANALYSIS_SETTINGS['temperature'],
        'timeout': AI_ANALYSIS_SETTINGS['timeout_seconds']
    }

def is_ai_analysis_enabled() -> bool:
    """Check if AI analysis is enabled"""
    return TOGETHER_API_KEY and AI_ANALYSIS_SETTINGS.get('enable_caching', True)

def get_safety_threshold(condition_type: str) -> float:
    """Get safety threshold for specific condition"""
    threshold_map = {
        'suicide_risk': SAFETY_SETTINGS['suicide_risk_immediate_threshold'],
        'clinical_anxiety': SAFETY_SETTINGS['clinical_anxiety_threshold'],
        'depression_signs': SAFETY_SETTINGS['depression_signs_threshold']
    }
    return threshold_map.get(condition_type, 0.7)

def should_use_fallback() -> bool:
    """Check if should use fallback logic"""
    return SAFETY_SETTINGS['fallback_to_old_logic']

# === VALIDATION ===

def validate_config() -> List[str]:
    """Validate configuration and return list of issues"""
    issues = []
    
    # Check required settings
    if not TOGETHER_API_KEY:
        issues.append("TOGETHER_API_KEY is not set")
    
    if not SECRET_KEY or SECRET_KEY == 'mental-health-chatbot-secret-key-change-in-production':
        issues.append("SECRET_KEY should be changed for production")
    
    # Validate thresholds
    if not 0.0 <= SIMPLIFIED_TRANSITION_THRESHOLDS['overall_threshold'] <= 1.0:
        issues.append("overall_threshold must be between 0.0 and 1.0")
    
    # Validate weights sum to 1.0
    weight_sum = (SIMPLIFIED_TRANSITION_THRESHOLDS['ai_weight'] + 
                  SIMPLIFIED_TRANSITION_THRESHOLDS['depth_weight'] + 
                  SIMPLIFIED_TRANSITION_THRESHOLDS['duration_weight'])
    if abs(weight_sum - 1.0) > 0.01:
        issues.append(f"Transition weights must sum to 1.0, current sum: {weight_sum}")
    
    # Validate AI settings
    if AI_ANALYSIS_SETTINGS['temperature'] < 0.0 or AI_ANALYSIS_SETTINGS['temperature'] > 2.0:
        issues.append("AI temperature must be between 0.0 and 2.0")
    
    if AI_ANALYSIS_SETTINGS['max_tokens'] < 50 or AI_ANALYSIS_SETTINGS['max_tokens'] > 1000:
        issues.append("AI max_tokens should be between 50 and 1000")
    
    return issues

# Run validation on import
_config_issues = validate_config()
if _config_issues and FLASK_ENV == 'development':
    print("Configuration Issues:")
    for issue in _config_issues:
        print(f"  - {issue}")

# Export commonly used settings
__all__ = [
    'TOGETHER_API_KEY', 'TOGETHER_MODEL', 'SECRET_KEY',
    'SIMPLIFIED_TRANSITION_THRESHOLDS', 'AI_ANALYSIS_SETTINGS',
    'CONVERSATION_DEPTH_WEIGHTS', 'AI_USAGE_CONTROL',
    'SAFETY_SETTINGS', 'ASSESSMENT_TYPES',
    'get_assessment_config', 'get_transition_threshold',
    'get_ai_model_config', 'is_ai_analysis_enabled',
    'get_safety_threshold', 'should_use_fallback',
    'validate_config'
]