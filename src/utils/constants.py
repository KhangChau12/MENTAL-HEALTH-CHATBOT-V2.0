"""
Constants and Enums for the Mental Health Chatbot
Vietnamese-only version (cleaned up)
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

# Vietnamese keyword sets for classification
KEYWORD_SETS = {
    'depression_keywords': [
        'buồn', 'chán nản', 'tuyệt vọng', 'vô vọng', 'trầm cảm',
        'mệt mỏi', 'không hứng thú', 'mất động lực', 'cô đơn',
        'tự ti', 'vô dụng', 'không có ý nghĩa', 'không muốn làm gì'
    ],
    'anxiety_keywords': [
        'lo lắng', 'hồi hộp', 'căng thẳng', 'sợ hãi', 'bồn chồn',
        'bất an', 'hoảng loạn', 'run rẩy', 'tim đập nhanh', 'không yên'
    ],
    'stress_keywords': [
        'căng thẳng', 'áp lực', 'quá tải', 'không kiểm soát',
        'choáng ngợp', 'bực bội', 'cáu kỉnh', 'mất kiên nhẫn', 'stress'
    ],
    'suicide_keywords': [
        'tự tử', 'chết', 'kết thúc cuộc đời', 'không muốn sống',
        'tự làm hại', 'muốn biến mất', 'cuộc sống vô nghĩa', 'tự gây thương tích'
    ]
}

# Intensity modifiers for keyword classification
INTENSITY_MODIFIERS = {
    'high_intensity': [
        'rất', 'cực kỳ', 'quá', 'vô cùng', 'luôn luôn', 'liên tục',
        'không thể chịu đựng', 'kinh khủng', 'tệ hại', 'khủng khiếp'
    ],
    'moderate_intensity': [
        'khá', 'thường xuyên', 'nhiều lần', 'đáng kể', 'có phần',
        'tương đối', 'đôi lúc', 'thỉnh thoảng'
    ],
    'low_intensity': [
        'hơi', 'đôi khi', 'thỉnh thoảng', 'ít khi', 'nhẹ',
        'một chút', 'không nhiều'
    ]
}

# Emergency contact information (Vietnam)
EMERGENCY_CONTACTS = {
    'suicide_prevention': '1800-0011',
    'mental_health_hotline': '1900-6048',
    'emergency_services': '113',
    'tâm_lý_hotline': '1800-1060'
}

# Resource URLs (Vietnam)
RESOURCE_URLS = {
    'mental_health_foundation': 'https://tamly.vn',
    'government_health': 'https://moh.gov.vn',
    'crisis_support': 'https://tamlinh.org',
    'vietnam_psychology': 'https://hoisinhhocvietnam.org.vn'
}

# Validation patterns
VALIDATION_PATTERNS = {
    'session_id': r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
    'assessment_score': r'^[0-4]$'
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

# Vietnamese severity level labels
SEVERITY_LABELS = {
    'minimal': 'Tối thiểu',
    'mild': 'Nhẹ',
    'moderate': 'Trung bình',
    'moderately_severe': 'Trung bình nặng',
    'severe': 'Nặng',
    'extremely_severe': 'Cực kỳ nặng',
    'normal': 'Bình thường'
}

# Vietnamese risk level labels
RISK_LABELS = {
    'minimal': 'Tối thiểu',
    'low': 'Thấp',
    'moderate': 'Trung bình',
    'high': 'Cao'
}