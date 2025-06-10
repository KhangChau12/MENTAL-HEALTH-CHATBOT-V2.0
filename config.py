"""
Enhanced configuration for Mental Health Chatbot
Centralized configuration management with validation
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mental-health-chatbot-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'on']
    
    # Together AI Configuration
    TOGETHER_API_KEY = os.environ.get('TOGETHER_API_KEY') or '148568d44f2a7007651f0d3a035db1981348ccc61be4fb5470613d4599b85aff'
    TOGETHER_MODEL = os.environ.get('TOGETHER_MODEL') or 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # AI Parameters
    AI_MAX_TOKENS = int(os.environ.get('AI_MAX_TOKENS', '1000'))
    AI_TEMPERATURE = float(os.environ.get('AI_TEMPERATURE', '0.7'))
    AI_TOP_P = float(os.environ.get('AI_TOP_P', '0.7'))
    AI_TOP_K = int(os.environ.get('AI_TOP_K', '50'))
    AI_REPETITION_PENALTY = float(os.environ.get('AI_REPETITION_PENALTY', '1.0'))
    AI_STOP = ["<|eot_id|>", "<|eom_id|>"]
    
    # Application Settings
    DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE', 'vi')
    SUPPORTED_LANGUAGES = os.environ.get('SUPPORTED_LANGUAGES', 'vi,en').split(',')
    MAX_CONVERSATION_LENGTH = int(os.environ.get('MAX_CONVERSATION_LENGTH', '12'))
    TRANSITION_CHECK_INTERVAL = int(os.environ.get('TRANSITION_CHECK_INTERVAL', '3'))
    MIN_MESSAGES_BEFORE_TRANSITION = int(os.environ.get('MIN_MESSAGES_BEFORE_TRANSITION', '6'))
    
    # Export Settings
    EXPORT_FORMATS = os.environ.get('EXPORT_FORMATS', 'pdf,json').split(',')
    PDF_TEMPLATE_PATH = os.environ.get('PDF_TEMPLATE_PATH', 'templates/export/')
    JSON_EXPORT_INDENT = int(os.environ.get('JSON_EXPORT_INDENT', '2'))
    
    # Admin Settings
    ADMIN_ENABLED = os.environ.get('ADMIN_ENABLED', 'True').lower() in ['true', '1', 'on']
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    STATISTICS_RETENTION_DAYS = int(os.environ.get('STATISTICS_RETENTION_DAYS', '30'))
    
    # Assessment Configuration
    ASSESSMENT_TYPES = ['initial', 'phq9', 'gad7', 'dass21_stress', 'suicide_risk']
    
    # Transition Thresholds (lowered for better UX)
    TRANSITION_THRESHOLDS = {
        'depression': 3,  # Reduced from 6
        'anxiety': 3,     # Reduced from 5
        'stress': 3,      # Reduced from 5
        'suicide_risk': 1  # Immediate transition
    }
    
    # Scoring Ranges
    SCORING_RANGES = {
        'phq9': {
            'minimal': (0, 4),
            'mild': (5, 9),
            'moderate': (10, 14),
            'moderately_severe': (15, 19),
            'severe': (20, 27)
        },
        'gad7': {
            'minimal': (0, 4),
            'mild': (5, 9),
            'moderate': (10, 14),
            'severe': (15, 21)
        },
        'dass21_stress': {
            'normal': (0, 14),
            'mild': (15, 18),
            'moderate': (19, 25),
            'severe': (26, 33),
            'extremely_severe': (34, 42)
        }
    }
    
    @classmethod
    def validate_config(cls):
        """Validate configuration values"""
        errors = []
        
        if not cls.TOGETHER_API_KEY:
            errors.append("TOGETHER_API_KEY is required")
        
        if cls.MAX_CONVERSATION_LENGTH < cls.MIN_MESSAGES_BEFORE_TRANSITION:
            errors.append("MAX_CONVERSATION_LENGTH must be >= MIN_MESSAGES_BEFORE_TRANSITION")
        
        if cls.TRANSITION_CHECK_INTERVAL <= 0:
            errors.append("TRANSITION_CHECK_INTERVAL must be > 0")
        
        if errors:
            raise ValueError("Configuration errors: " + ", ".join(errors))
        
        return True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with more secure defaults for production
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}