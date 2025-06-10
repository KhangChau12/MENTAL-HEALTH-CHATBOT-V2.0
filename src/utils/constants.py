"""
Constants and Enums for the Mental Health Chatbot
"""

from enum import Enum

class ChatStates:
    """Chat state constants"""
    CHAT = 'chat'
    ASSESSMENT = 'assessment'
    RESULTS = 'results'
    COMPLETED = 'completed'

class AssessmentTypes:
    """Assessment type constants"""
    INITIAL = 'initial'
    PHQ9 = 'phq9'
    GAD7 = 'gad7'
    DASS21_STRESS = 'dass21_stress'
    SUICIDE_RISK = 'suicide_risk'

class QuestionTypes:
    """Question type constants"""
    LIKERT_SCALE = 'likert_scale'
    BINARY = 'binary'
    MULTIPLE_CHOICE = 'multiple_choice'
    OPEN_TEXT = 'open_text'

class SeverityLevels:
    """Severity level constants"""
    MINIMAL = 'minimal'
    MILD = 'mild'
    MODERATE = 'moderate'
    MODERATELY_SEVERE = 'moderately_severe'
    SEVERE = 'severe'
    EXTREMELY_SEVERE = 'extremely_severe'
    NORMAL = 'normal'

class RiskLevels:
    """Risk level constants"""
    MINIMAL = 'minimal'
    LOW = 'low'
    MODERATE = 'moderate'
    HIGH = 'high'

class Languages:
    """Supported language constants"""
    VIETNAMESE = 'vi'
    ENGLISH = 'en'

class ExportFormats:
    """Export format constants"""
    PDF = 'pdf'
    JSON = 'json'

class MessageTypes:
    """Message type constants"""
    WELCOME = 'welcome'
    CONVERSATION = 'conversation'
    TRANSITION = 'transition'
    ASSESSMENT_QUESTION = 'assessment_question'
    ASSESSMENT_COMPLETE = 'assessment_complete'
    RESULTS = 'results'
    ERROR = 'error'
    CLARIFICATION = 'clarification'

# Keyword sets for classification fallback
KEYWORD_SETS = {
    'depression_keywords': {
        'vietnamese': [
            'buồn', 'chán nản', 'tuyệt vọng', 'vô vọng', 'trầm cảm',
            'mệt mỏi', 'không hứng thú', 'mất động lực', 'cô đơn',
            'tự ti', 'vô dụng', 'không có ý nghĩa'
        ],
        'english': [
            'sad', 'depressed', 'hopeless', 'worthless', 'empty',
            'tired', 'fatigue', 'no interest', 'unmotivated', 'lonely',
            'meaningless', 'useless'
        ]
    },
    'anxiety_keywords': {
        'vietnamese': [
            'lo lắng', 'hồi hộp', 'căng thẳng', 'sợ hãi', 'bồn chồn',
            'bất an', 'hoảng loạn', 'run rẩy', 'tim đập nhanh'
        ],
        'english': [
            'anxious', 'worried', 'nervous', 'panic', 'restless',
            'uneasy', 'fearful', 'tense', 'racing heart'
        ]
    },
    'stress_keywords': {
        'vietnamese': [
            'căng thẳng', 'áp lực', 'quá tải', 'không kiểm soát',
            'choáng ngợp', 'bực bội', 'cáu kỉnh', 'mất kiên nhẫn'
        ],
        'english': [
            'stressed', 'pressure', 'overwhelmed', 'out of control',
            'frustrated', 'irritable', 'impatient', 'burned out'
        ]
    },
    'suicide_keywords': {
        'vietnamese': [
            'tự tử', 'chết', 'kết thúc cuộc đời', 'không muốn sống',
            'tự làm hại', 'muốn biến mất', 'cuộc sống vô nghĩa'
        ],
        'english': [
            'suicide', 'kill myself', 'end my life', 'want to die',
            'self harm', 'hurt myself', 'life meaningless', 'better off dead'
        ]
    }
}

# Intensity modifiers for keyword classification
INTENSITY_MODIFIERS = {
    'high_intensity': {
        'vietnamese': [
            'rất', 'cực kỳ', 'quá', 'vô cùng', 'luôn luôn', 'liên tục',
            'không thể chịu đựng', 'kinh khủng', 'tệ hại'
        ],
        'english': [
            'very', 'extremely', 'severely', 'constantly', 'always',
            'unbearable', 'terrible', 'awful', 'horrible'
        ]
    },
    'moderate_intensity': {
        'vietnamese': [
            'khá', 'thường xuyên', 'nhiều lần', 'đáng kể', 'có phần'
        ],
        'english': [
            'quite', 'often', 'frequently', 'significantly', 'somewhat'
        ]
    },
    'low_intensity': {
        'vietnamese': [
            'hơi', 'đôi khi', 'thỉnh thoảng', 'ít khi', 'nhẹ'
        ],
        'english': [
            'slightly', 'sometimes', 'occasionally', 'rarely', 'mildly'
        ]
    }
}

# Emergency contact information
EMERGENCY_CONTACTS = {
    'vietnam': {
        'suicide_prevention': '1800-0011',
        'mental_health_hotline': '1900-6048',
        'emergency_services': '113'
    },
    'international': {
        'suicide_prevention': '988',  # US
        'crisis_text_line': 'Text HOME to 741741'
    }
}

# Resource URLs
RESOURCE_URLS = {
    'vietnam': {
        'mental_health_foundation': 'https://tâmlý.vn',
        'government_health': 'https://moh.gov.vn',
        'crisis_support': 'https://tamlinh.org'
    },
    'international': {
        'who_mental_health': 'https://www.who.int/mental_disorders',
        'nami': 'https://www.nami.org',
        'mental_health_america': 'https://www.mhanational.org'
    }
}

# Validation patterns
VALIDATION_PATTERNS = {
    'session_id': r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
    'assessment_score': r'^[0-4]$',
    'language_code': r'^(vi|en)$'
}

# Default configuration values
DEFAULT_CONFIG = {
    'max_conversation_length': 12,
    'min_messages_before_transition': 6,
    'transition_check_interval': 3,
    'ai_max_tokens': 1000,
    'ai_temperature': 0.7,
    'session_timeout_minutes': 30
}

# Assessment question limits
ASSESSMENT_LIMITS = {
    'phq9': {'min_questions': 9, 'max_questions': 9},
    'gad7': {'min_questions': 7, 'max_questions': 7},
    'dass21_stress': {'min_questions': 7, 'max_questions': 7},
    'suicide_risk': {'min_questions': 3, 'max_questions': 5},
    'initial': {'min_questions': 5, 'max_questions': 10}
}