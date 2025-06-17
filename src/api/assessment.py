"""
Assessment API - FIXED VERSION với các lỗi đã được khắc phục
Enhanced version compatible with existing project structure
"""

import logging
import json
from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from typing import Dict, List, Optional, Any

# FIXED IMPORTS - Chỉ import những gì có sẵn
try:
    from src.services.export_service import ExportService
    export_service = ExportService()
    EXPORT_AVAILABLE = True
except ImportError:
    export_service = None
    EXPORT_AVAILABLE = False

# Import validators với error handling
try:
    from src.utils.validators import validate_answers, VALID_ASSESSMENT_TYPES
except ImportError:
    VALID_ASSESSMENT_TYPES = ['phq9', 'gad7', 'dass21_stress', 'suicide_risk', 'initial_screening']
    
    def validate_answers(answers: Dict, assessment_type: str) -> bool:
        """Fallback validation function"""
        if not isinstance(answers, dict):
            return False
        return len(answers) > 0

logger = logging.getLogger(__name__)

# Create blueprint với tên unique để tránh conflicts
assessment_bp = Blueprint('assessment_api', __name__)

# FIXED: Remove AssessmentTypes class dependency - sử dụng constants trực tiếp
ASSESSMENT_TYPES_LIST = ['phq9', 'gad7', 'dass21_stress', 'suicide_risk', 'initial_screening']

# Standard questionnaires data - FIXED: Self-contained data
STANDARD_QUESTIONNAIRES = {
    'phq9': {
        'title': 'PHQ-9 - Đánh giá Trầm cảm',
        'description': 'Bộ câu hỏi sàng lọc trầm cảm chuẩn quốc tế theo DSM-5',
        'instructions': 'Trong 2 tuần qua, bạn có thường xuyên gặp phải các vấn đề sau không?',
        'question_count': 9,
        'estimated_time': '3-5 phút',
        'category': 'depression',
        'scoring': {
            'max_score': 27,
            'ranges': {
                'minimal': {'min': 0, 'max': 4, 'description': 'Không có hoặc rất ít triệu chứng trầm cảm'},
                'mild': {'min': 5, 'max': 9, 'description': 'Triệu chứng trầm cảm nhẹ'},
                'moderate': {'min': 10, 'max': 14, 'description': 'Triệu chứng trầm cảm vừa phải'},
                'moderately_severe': {'min': 15, 'max': 19, 'description': 'Triệu chứng trầm cảm khá nặng'},
                'severe': {'min': 20, 'max': 27, 'description': 'Triệu chứng trầm cảm nặng'}
            }
        },
        'questions': [
            {
                'id': 'phq9_1',
                'text': 'Ít có hứng thú hoặc không cảm thấy vui vẻ khi làm việc gì',
                'category': 'interest',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'phq9_2',
                'text': 'Cảm thấy buồn, chán nản hoặc tuyệt vọng',
                'category': 'mood',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'phq9_3',
                'text': 'Khó ngủ, ngủ không sâu giấc hoặc ngủ quá nhiều',
                'category': 'sleep',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'phq9_4',
                'text': 'Cảm thấy mệt mỏi hoặc ít năng lượng',
                'category': 'energy',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'phq9_5',
                'text': 'Ăn kém hoặc ăn quá nhiều',
                'category': 'appetite',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'phq9_6',
                'text': 'Cảm thấy tệ về bản thân - hoặc cảm thấy mình là kẻ thất bại hoặc đã làm gia đình thất vọng',
                'category': 'self_worth',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'phq9_7',
                'text': 'Khó tập trung vào việc gì đó, chẳng hạn như đọc báo hoặc xem tivi',
                'category': 'concentration',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'phq9_8',
                'text': 'Di chuyển hoặc nói chuyện chậm chạp đến mức người khác có thể nhận ra? Hoặc ngược lại - bồn chồn hoặc bất an hơn bình thường',
                'category': 'psychomotor',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'phq9_9',
                'text': 'Có ý nghĩ rằng tốt hơn là chết đi hoặc tự làm hại bản thân theo cách nào đó',
                'category': 'suicide_risk',
                'warning': 'high_risk',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            }
        ]
    },
    
    'gad7': {
        'title': 'GAD-7 - Đánh giá Lo âu',
        'description': 'Bộ câu hỏi sàng lọc rối loạn lo âu tổng quát chuẩn quốc tế',
        'instructions': 'Trong 2 tuần qua, bạn có thường xuyên gặp phải các vấn đề sau không?',
        'question_count': 7,
        'estimated_time': '2-4 phút',
        'category': 'anxiety',
        'scoring': {
            'max_score': 21,
            'ranges': {
                'minimal': {'min': 0, 'max': 4, 'description': 'Không có hoặc rất ít triệu chứng lo âu'},
                'mild': {'min': 5, 'max': 9, 'description': 'Triệu chứng lo âu nhẹ'},
                'moderate': {'min': 10, 'max': 14, 'description': 'Triệu chứng lo âu vừa phải'},
                'severe': {'min': 15, 'max': 21, 'description': 'Triệu chứng lo âu nặng'}
            }
        },
        'questions': [
            {
                'id': 'gad7_1',
                'text': 'Cảm thấy lo lắng, bồn chồn hoặc căng thẳng',
                'category': 'nervousness',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'gad7_2',
                'text': 'Không thể ngăn chặn hoặc kiểm soát sự lo lắng',
                'category': 'control',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'gad7_3',
                'text': 'Lo lắng quá mức về những điều khác nhau',
                'category': 'excessive_worry',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'gad7_4',
                'text': 'Khó thư giãn',
                'category': 'relaxation',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'gad7_5',
                'text': 'Bồn chồn đến mức khó ngồi yên',
                'category': 'restlessness',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'gad7_6',
                'text': 'Dễ bực bội hoặc cáu kỉnh',
                'category': 'irritability',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            },
            {
                'id': 'gad7_7',
                'text': 'Cảm thấy sợ hãi như thể điều gì đó tệ hại sắp xảy ra',
                'category': 'fear',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Vài ngày'},
                    {'value': 2, 'text': 'Hơn một nửa số ngày'},
                    {'value': 3, 'text': 'Gần như mỗi ngày'}
                ]
            }
        ]
    },
    
    'dass21_stress': {
        'title': 'DASS-21 - Đánh giá Căng thẳng',
        'description': 'Phần căng thẳng của bộ câu hỏi Depression, Anxiety and Stress Scale-21',
        'instructions': 'Vui lòng đọc từng câu và chọn số phù hợp để cho biết mức độ áp dụng cho bạn trong tuần qua.',
        'question_count': 7,
        'estimated_time': '3-5 phút',
        'category': 'stress',
        'scoring': {
            'max_score': 21,
            'ranges': {
                'normal': {'min': 0, 'max': 7, 'description': 'Mức căng thẳng bình thường'},
                'mild': {'min': 8, 'max': 9, 'description': 'Căng thẳng nhẹ'},
                'moderate': {'min': 10, 'max': 12, 'description': 'Căng thẳng vừa phải'},
                'severe': {'min': 13, 'max': 16, 'description': 'Căng thẳng nặng'},
                'extremely_severe': {'min': 17, 'max': 21, 'description': 'Căng thẳng rất nặng'}
            }
        },
        'questions': [
            {
                'id': 'dass21_stress_1',
                'text': 'Tôi thấy khó để bình tĩnh lại sau khi có điều gì đó làm tôi buồn phiền',
                'category': 'difficulty_relaxing',
                'options': [
                    {'value': 0, 'text': 'Không áp dụng với tôi chút nào'},
                    {'value': 1, 'text': 'Áp dụng với tôi ở mức độ nào đó, hoặc thỉnh thoảng'},
                    {'value': 2, 'text': 'Áp dụng với tôi ở mức độ đáng kể, hoặc khá thường xuyên'},
                    {'value': 3, 'text': 'Áp dụng với tôi rất nhiều, hoặc hầu hết thời gian'}
                ]
            },
            {
                'id': 'dass21_stress_2',
                'text': 'Tôi có khuynh hướng phản ứng thái quá với các tình huống',
                'category': 'overreaction',
                'options': [
                    {'value': 0, 'text': 'Không áp dụng với tôi chút nào'},
                    {'value': 1, 'text': 'Áp dụng với tôi ở mức độ nào đó, hoặc thỉnh thoảng'},
                    {'value': 2, 'text': 'Áp dụng với tôi ở mức độ đáng kể, hoặc khá thường xuyên'},
                    {'value': 3, 'text': 'Áp dụng với tôi rất nhiều, hoặc hầu hết thời gian'}
                ]
            },
            {
                'id': 'dass21_stress_3',
                'text': 'Tôi thấy mình dễ bị kích động',
                'category': 'irritability',
                'options': [
                    {'value': 0, 'text': 'Không áp dụng với tôi chút nào'},
                    {'value': 1, 'text': 'Áp dụng với tôi ở mức độ nào đó, hoặc thỉnh thoảng'},
                    {'value': 2, 'text': 'Áp dụng với tôi ở mức độ đáng kể, hoặc khá thường xuyên'},
                    {'value': 3, 'text': 'Áp dụng với tôi rất nhiều, hoặc hầu hết thời gian'}
                ]
            },
            {
                'id': 'dass21_stress_4',
                'text': 'Tôi thấy khó chịu khi bị cản trở làm việc mình muốn làm',
                'category': 'impatience',
                'options': [
                    {'value': 0, 'text': 'Không áp dụng với tôi chút nào'},
                    {'value': 1, 'text': 'Áp dụng với tôi ở mức độ nào đó, hoặc thỉnh thoảng'},
                    {'value': 2, 'text': 'Áp dụng với tôi ở mức độ đáng kể, hoặc khá thường xuyên'},
                    {'value': 3, 'text': 'Áp dụng với tôi rất nhiều, hoặc hầu hết thời gian'}
                ]
            },
            {
                'id': 'dass21_stress_5',
                'text': 'Tôi thấy mình đang căng thẳng',
                'category': 'tension',
                'options': [
                    {'value': 0, 'text': 'Không áp dụng với tôi chút nào'},
                    {'value': 1, 'text': 'Áp dụng với tôi ở mức độ nào đó, hoặc thỉnh thoảng'},
                    {'value': 2, 'text': 'Áp dụng với tôi ở mức độ đáng kể, hoặc khá thường xuyên'},
                    {'value': 3, 'text': 'Áp dụng với tôi rất nhiều, hoặc hầu hết thời gian'}
                ]
            },
            {
                'id': 'dass21_stress_6',
                'text': 'Tôi không thể chịu đựng được những việc cản trở tôi tiếp tục làm những gì tôi đang làm',
                'category': 'intolerance',
                'options': [
                    {'value': 0, 'text': 'Không áp dụng với tôi chút nào'},
                    {'value': 1, 'text': 'Áp dụng với tôi ở mức độ nào đó, hoặc thỉnh thoảng'},
                    {'value': 2, 'text': 'Áp dụng với tôi ở mức độ đáng kể, hoặc khá thường xuyên'},
                    {'value': 3, 'text': 'Áp dụng với tôi rất nhiều, hoặc hầu hết thời gian'}
                ]
            },
            {
                'id': 'dass21_stress_7',
                'text': 'Tôi thấy mình nóng nảy',
                'category': 'agitation',
                'options': [
                    {'value': 0, 'text': 'Không áp dụng với tôi chút nào'},
                    {'value': 1, 'text': 'Áp dụng với tôi ở mức độ nào đó, hoặc thỉnh thoảng'},
                    {'value': 2, 'text': 'Áp dụng với tôi ở mức độ đáng kể, hoặc khá thường xuyên'},
                    {'value': 3, 'text': 'Áp dụng với tôi rất nhiều, hoặc hầu hết thời gian'}
                ]
            }
        ]
    },
    
    'suicide_risk': {
        'title': 'Đánh giá Nguy cơ Tự tử',
        'description': 'Đánh giá sơ bộ các yếu tố nguy cơ tự tử',
        'instructions': 'Những câu hỏi sau giúp đánh giá sơ bộ nguy cơ. Vui lòng trả lời thật lòng.',
        'question_count': 5,
        'estimated_time': '2-3 phút',
        'category': 'risk',
        'warning': 'Đây là đánh giá sơ bộ. Nếu có nguy cơ cao, hãy liên hệ ngay với chuyên gia.',
        'scoring': {
            'max_score': 15,
            'ranges': {
                'low': {'min': 0, 'max': 3, 'description': 'Nguy cơ thấp'},
                'moderate': {'min': 4, 'max': 8, 'description': 'Nguy cơ vừa phải - cần theo dõi'},
                'high': {'min': 9, 'max': 15, 'description': 'Nguy cơ cao - cần can thiệp ngay'}
            }
        },
        'questions': [
            {
                'id': 'suicide_1',
                'text': 'Bạn có cảm thấy cuộc sống không đáng sống không?',
                'category': 'hopelessness',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Hiếm khi'},
                    {'value': 2, 'text': 'Thỉnh thoảng'},
                    {'value': 3, 'text': 'Thường xuyên'}
                ]
            },
            {
                'id': 'suicide_2',
                'text': 'Bạn có nghĩ rằng gia đình/bạn bè sẽ tốt hơn nếu không có bạn?',
                'category': 'burden',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Hiếm khi'},
                    {'value': 2, 'text': 'Thỉnh thoảng'},
                    {'value': 3, 'text': 'Thường xuyên'}
                ]
            },
            {
                'id': 'suicide_3',
                'text': 'Bạn có ý nghĩ về việc tự làm hại bản thân?',
                'category': 'self_harm',
                'warning': 'high_risk',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Hiếm khi'},
                    {'value': 2, 'text': 'Thỉnh thoảng'},
                    {'value': 3, 'text': 'Thường xuyên'}
                ]
            },
            {
                'id': 'suicide_4',
                'text': 'Bạn có lên kế hoạch cụ thể để tự làm hại bản thân?',
                'category': 'planning',
                'warning': 'high_risk',
                'options': [
                    {'value': 0, 'text': 'Không có'},
                    {'value': 1, 'text': 'Nghĩ đơn giản'},
                    {'value': 2, 'text': 'Có ý tưởng mơ hồ'},
                    {'value': 3, 'text': 'Có kế hoạch cụ thể'}
                ]
            },
            {
                'id': 'suicide_5',
                'text': 'Bạn có từng cố gắng tự làm hại bản thân trước đây?',
                'category': 'history',
                'warning': 'high_risk',
                'options': [
                    {'value': 0, 'text': 'Không bao giờ'},
                    {'value': 1, 'text': 'Đã nghĩ đến'},
                    {'value': 2, 'text': 'Đã cố gắng nhưng không nghiêm trọng'},
                    {'value': 3, 'text': 'Đã có hành động nghiêm trọng'}
                ]
            }
        ]
    }
}

# API Routes - FIXED: Chỉ API routes, không có page routes

@assessment_bp.route('/types', methods=['GET'])
def get_assessment_types():
    """Get available assessment types for API calls"""
    try:
        assessment_types = {}
        for key, data in STANDARD_QUESTIONNAIRES.items():
            assessment_types[key] = {
                'name': key.upper(),
                'title': data['title'],
                'description': data['description'],
                'question_count': data['question_count'],
                'estimated_time': data['estimated_time'],
                'category': data['category']
            }
        
        return jsonify({
            'success': True,
            'assessment_types': assessment_types,
            'total_types': len(assessment_types)
        })
        
    except Exception as e:
        logger.error(f"Error getting assessment types: {e}")
        return jsonify({
            'error': 'Failed to get assessment types',
            'message': 'Không thể lấy danh sách loại đánh giá'
        }), 500

@assessment_bp.route('/start', methods=['POST'])
def start_assessment():
    """
    Start a new assessment - supports both poll and chat modes
    
    Expected JSON:
    {
        "assessment_type": "phq9",
        "session_id": "uuid",
        "language": "vi",
        "mode": "poll"  // "poll" or "chat"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Vui lòng cung cấp thông tin đánh giá'
            }), 400
        
        assessment_type = data.get('assessment_type')
        session_id = data.get('session_id')
        language = data.get('language', 'vi')
        mode = data.get('mode', 'poll')  # Default to poll mode
        
        # FIXED: Use internal assessment types list instead of missing class
        if not assessment_type or assessment_type not in ASSESSMENT_TYPES_LIST:
            return jsonify({
                'error': 'Invalid assessment type',
                'message': 'Loại đánh giá không hợp lệ',
                'available_types': ASSESSMENT_TYPES_LIST
            }), 400
        
        # FIXED: Simple session ID validation
        if not session_id or not _validate_session_id(session_id):
            return jsonify({
                'error': 'Invalid session ID',
                'message': 'Mã phiên làm việc không hợp lệ'
            }), 400
        
        # Get questionnaire data
        questionnaire = STANDARD_QUESTIONNAIRES[assessment_type]
        
        # Prepare response based on mode
        if mode == 'poll':
            # Poll mode - return all questions for frontend handling
            response_data = {
                'success': True,
                'assessment_type': assessment_type,
                'session_id': session_id,
                'mode': 'poll',
                'questionnaire': {
                    'title': questionnaire['title'],
                    'description': questionnaire['description'],
                    'instructions': questionnaire['instructions'],
                    'question_count': questionnaire['question_count'],
                    'estimated_time': questionnaire['estimated_time'],
                    'questions': questionnaire['questions'],
                    'scoring': questionnaire['scoring']
                },
                'started_at': datetime.now().isoformat()
            }
        else:
            # Chat mode - return first question only
            first_question = questionnaire['questions'][0]
            response_data = {
                'success': True,
                'assessment_type': assessment_type,
                'session_id': session_id,
                'mode': 'chat',
                'current_question': {
                    'index': 0,
                    'total': questionnaire['question_count'],
                    'question': first_question,
                    'instructions': questionnaire['instructions']
                },
                'started_at': datetime.now().isoformat()
            }
        
        _log_assessment_activity(assessment_type, session_id, 'start', mode=mode)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error starting assessment: {e}")
        return jsonify({
            'error': 'Failed to start assessment',
            'message': 'Không thể bắt đầu đánh giá'
        }), 500

@assessment_bp.route('/question/<assessment_type>/<int:question_index>', methods=['GET'])
def get_question(assessment_type, question_index):
    """Get specific question for chat mode"""
    try:
        # Validate assessment type
        if assessment_type not in STANDARD_QUESTIONNAIRES:
            return jsonify({
                'error': 'Invalid assessment type',
                'message': 'Loại đánh giá không hợp lệ'
            }), 400
        
        questionnaire = STANDARD_QUESTIONNAIRES[assessment_type]
        
        # Validate question index
        if question_index < 0 or question_index >= len(questionnaire['questions']):
            return jsonify({
                'error': 'Invalid question index',
                'message': 'Chỉ số câu hỏi không hợp lệ'
            }), 400
        
        question = questionnaire['questions'][question_index]
        
        return jsonify({
            'success': True,
            'question': question,
            'index': question_index,
            'total': len(questionnaire['questions']),
            'progress': round((question_index / len(questionnaire['questions'])) * 100, 1)
        })
        
    except Exception as e:
        logger.error(f"Error getting question: {e}")
        return jsonify({
            'error': 'Failed to get question',
            'message': 'Không thể lấy câu hỏi'
        }), 500

@assessment_bp.route('/submit', methods=['POST'])
def submit_assessment():
    """
    Submit assessment answers and get results
    
    Expected JSON:
    {
        "assessment_type": "phq9",
        "session_id": "uuid", 
        "answers": {"phq9_1": 2, "phq9_2": 1, ...},
        "chat_history": [...],
        "completed_at": "2024-01-01T12:00:00"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Vui lòng cung cấp dữ liệu đánh giá'
            }), 400
        
        # Extract and validate data
        assessment_type = data.get('assessment_type')
        session_id = data.get('session_id')
        answers = data.get('answers', {})
        chat_history = data.get('chat_history', [])
        completed_at = data.get('completed_at', datetime.now().isoformat())
        
        # Validate required fields
        if not session_id or not _validate_session_id(session_id):
            return jsonify({
                'error': 'Invalid session ID',
                'message': 'Mã phiên làm việc không hợp lệ'
            }), 400
        
        if not assessment_type or assessment_type not in STANDARD_QUESTIONNAIRES:
            return jsonify({
                'error': 'Invalid assessment type',
                'message': 'Loại đánh giá không hợp lệ'
            }), 400
        
        if not answers:
            return jsonify({
                'error': 'No answers provided',
                'message': 'Không có câu trả lời được cung cấp'
            }), 400
        
        # FIXED: Validate answers format using fallback function
        if not validate_answers(answers, assessment_type):
            return jsonify({
                'error': 'Invalid answers format',
                'message': 'Định dạng câu trả lời không hợp lệ'
            }), 400
        
        # Get questionnaire for scoring
        questionnaire = STANDARD_QUESTIONNAIRES[assessment_type]
        
        # Calculate results
        results = _calculate_assessment_results(assessment_type, answers, questionnaire)
        
        # Generate recommendations
        recommendations = _generate_recommendations(assessment_type, results, answers)
        
        # Prepare complete results
        assessment_results = {
            'success': True,
            'assessment_type': assessment_type,
            'session_id': session_id,
            'completed_at': completed_at,
            'questionnaire_info': {
                'title': questionnaire['title'],
                'description': questionnaire['description']
            },
            'results': results,
            'recommendations': recommendations,
            'answers': answers,
            'chat_history': chat_history,
            'next_actions': _get_next_actions(results['severity'])
        }
        
        _log_assessment_activity(assessment_type, session_id, 'complete', 
                                score=results['total_score'], 
                                severity=results['severity'])
        
        return jsonify(assessment_results)
        
    except Exception as e:
        logger.error(f"Error submitting assessment: {e}")
        return jsonify({
            'error': 'Assessment processing failed',
            'message': 'Không thể xử lý kết quả đánh giá'
        }), 500

@assessment_bp.route('/results/<session_id>', methods=['GET'])
def get_results(session_id):
    """Get assessment results by session ID"""
    try:
        # Validate session ID
        if not _validate_session_id(session_id):
            return jsonify({
                'error': 'Invalid session ID',
                'message': 'Mã phiên làm việc không hợp lệ'
            }), 400
        
        # In a real implementation, you would fetch from database
        # For now, return a placeholder response
        return jsonify({
            'error': 'Results not found',
            'message': 'Không tìm thấy kết quả cho phiên này',
            'note': 'Chức năng lưu trữ kết quả sẽ được triển khai trong phiên bản tiếp theo'
        }), 404
        
    except Exception as e:
        logger.error(f"Error getting results: {e}")
        return jsonify({
            'error': 'Failed to get results',
            'message': 'Không thể lấy kết quả'
        }), 500

@assessment_bp.route('/statistics', methods=['GET'])
def get_assessment_statistics():
    """Get assessment usage statistics"""
    try:
        # Mock statistics - in real implementation, fetch from database
        stats = {
            'total_assessments': 1250,
            'assessments_today': 45,
            'assessments_this_week': 312,
            'assessment_types': {
                'phq9': {'count': 580, 'percentage': 46.4},
                'gad7': {'count': 420, 'percentage': 33.6},
                'dass21_stress': {'count': 180, 'percentage': 14.4},
                'suicide_risk': {'count': 70, 'percentage': 5.6}
            },
            'average_completion_time': '4.2 phút',
            'completion_rate': 87.3,
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({
            'error': 'Failed to get statistics',
            'message': 'Không thể lấy thống kê'
        }), 500

@assessment_bp.route('/export', methods=['POST'])
def export_results():
    """Export assessment results - FIXED: Only if export service available"""
    try:
        if not EXPORT_AVAILABLE:
            return jsonify({
                'error': 'Export service unavailable',
                'message': 'Chức năng xuất file chưa sẵn sàng'
            }), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Vui lòng cung cấp dữ liệu để xuất'
            }), 400
        
        # Redirect to export service if available
        from flask import redirect, url_for
        return redirect(url_for('export.export_pdf'), code=307)
        
    except Exception as e:
        logger.error(f"Error exporting results: {e}")
        return jsonify({
            'error': 'Export failed',
            'message': 'Không thể xuất kết quả'
        }), 500

# Helper functions - FIXED: Self-contained implementations

def _calculate_assessment_results(assessment_type: str, answers: Dict, questionnaire: Dict) -> Dict:
    """Calculate assessment results and scoring"""
    try:
        # Calculate total score
        total_score = sum(int(answers.get(q['id'], 0)) for q in questionnaire['questions'])
        max_score = questionnaire['scoring']['max_score']
        
        # Determine severity level
        severity = 'minimal'
        severity_description = ''
        
        for level, range_info in questionnaire['scoring']['ranges'].items():
            if range_info['min'] <= total_score <= range_info['max']:
                severity = level
                severity_description = range_info['description']
                break
        
        # Calculate percentage
        percentage = round((total_score / max_score) * 100, 1)
        
        # Check for high-risk indicators
        risk_indicators = []
        for question in questionnaire['questions']:
            if question.get('warning') == 'high_risk':
                answer_value = answers.get(question['id'], 0)
                if answer_value >= 2:  # High score on risk question
                    risk_indicators.append({
                        'question_id': question['id'],
                        'question_text': question['text'],
                        'answer_value': answer_value,
                        'risk_level': 'high' if answer_value >= 3 else 'moderate'
                    })
        
        return {
            'total_score': total_score,
            'max_score': max_score,
            'percentage': percentage,
            'severity': severity,
            'severity_description': severity_description,
            'risk_indicators': risk_indicators,
            'answered_questions': len(answers),
            'total_questions': len(questionnaire['questions']),
            'completion_rate': round((len(answers) / len(questionnaire['questions'])) * 100, 1)
        }
        
    except Exception as e:
        logger.error(f"Error calculating results: {e}")
        return {
            'total_score': 0,
            'max_score': questionnaire['scoring']['max_score'],
            'percentage': 0,
            'severity': 'error',
            'severity_description': 'Không thể tính toán kết quả',
            'risk_indicators': [],
            'answered_questions': 0,
            'total_questions': len(questionnaire['questions']),
            'completion_rate': 0
        }

def _generate_recommendations(assessment_type: str, results: Dict, answers: Dict) -> List[Dict]:
    """Generate personalized recommendations based on results"""
    recommendations = []
    severity = results['severity']
    total_score = results['total_score']
    
    # Base recommendations by severity
    if severity in ['minimal', 'normal']:
        recommendations.extend([
            {
                'type': 'lifestyle',
                'priority': 'low',
                'title': 'Duy trì sức khỏe tâm thần tốt',
                'description': 'Tiếp tục duy trì lối sống lành mạnh và các hoạt động tích cực.',
                'actions': [
                    'Tập thể dục đều đặn',
                    'Duy trì mối quan hệ xã hội tích cực',
                    'Thực hành mindfulness hoặc thiền định',
                    'Đảm bảo giấc ngủ đủ và chất lượng'
                ]
            }
        ])
    
    elif severity == 'mild':
        recommendations.extend([
            {
                'type': 'self_care',
                'priority': 'medium',
                'title': 'Tăng cường chăm sóc bản thân',
                'description': 'Áp dụng các kỹ thuật tự chăm sóc để cải thiện tình trạng.',
                'actions': [
                    'Lập kế hoạch sinh hoạt hàng ngày',
                    'Thực hành các kỹ thuật thư giãn',
                    'Tìm kiếm hoạt động yêu thích',
                    'Nói chuyện với bạn bè hoặc gia đình'
                ]
            }
        ])
    
    elif severity in ['moderate', 'moderately_severe']:
        recommendations.extend([
            {
                'type': 'professional',
                'priority': 'high',
                'title': 'Cân nhắc tìm kiếm hỗ trợ chuyên nghiệp',
                'description': 'Nên tham khảo ý kiến từ chuyên gia sức khỏe tâm thần.',
                'actions': [
                    'Liên hệ với bác sĩ tâm lý hoặc tâm thần',
                    'Tham gia liệu pháp tâm lý cá nhân',
                    'Cân nhắc tham gia nhóm hỗ trợ',
                    'Thảo luận về các phương pháp điều trị'
                ]
            }
        ])
    
    elif severity in ['severe', 'extremely_severe', 'high']:
        recommendations.extend([
            {
                'type': 'urgent',
                'priority': 'urgent',
                'title': 'Cần can thiệp ngay lập tức',
                'description': 'Tình trạng nghiêm trọng, cần được hỗ trợ chuyên nghiệp ngay.',
                'actions': [
                    'Liên hệ ngay với chuyên gia sức khỏe tâm thần',
                    'Cân nhắc điều trị nội trú nếu cần thiết',
                    'Đảm bảo có người thân bên cạnh hỗ trợ',
                    'Tránh xa các chất kích thích'
                ]
            }
        ])
    
    # Assessment-specific recommendations
    if assessment_type == 'phq9':
        if results.get('risk_indicators'):
            recommendations.append({
                'type': 'crisis',
                'priority': 'urgent',
                'title': 'Cần hỗ trợ khẩn cấp',
                'description': 'Phát hiện dấu hiệu nguy hiểm. Vui lòng tìm kiếm giúp đỡ ngay.',
                'actions': [
                    'Gọi đường dây nóng: 1800 599 999',
                    'Đến bệnh viện gần nhất',
                    'Liên hệ với người thân ngay lập tức',
                    'Không ở một mình'
                ]
            })
    
    elif assessment_type == 'gad7' and total_score >= 10:
        recommendations.append({
            'type': 'anxiety_management',
            'priority': 'high',
            'title': 'Quản lý lo âu',
            'description': 'Học các kỹ thuật quản lý lo âu hiệu quả.',
            'actions': [
                'Thực hành kỹ thuật thở sâu',
                'Học về liệu pháp nhận thức hành vi (CBT)',
                'Tránh caffeine và chất kích thích',
                'Tập yoga hoặc tai chi'
            ]
        })
    
    elif assessment_type == 'dass21_stress' and total_score >= 10:
        recommendations.append({
            'type': 'stress_management',
            'priority': 'high',
            'title': 'Quản lý căng thẳng',
            'description': 'Áp dụng các phương pháp giảm căng thẳng hiệu quả.',
            'actions': [
                'Xác định và giảm nguồn căng thẳng',
                'Học kỹ năng quản lý thời gian',
                'Thực hành mindfulness',
                'Tăng cường hoạt động thể chất'
            ]
        })
    
    return recommendations

def _get_next_actions(severity: str) -> List[str]:
    """Get immediate next actions based on severity"""
    actions = {
        'minimal': [
            'Tiếp tục duy trì lối sống lành mạnh',
            'Thực hiện đánh giá định kỳ sau 3-6 tháng'
        ],
        'mild': [
            'Áp dụng các kỹ thuật tự chăm sóc',
            'Theo dõi triệu chứng trong 2-4 tuần',
            'Đánh giá lại nếu triệu chứng không cải thiện'
        ],
        'moderate': [
            'Tham khảo ý kiến chuyên gia trong 1-2 tuần',
            'Bắt đầu áp dụng các can thiệp đơn giản',
            'Theo dõi triệu chứng hàng ngày'
        ],
        'moderately_severe': [
            'Liên hệ chuyên gia sức khỏe tâm thần trong tuần này',
            'Cân nhắc bắt đầu điều trị',
            'Đảm bảo có hệ thống hỗ trợ'
        ],
        'severe': [
            'Tìm kiếm hỗ trợ chuyên nghiệp ngay lập tức',
            'Cân nhắc điều trị tích cực',
            'Đảm bảo an toàn cá nhân'
        ],
        'high': [
            'Liên hệ đường dây khẩn cấp ngay',
            'Không ở một mình',
            'Đến cơ sở y tế gần nhất'
        ]
    }
    
    return actions.get(severity, ['Tham khảo ý kiến chuyên gia'])

def _validate_session_id(session_id: str) -> bool:
    """FIXED: Simple session ID validation"""
    if not session_id or not isinstance(session_id, str):
        return False
    
    # Simple validation - in production, use proper UUID validation
    return len(session_id) >= 10 and len(session_id) <= 100

def _sanitize_answers(answers: Dict) -> Dict:
    """Sanitize and clean answer data"""
    sanitized = {}
    
    for question_id, answer in answers.items():
        # Ensure question_id is string and answer is numeric
        if isinstance(question_id, str) and isinstance(answer, (int, float)):
            # Clamp answer values to reasonable range
            sanitized_answer = max(0, min(int(answer), 3))  # Most scales are 0-3
            sanitized[question_id] = sanitized_answer
    
    return sanitized

def _log_assessment_activity(assessment_type: str, session_id: str, action: str, **kwargs):
    """Log assessment activity for monitoring"""
    log_data = {
        'assessment_type': assessment_type,
        'session_id': session_id,
        'action': action,
        'timestamp': datetime.now().isoformat(),
        **kwargs
    }
    
    logger.info(f"Assessment activity: {json.dumps(log_data, ensure_ascii=False)}")

# Error handlers for assessment blueprint

@assessment_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad request',
        'message': 'Yêu cầu không hợp lệ'
    }), 400

@assessment_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'Không tìm thấy tài nguyên được yêu cầu'
    }), 404

@assessment_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Đã xảy ra lỗi máy chủ nội bộ'
    }), 500

# Export the blueprint
__all__ = ['assessment_bp', 'STANDARD_QUESTIONNAIRES']