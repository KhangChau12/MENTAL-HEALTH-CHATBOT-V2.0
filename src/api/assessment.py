"""
Assessment API - Complete endpoints for handling assessments and results
"""

import logging
import json
from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, List, Optional, Any

from ..core.assessment_engine import AssessmentEngine
from ..services.export_service import ExportService
from ..utils.validators import validate_assessment_data, validate_answers, validate_session_id
from ..utils.constants import AssessmentTypes

logger = logging.getLogger(__name__)

# Create blueprint
assessment_bp = Blueprint('assessment', __name__)

# Initialize services
assessment_engine = AssessmentEngine()
export_service = ExportService()

@assessment_bp.route('/start', methods=['POST'])
def start_assessment():
    """
    Start a new assessment
    
    Expected JSON:
    {
        "assessment_type": "phq9",
        "session_id": "uuid",
        "language": "vi"
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
        
        # Validate assessment type
        if not assessment_type or assessment_type not in [
            AssessmentTypes.PHQ9, AssessmentTypes.GAD7, 
            AssessmentTypes.DASS21_STRESS, AssessmentTypes.SUICIDE_RISK
        ]:
            return jsonify({
                'error': 'Invalid assessment type',
                'message': 'Loại đánh giá không hợp lệ'
            }), 400
        
        # Start assessment
        assessment_data = assessment_engine.start_assessment(
            assessment_type=assessment_type,
            session_id=session_id,
            language=language
        )
        
        if not assessment_data:
            return jsonify({
                'error': 'Failed to start assessment',
                'message': 'Không thể khởi tạo đánh giá'
            }), 500
        
        logger.info(f"Assessment started: type={assessment_type}, session={session_id}")
        
        return jsonify({
            'success': True,
            'assessment': assessment_data,
            'message': 'Đánh giá đã được khởi tạo thành công'
        })
        
    except Exception as e:
        logger.error(f"Error starting assessment: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Đã xảy ra lỗi khi khởi tạo đánh giá'
        }), 500

@assessment_bp.route('/submit', methods=['POST'])
def submit_assessment():
    """
    Submit completed assessment answers
    
    Expected JSON:
    {
        "session_id": "uuid",
        "assessment_type": "phq9",
        "answers": {"q1": 2, "q2": 1, ...},
        "chat_history": [...],
        "state": {...}
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
        session_id = data.get('session_id')
        assessment_type = data.get('assessment_type')
        answers = data.get('answers', {})
        chat_history = data.get('chat_history', [])
        state = data.get('state', {})
        
        # Validate required fields
        if not session_id:
            return jsonify({
                'error': 'Session ID required',
                'message': 'Cần có mã phiên làm việc'
            }), 400
        
        if not assessment_type:
            return jsonify({
                'error': 'Assessment type required',
                'message': 'Cần xác định loại đánh giá'
            }), 400
        
        if not answers:
            return jsonify({
                'error': 'No answers provided',
                'message': 'Không có câu trả lời được cung cấp'
            }), 400
        
        # Validate answers format
        if not validate_answers(answers, assessment_type):
            return jsonify({
                'error': 'Invalid answers format',
                'message': 'Định dạng câu trả lời không hợp lệ'
            }), 400
        
        # Process assessment
        try:
            results = assessment_engine.process_assessment(
                assessment_type=assessment_type,
                answers=answers,
                session_id=session_id,
                chat_history=chat_history,
                state=state
            )
            
            if not results:
                raise ValueError("Assessment processing returned no results")
            
        except Exception as processing_error:
            logger.error(f"Assessment processing failed: {processing_error}")
            return jsonify({
                'error': 'Processing failed',
                'message': 'Không thể xử lý kết quả đánh giá'
            }), 500
        
        # Log successful completion
        logger.info(f"Assessment completed: type={assessment_type}, "
                   f"session={session_id}, score={results.get('total_score')}")
        
        return jsonify({
            'success': True,
            'results': results,
            'message': 'Đánh giá đã được hoàn thành thành công'
        })
        
    except Exception as e:
        logger.error(f"Error submitting assessment: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Đã xảy ra lỗi khi xử lý đánh giá'
        }), 500

@assessment_bp.route('/results/<session_id>', methods=['GET'])
def get_assessment_results(session_id):
    """
    Get assessment results by session ID
    """
    try:
        if not session_id:
            return jsonify({
                'error': 'Session ID required',
                'message': 'Cần có mã phiên làm việc'
            }), 400
        
        # For now, return a message that results should be loaded from localStorage
        # In a real implementation, this would query a database
        return jsonify({
            'success': False,
            'message': 'Kết quả được lưu trữ cục bộ. Vui lòng kiểm tra localStorage của trình duyệt.',
            'note': 'This endpoint would normally query a database for stored results'
        })
        
    except Exception as e:
        logger.error(f"Error getting results: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Không thể tải kết quả đánh giá'
        }), 500

@assessment_bp.route('/validate', methods=['POST'])
def validate_assessment():
    """
    Validate assessment data before submission
    
    Expected JSON:
    {
        "assessment_type": "phq9",
        "answers": {"q1": 2, "q2": 1, ...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Vui lòng cung cấp dữ liệu để kiểm tra'
            }), 400
        
        assessment_type = data.get('assessment_type')
        answers = data.get('answers', {})
        
        # Validate assessment type
        valid_types = [
            AssessmentTypes.PHQ9, AssessmentTypes.GAD7,
            AssessmentTypes.DASS21_STRESS, AssessmentTypes.SUICIDE_RISK
        ]
        
        if assessment_type not in valid_types:
            return jsonify({
                'valid': False,
                'errors': ['Loại đánh giá không hợp lệ'],
                'message': 'Loại đánh giá không được hỗ trợ'
            })
        
        # Validate answers
        validation_result = assessment_engine.validate_assessment_answers(
            assessment_type, answers
        )
        
        return jsonify(validation_result)
        
    except Exception as e:
        logger.error(f"Error validating assessment: {e}")
        return jsonify({
            'error': 'Validation failed',
            'message': 'Không thể kiểm tra dữ liệu đánh giá'
        }), 500

@assessment_bp.route('/preview', methods=['POST'])
def preview_assessment_results():
    """
    Preview assessment results without saving
    
    Expected JSON:
    {
        "assessment_type": "phq9",
        "answers": {"q1": 2, "q2": 1, ...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Vui lòng cung cấp dữ liệu đánh giá'
            }), 400
        
        assessment_type = data.get('assessment_type')
        answers = data.get('answers', {})
        
        if not assessment_type or not answers:
            return jsonify({
                'error': 'Missing required data',
                'message': 'Thiếu thông tin đánh giá hoặc câu trả lời'
            }), 400
        
        # Generate preview
        try:
            preview = assessment_engine.generate_preview_results(
                assessment_type, answers
            )
            
            return jsonify({
                'success': True,
                'preview': preview,
                'message': 'Xem trước kết quả thành công'
            })
            
        except Exception as preview_error:
            logger.error(f"Preview generation failed: {preview_error}")
            return jsonify({
                'error': 'Preview failed',
                'message': 'Không thể tạo xem trước kết quả'
            }), 500
        
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Đã xảy ra lỗi khi tạo xem trước'
        }), 500

@assessment_bp.route('/types', methods=['GET'])
def get_assessment_types():
    """
    Get available assessment types and their information
    """
    try:
        assessment_types = {
            AssessmentTypes.PHQ9: {
                'name': 'PHQ-9',
                'title': 'Đánh giá Trầm cảm',
                'description': 'Bộ câu hỏi sàng lọc trầm cảm tiêu chuẩn',
                'question_count': 9,
                'estimated_time': '3-5 phút',
                'category': 'depression'
            },
            AssessmentTypes.GAD7: {
                'name': 'GAD-7',
                'title': 'Đánh giá Lo âu',
                'description': 'Bộ câu hỏi sàng lọc lo âu tổng quát',
                'question_count': 7,
                'estimated_time': '2-4 phút',
                'category': 'anxiety'
            },
            AssessmentTypes.DASS21_STRESS: {
                'name': 'DASS-21',
                'title': 'Đánh giá Căng thẳng',
                'description': 'Bộ câu hỏi đánh giá căng thẳng',
                'question_count': 7,
                'estimated_time': '3-5 phút',
                'category': 'stress'
            },
            AssessmentTypes.SUICIDE_RISK: {
                'name': 'Suicide Risk',
                'title': 'Đánh giá Nguy cơ Tự tử',
                'description': 'Đánh giá nhanh nguy cơ tự tử',
                'question_count': 5,
                'estimated_time': '2-3 phút',
                'category': 'risk'
            }
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

@assessment_bp.route('/statistics', methods=['GET'])
def get_assessment_statistics():
    """
    Get assessment usage statistics (mock data for now)
    """
    try:
        # In a real implementation, this would query database
        stats = {
            'total_assessments': 1247,
            'assessments_today': 23,
            'assessments_this_week': 156,
            'assessments_this_month': 678,
            'by_type': {
                'phq9': 487,
                'gad7': 345,
                'dass21_stress': 289,
                'suicide_risk': 126
            },
            'completion_rate': 87.3,
            'average_duration': '4.2 phút',
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

@assessment_bp.route('/health', methods=['GET'])
def assessment_health():
    """
    Check assessment service health
    """
    try:
        health_status = {
            'service': 'assessment',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'features': {
                'assessment_engine': True,
                'result_processing': True,
                'validation': True,
                'preview_generation': True,
                'export_integration': export_service is not None
            },
            'supported_types': [
                AssessmentTypes.PHQ9,
                AssessmentTypes.GAD7,
                AssessmentTypes.DASS21_STRESS,
                AssessmentTypes.SUICIDE_RISK
            ],
            'version': '1.0.0'
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'service': 'assessment',
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Helper functions

def _validate_session_id(session_id: str) -> bool:
    """Validate session ID format"""
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
            sanitized_answer = max(0, min(int(answer), 10))
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
    
    logger.info(f"Assessment activity: {json.dumps(log_data)}")

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