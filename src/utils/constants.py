"""
Constants - SỬA ĐỔI để thêm constants cho features mới
Updated constants for AI-powered transition logic
"""

# === EXISTING CONSTANTS (KEEP UNCHANGED) ===

# Assessment Types
ASSESSMENT_TYPES = [
    'phq9',
    'gad7', 
    'dass21_stress',
    'suicide_risk',
    'initial_screening'
]

# Language Support
SUPPORTED_LANGUAGES = {
    'vi': 'Tiếng Việt',
    'en': 'English'
}

# Chat States
CHAT_STATES = [
    'started',
    'in_progress', 
    'assessment_ready',
    'assessment_in_progress',
    'completed'
]

# Response Types
RESPONSE_TYPES = [
    'greeting',
    'chat_response',
    'transition',
    'assessment_question',
    'assessment_result',
    'error'
]

# Export Formats
EXPORT_FORMATS = [
    'pdf',
    'json',
    'txt'
]

# === NEW CONSTANTS FOR AI-POWERED TRANSITION LOGIC ===

# Emotional Context Types từ AI Analysis
EMOTIONAL_CONTEXT_TYPES = [
    'normal_worry',      # Lo lắng bình thường
    'normal_sadness',    # Buồn bình thường  
    'situational_stress', # Stress có nguyên nhân rõ ràng
    'clinical_anxiety',   # Lo âu có dấu hiệu bệnh lý
    'depression_signs',   # Dấu hiệu trầm cảm
    'chronic_stress',     # Stress mãn tính
    'suicide_risk'        # Nguy cơ tự tử
]

# Context Type Descriptions
CONTEXT_TYPE_DESCRIPTIONS = {
    'normal_worry': 'Lo lắng bình thường về các vấn đề cụ thể',
    'normal_sadness': 'Buồn bã do các sự kiện hay tình huống cụ thể',
    'situational_stress': 'Căng thẳng có nguyên nhân rõ ràng và tạm thời',
    'clinical_anxiety': 'Lo âu không có lý do rõ ràng, ảnh hưởng đến cuộc sống',
    'depression_signs': 'Dấu hiệu trầm cảm kéo dài, mất hứng thú',
    'chronic_stress': 'Căng thẳng kéo dài nhiều tuần hoặc tháng',
    'suicide_risk': 'Có ý định hoặc suy nghĩ tự hại bản thân'
}

# Assessment Mapping từ Context Types
CONTEXT_TO_ASSESSMENT_MAPPING = {
    'normal_worry': 'gad7',
    'normal_sadness': 'phq9',
    'situational_stress': 'dass21_stress',
    'clinical_anxiety': 'gad7',
    'depression_signs': 'phq9',
    'chronic_stress': 'dass21_stress',
    'suicide_risk': 'suicide_risk'
}

# Temporal Indicators Mapping
TEMPORAL_INDICATORS = {
    # Ngắn hạn (low severity)
    'hôm qua': 0.1, 'hôm nay': 0.1, 'sáng nay': 0.1, 'chiều nay': 0.1, 'tối nay': 0.1,
    'today': 0.1, 'yesterday': 0.1, 'this morning': 0.1, 'this afternoon': 0.1, 'tonight': 0.1,
    
    # Trung hạn (moderate severity)  
    'tuần này': 0.4, '1 tuần': 0.4, 'mấy ngày': 0.3, 'vài ngày': 0.3, 'tuần trước': 0.4,
    'this week': 0.4, '1 week': 0.4, 'few days': 0.3, 'several days': 0.3, 'last week': 0.4,
    
    # Dài hạn (high severity)
    '2 tuần': 0.8, 'hai tuần': 0.8, 'mấy tuần': 0.7, 'tháng này': 0.7, '1 tháng': 0.8, 'tháng trước': 0.7,
    '2 weeks': 0.8, 'two weeks': 0.8, 'few weeks': 0.7, 'this month': 0.7, '1 month': 0.8, 'last month': 0.7,
    
    # Rất dài hạn (very high severity)
    'mấy tháng': 0.9, 'nhiều tháng': 0.9, 'suốt': 0.9, 'liên tục': 0.9, 'mãi mãi': 0.9,
    'few months': 0.9, 'several months': 0.9, 'constantly': 0.9, 'continuously': 0.9, 'always': 0.9,
    'kể từ': 0.9, 'từ lúc': 0.9, 'since': 0.9, 'ever since': 0.9
}

# Conversation Depth Indicators
DEPTH_INDICATORS = {
    # Personal pronouns (indicate personal sharing)
    'personal_pronouns': [
        'tôi', 'mình', 'em', 'con', 'ta', 'anh', 'chị',
        'i', 'me', 'my', 'myself', 'mine'
    ],
    
    # Emotional expressions (indicate emotional sharing)
    'emotional_expressions': [
        'cảm thấy', 'suy nghĩ', 'lo lắng', 'buồn', 'vui', 'giận', 'sợ', 'hạnh phúc',
        'feel', 'think', 'worry', 'sad', 'happy', 'angry', 'scared', 'afraid',
        'anxious', 'depressed', 'stressed', 'overwhelmed', 'frustrated'
    ],
    
    # Sharing indicators (encourage openness)
    'sharing_indicators': [
        'chia sẻ', 'nói thật', 'thực ra', 'thường', 'luôn luôn', 'thật sự',
        'share', 'honestly', 'actually', 'usually', 'always', 'really',
        'to be honest', 'truthfully', 'in fact'
    ],
    
    # Vulnerability markers (indicate personal struggles)
    'vulnerability_markers': [
        'khó khăn', 'đau khổ', 'không biết', 'bối rối', 'hoang mang', 'tuyệt vọng',
        'difficult', 'struggling', 'confused', 'lost', 'helpless', 'hopeless',
        'overwhelmed', 'stuck', 'desperate', 'alone', 'isolated'
    ]
}

# Severity Level Mapping
SEVERITY_LEVELS = {
    'minimal': {'range': (0.0, 0.3), 'description': 'Mức độ tối thiểu', 'color': 'green'},
    'mild': {'range': (0.3, 0.5), 'description': 'Mức độ nhẹ', 'color': 'yellow'},
    'moderate': {'range': (0.5, 0.7), 'description': 'Mức độ trung bình', 'color': 'orange'},
    'severe': {'range': (0.7, 0.9), 'description': 'Mức độ nghiêm trọng', 'color': 'red'},
    'critical': {'range': (0.9, 1.0), 'description': 'Mức độ cực kỳ nghiêm trọng', 'color': 'darkred'}
}

# AI Analysis Response Templates
AI_ANALYSIS_TEMPLATES = {
    'system_prompt': """Bạn là chuyên gia tâm lý, hãy phân tích tin nhắn để phân biệt giữa cảm xúc bình thường và dấu hiệu bệnh lý.

HƯỚNG DẪN PHÂN LOẠI:
- normal_worry: Lo lắng về việc cụ thể (thi cử, công việc, tương lai)
- normal_sadness: Buồn do sự kiện cụ thể (chia tay, thất bại)
- situational_stress: Stress có nguyên nhân rõ ràng và tạm thời
- clinical_anxiety: Lo âu không có lý do rõ ràng, kéo dài, ảnh hưởng cuộc sống
- depression_signs: Buồn chán kéo dài, mất hứng thú, cảm giác vô vọng
- chronic_stress: Stress kéo dài nhiều tuần/tháng
- suicide_risk: Có ý định tự hại bản thân

SEVERITY SCORE:
- 0.0-0.3: Cảm xúc bình thường, tạm thời
- 0.4-0.6: Cần quan tâm, theo dõi
- 0.7-0.9: Có dấu hiệu bệnh lý, cần đánh giá
- 0.9-1.0: Nguy hiểm, cần can thiệp ngay""",

    'response_format': """{
    "severity": [số từ 0.0 đến 1.0],
    "type": "[một trong các loại đã định nghĩa]",
    "reasoning": "[giải thích ngắn gọn]",
    "confidence": [số từ 0.0 đến 1.0]
}"""
}

# Follow-up Question Templates
FOLLOWUP_TEMPLATES = {
    'normal_worry': [
        "Bạn có thể chia sẻ cụ thể hơn về điều gì đang khiến bạn lo lắng không?",
        "Điều này đã ảnh hưởng đến cuộc sống hàng ngày của bạn như thế nào?",
        "Bạn đã thử cách nào để giải quyết vấn đề này chưa?"
    ],
    'normal_sadness': [
        "Cảm giác buồn này có kéo dài từ lúc nào không?",
        "Bạn có muốn chia sẻ về nguyên nhân khiến bạn cảm thấy buồn?",
        "Bạn có làm được những việc bình thường như trước đây không?"
    ],
    'situational_stress': [
        "Tình huống này đã diễn ra trong bao lâu rồi?",
        "Bạn cảm thấy stress này ảnh hưởng đến giấc ngủ hay ăn uống không?",
        "Có ai bạn có thể tâm sự về vấn đề này không?"
    ],
    'clinical_anxiety': [
        "Cảm giác lo âu này có xuất hiện khi không có lý do rõ ràng không?",
        "Bạn có gặp các triệu chứng như tim đập nhanh, khó thở không?",
        "Điều này có làm bạn tránh né các hoạt động bình thường không?"
    ],
    'depression_signs': [
        "Bạn có mất hứng thú với những việc từng thích làm không?",
        "Giấc ngủ và cảm giác năng lượng của bạn có thay đổi không?",
        "Bạn có cảm thấy tuyệt vọng về tương lai không?"
    ],
    'chronic_stress': [
        "Tình trạng này đã kéo dài bao lâu rồi?",
        "Bạn có thấy khó khăn trong việc thư giãn hay nghỉ ngơi không?",
        "Stress này có ảnh hưởng đến công việc hay học tập không?"
    ],
    'suicide_risk': [
        "Tôi quan tâm đến sự an toàn của bạn. Bạn có suy nghĩ về việc tự hại bản thân không?",
        "Bạn có cần tôi hỗ trợ tìm kiếm sự giúp đỡ chuyên nghiệp không?",
        "Có ai mà bạn tin tưởng có thể nói chuyện ngay bây giờ không?"
    ]
}

# Transition Messages
TRANSITION_MESSAGES = {
    'default': "Cảm ơn bạn đã tin tưởng chia sẻ. Để hiểu rõ hơn tình trạng của bạn, tôi muốn đặt một số câu hỏi cụ thể. Bạn có sẵn sàng không?",
    'high_severity': "Tôi thấy bạn đang trải qua những khó khăn đáng kể. Để hỗ trợ bạn tốt hơn, tôi muốn đặt một số câu hỏi đánh giá. Bạn có đồng ý không?",
    'suicide_risk': "Tôi quan tâm đến sự an toàn của bạn. Để đánh giá tốt hơn tình trạng của bạn, tôi muốn hỏi một số câu hỏi quan trọng. Bạn có sẵn sàng không?",
    'clinical_signs': "Dựa trên những gì bạn chia sẻ, tôi nghĩ việc đánh giá chi tiết hơn sẽ hữu ích. Bạn có thể trả lời một số câu hỏi để tôi hiểu rõ hơn không?"
}

# Error Messages
ERROR_MESSAGES = {
    'ai_analysis_failed': 'Không thể phân tích tin nhắn bằng AI. Sử dụng phương pháp dự phòng.',
    'conversation_analysis_failed': 'Lỗi trong việc phân tích cuộc trò chuyện.',
    'transition_decision_failed': 'Lỗi trong việc quyết định chuyển đổi.',
    'followup_generation_failed': 'Không thể tạo câu hỏi theo dõi.',
    'context_analysis_timeout': 'Phân tích ngữ cảnh bị timeout.',
    'invalid_ai_response': 'Phản hồi từ AI không hợp lệ.',
    'api_rate_limit': 'Đã đạt giới hạn số lượng yêu cầu API.',
    'network_error': 'Lỗi kết nối mạng khi gọi API.',
    'parsing_error': 'Lỗi phân tích dữ liệu phản hồi.'
}

# Success Messages
SUCCESS_MESSAGES = {
    'ai_analysis_completed': 'Phân tích AI hoàn thành thành công',
    'transition_decision_made': 'Quyết định chuyển đổi đã được đưa ra',
    'conversation_analyzed': 'Cuộc trò chuyện đã được phân tích',
    'followup_generated': 'Câu hỏi theo dõi đã được tạo',
    'context_understood': 'Ngữ cảnh đã được hiểu'
}

# Validation Patterns
VALIDATION_PATTERNS = {
    'severity_score': r'^(0(\.[0-9])?|1(\.0)?)$',  # 0.0 to 1.0
    'confidence_score': r'^(0(\.[0-9])?|1(\.0)?)$',  # 0.0 to 1.0
    'context_type': r'^(normal_worry|normal_sadness|situational_stress|clinical_anxiety|depression_signs|chronic_stress|suicide_risk)$',
    'assessment_type': r'^(phq9|gad7|dass21_stress|suicide_risk|initial_screening)$'
}

# Default Values
DEFAULT_VALUES = {
    'ai_severity': 0.0,
    'depth_score': 0.0,
    'duration_score': 0.0,
    'confidence': 0.0,
    'context_type': 'normal_worry',
    'assessment_type': 'phq9',
    'followup_needed': True,
    'transition_threshold': 0.65
}

# Export all constants
__all__ = [
    'ASSESSMENT_TYPES', 'SUPPORTED_LANGUAGES', 'CHAT_STATES', 'RESPONSE_TYPES', 'EXPORT_FORMATS',
    'EMOTIONAL_CONTEXT_TYPES', 'CONTEXT_TYPE_DESCRIPTIONS', 'CONTEXT_TO_ASSESSMENT_MAPPING',
    'TEMPORAL_INDICATORS', 'DEPTH_INDICATORS', 'SEVERITY_LEVELS', 'AI_ANALYSIS_TEMPLATES',
    'FOLLOWUP_TEMPLATES', 'TRANSITION_MESSAGES', 'ERROR_MESSAGES', 'SUCCESS_MESSAGES',
    'VALIDATION_PATTERNS', 'DEFAULT_VALUES'
]