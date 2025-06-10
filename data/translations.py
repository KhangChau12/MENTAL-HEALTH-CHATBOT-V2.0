"""
Multilingual support for Mental Health Chatbot
Translations for Vietnamese and English
"""

translations = {
    "vi": {
        "app_title": "Trợ lý Sức khỏe Tâm thần",
        "app_subtitle": "Hỗ trợ sàng lọc và đánh giá sức khỏe tâm thần",
        
        # Navigation
        "nav_home": "Trang chủ",
        "nav_about": "Giới thiệu", 
        "nav_privacy": "Quyền riêng tư",
        "nav_admin": "Quản trị",
        
        # Mode selection
        "mode_selection_title": "Chọn phương thức đánh giá",
        "mode_ai_title": "Chế độ AI",
        "mode_ai_description": "Trò chuyện tự nhiên với AI, sau đó chuyển sang đánh giá chuyên sâu",
        "mode_logic_title": "Chế độ Logic",
        "mode_logic_description": "Đi thẳng vào bộ câu hỏi đánh giá có cấu trúc",
        
        # Chat interface
        "chat_input_placeholder": "Nhập tin nhắn của bạn...",
        "chat_send": "Gửi",
        "chat_mode_ai": "Chế độ AI",
        "chat_mode_logic": "Chế độ Logic",
        "chat_reset": "Bắt đầu lại",
        
        # Assessment
        "assessment_progress": "Tiến độ",
        "assessment_question": "Câu hỏi",
        "assessment_of": "của",
        "assessment_skip": "Bỏ qua",
        "assessment_previous": "Trước",
        "assessment_next": "Tiếp theo",
        "assessment_submit": "Gửi",
        "assessment_complete": "Hoàn thành",
        
        # Results
        "results_title": "Kết quả đánh giá",
        "results_score": "Điểm số",
        "results_severity": "Mức độ",
        "results_interpretation": "Giải thích",
        "results_recommendations": "Khuyến nghị",
        "results_export": "Xuất kết quả",
        "results_new_assessment": "Đánh giá mới",
        
        # Export
        "export_pdf": "Xuất PDF",
        "export_json": "Xuất JSON", 
        "export_preview": "Xem trước",
        "export_download": "Tải xuống",
        
        # Severity levels
        "severity_minimal": "Tối thiểu",
        "severity_mild": "Nhẹ",
        "severity_moderate": "Trung bình",
        "severity_moderately_severe": "Trung bình nặng",
        "severity_severe": "Nặng",
        "severity_extremely_severe": "Cực kỳ nặng",
        "severity_normal": "Bình thường",
        
        # Risk levels
        "risk_minimal": "Tối thiểu",
        "risk_low": "Thấp", 
        "risk_moderate": "Trung bình",
        "risk_high": "Cao",
        
        # Messages
        "welcome_message": "Xin chào! Tôi là trợ lý sức khỏe tâm thần của bạn. Hãy chia sẻ với tôi cảm giác của bạn.",
        "transition_message": "Cảm ơn bạn đã chia sẻ. Bây giờ tôi muốn đánh giá chi tiết hơn qua một số câu hỏi cụ thể.",
        "completion_message": "Cảm ơn bạn đã hoàn thành đánh giá. Dưới đây là kết quả của bạn.",
        
        # Errors
        "error_general": "Đã xảy ra lỗi. Vui lòng thử lại.",
        "error_connection": "Lỗi kết nối. Vui lòng kiểm tra mạng.",
        "error_invalid_input": "Dữ liệu đầu vào không hợp lệ.",
        "error_assessment_failed": "Không thể hoàn thành đánh giá.",
        
        # Warnings
        "warning_suicide_risk": "Tôi quan tâm đến những gì bạn chia sẻ. Vui lòng tìm kiếm sự giúp đỡ ngay lập tức.",
        "warning_high_risk": "Kết quả cho thấy bạn cần hỗ trợ chuyên nghiệp.",
        
        # Emergency
        "emergency_hotline": "Đường dây nóng khẩn cấp",
        "emergency_number": "1800-0011",
        "emergency_text": "Nếu bạn đang gặp khủng hoảng, hãy gọi ngay:",
        
        # Buttons
        "btn_start": "Bắt đầu",
        "btn_continue": "Tiếp tục", 
        "btn_back": "Quay lại",
        "btn_finish": "Hoàn thành",
        "btn_retry": "Thử lại",
        "btn_help": "Trợ giúp",
        
        # Disclaimer
        "disclaimer_title": "Lưu ý quan trọng",
        "disclaimer_text": "Đây chỉ là công cụ sàng lọc sơ bộ, không phải chẩn đoán y tế. Kết quả chỉ mang tính tham khảo và không thay thế cho tư vấn chuyên nghiệp.",
        
        # Theme
        "theme_light": "Giao diện sáng",
        "theme_dark": "Giao diện tối",
        "theme_toggle": "Chuyển đổi giao diện",
        
        # Admin
        "admin_title": "Bảng điều khiển Quản trị",
        "admin_statistics": "Thống kê",
        "admin_sessions": "Phiên làm việc",
        "admin_assessments": "Đánh giá",
        "admin_exports": "Xuất dữ liệu",
        
        # Time
        "time_minutes": "phút",
        "time_seconds": "giây",
        "time_estimated": "Ước tính",
        "time_remaining": "Còn lại"
    },
    
    "en": {
        "app_title": "Mental Health Assistant",
        "app_subtitle": "Mental health screening and assessment support",
        
        # Navigation
        "nav_home": "Home",
        "nav_about": "About",
        "nav_privacy": "Privacy",
        "nav_admin": "Admin",
        
        # Mode selection
        "mode_selection_title": "Choose Assessment Method",
        "mode_ai_title": "AI Mode",
        "mode_ai_description": "Natural conversation with AI, then transition to detailed assessment",
        "mode_logic_title": "Logic Mode", 
        "mode_logic_description": "Direct structured questionnaire assessment",
        
        # Chat interface
        "chat_input_placeholder": "Type your message...",
        "chat_send": "Send",
        "chat_mode_ai": "AI Mode",
        "chat_mode_logic": "Logic Mode",
        "chat_reset": "Start Over",
        
        # Assessment
        "assessment_progress": "Progress",
        "assessment_question": "Question",
        "assessment_of": "of",
        "assessment_skip": "Skip",
        "assessment_previous": "Previous",
        "assessment_next": "Next",
        "assessment_submit": "Submit",
        "assessment_complete": "Complete",
        
        # Results
        "results_title": "Assessment Results",
        "results_score": "Score",
        "results_severity": "Severity",
        "results_interpretation": "Interpretation",
        "results_recommendations": "Recommendations",
        "results_export": "Export Results",
        "results_new_assessment": "New Assessment",
        
        # Export
        "export_pdf": "Export PDF",
        "export_json": "Export JSON",
        "export_preview": "Preview",
        "export_download": "Download",
        
        # Severity levels
        "severity_minimal": "Minimal",
        "severity_mild": "Mild",
        "severity_moderate": "Moderate", 
        "severity_moderately_severe": "Moderately Severe",
        "severity_severe": "Severe",
        "severity_extremely_severe": "Extremely Severe",
        "severity_normal": "Normal",
        
        # Risk levels
        "risk_minimal": "Minimal",
        "risk_low": "Low",
        "risk_moderate": "Moderate",
        "risk_high": "High",
        
        # Messages
        "welcome_message": "Hello! I'm your mental health assistant. Please share how you're feeling with me.",
        "transition_message": "Thank you for sharing. Now I'd like to assess you more thoroughly with some specific questions.",
        "completion_message": "Thank you for completing the assessment. Here are your results.",
        
        # Errors
        "error_general": "An error occurred. Please try again.",
        "error_connection": "Connection error. Please check your network.",
        "error_invalid_input": "Invalid input data.",
        "error_assessment_failed": "Unable to complete assessment.",
        
        # Warnings
        "warning_suicide_risk": "I'm concerned about what you've shared. Please seek immediate help.",
        "warning_high_risk": "Results indicate you need professional support.",
        
        # Emergency
        "emergency_hotline": "Emergency Hotline",
        "emergency_number": "988",
        "emergency_text": "If you're in crisis, call immediately:",
        
        # Buttons
        "btn_start": "Start",
        "btn_continue": "Continue",
        "btn_back": "Back", 
        "btn_finish": "Finish",
        "btn_retry": "Retry",
        "btn_help": "Help",
        
        # Disclaimer
        "disclaimer_title": "Important Notice",
        "disclaimer_text": "This is a preliminary screening tool, not a medical diagnosis. Results are for reference only and do not replace professional consultation.",
        
        # Theme
        "theme_light": "Light Theme",
        "theme_dark": "Dark Theme", 
        "theme_toggle": "Toggle Theme",
        
        # Admin
        "admin_title": "Admin Dashboard",
        "admin_statistics": "Statistics",
        "admin_sessions": "Sessions",
        "admin_assessments": "Assessments",
        "admin_exports": "Exports",
        
        # Time
        "time_minutes": "minutes",
        "time_seconds": "seconds",
        "time_estimated": "Estimated",
        "time_remaining": "Remaining"
    }
}

# Helper function to get translation
def get_translation(key: str, language: str = 'vi', fallback: str = None) -> str:
    """
    Get translation for a key in specified language
    
    Args:
        key: Translation key
        language: Language code ('vi' or 'en')
        fallback: Fallback text if translation not found
        
    Returns:
        Translated text or fallback or key
    """
    if language not in translations:
        language = 'vi'  # Default to Vietnamese
    
    translation = translations[language].get(key)
    
    if translation:
        return translation
    elif fallback:
        return fallback
    else:
        # Try English as fallback
        if language != 'en':
            return translations['en'].get(key, key)
        return key

# Language-specific formatting
def format_message(template: str, language: str = 'vi', **kwargs) -> str:
    """
    Format message template with language-specific parameters
    
    Args:
        template: Message template
        language: Language code
        **kwargs: Template parameters
        
    Returns:
        Formatted message
    """
    try:
        return template.format(**kwargs)
    except (KeyError, ValueError):
        return template