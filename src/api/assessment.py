"""
Assessment API - Handles assessment-related endpoints
"""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime

from ..core.assessment_engine import AssessmentEngine
from ..utils.validators import validate_assessment_response
from data.questionnaires import questionnaires

logger = logging.getLogger(__name__)

# Create blueprint
assessment_bp = Blueprint('assessment', __name__)

# Initialize assessment engine
assessment_engine = AssessmentEngine()

@assessment_bp.route('/start', methods=['POST'])
def start_assessment():
    """
    Start a new assessment
    
    Expected JSON:
    {
        "assessment_type": "phq9",
        "state": {...}
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
        state = data.get('state', {})
        
        # Validate assessment type
        if not assessment_type or assessment_type not in questionnaires:
            return jsonify({
                'error': 'Invalid assessment type',
                'message': 'Loại đánh giá không hợp lệ'
            }), 400
        
        # Start assessment
        response = assessment_engine.start_assessment(assessment_type, state)
        
        logger.info(f"Assessment started: type={assessment_type}, "
                   f"session={state.get('session_id')}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error starting assessment: {e}")
        return jsonify({
            'error': 'Failed to start assessment',
            'message': 'Không thể bắt đầu đánh giá. Vui lòng thử lại.'
        }), 500

@assessment_bp.route('/respond', methods=['POST'])
def respond_to_question():
    """
    Respond to an assessment question
    
    Expected JSON:
    {
        "response": "user response",
        "state": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Vui lòng cung cấp câu trả lời'
            }), 400
        
        user_response = data.get('response', '').strip()
        state = data.get('state', {})
        
        # Validate response
        if not validate_assessment_response(user_response):
            return jsonify({
                'error': 'Invalid response',
                'message': 'Câu trả lời không hợp lệ. Vui lòng thử lại.'
            }), 400
        
        # Validate state
        if not state.get('assessment'):
            return jsonify({
                'error': 'No active assessment',
                'message': 'Không có phiên đánh giá đang hoạt động'
            }), 400
        
        # Process response
        response = assessment_engine.process_assessment_response(user_response, state)
        
        logger.info(f"Assessment response processed: "
                   f"session={state.get('session_id')}, "
                   f"assessment_type={state.get('assessment', {}).get('type')}, "
                   f"question_index={state.get('assessment', {}).get('current_question_index')}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing assessment response: {e}")
        return jsonify({
            'error': 'Failed to process response',
            'message': 'Không thể xử lý câu trả lời. Vui lòng thử lại.'
        }), 500

@assessment_bp.route('/skip', methods=['POST'])
def skip_question():
    """
    Skip current assessment question
    
    Expected JSON:
    {
        "state": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided'
            }), 400
        
        state = data.get('state', {})
        
        # Validate state
        assessment_state = state.get('assessment')
        if not assessment_state:
            return jsonify({
                'error': 'No active assessment',
                'message': 'Không có phiên đánh giá đang hoạt động'
            }), 400
        
        # Process skip (treat as score 0)
        skip_response = "0"  # Neutral/minimal score for skipped questions
        response = assessment_engine.process_assessment_response(skip_response, state)
        
        # Add skip indicator to metadata
        if 'metadata' in response:
            response['metadata']['skipped'] = True
        
        logger.info(f"Assessment question skipped: "
                   f"session={state.get('session_id')}, "
                   f"question_index={assessment_state.get('current_question_index')}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error skipping question: {e}")
        return jsonify({
            'error': 'Failed to skip question',
            'message': 'Không thể bỏ qua câu hỏi'
        }), 500

@assessment_bp.route('/list', methods=['GET'])
def list_assessments():
    """
    Get list of available assessments
    """
    try:
        assessments = []
        
        for assessment_id, config in questionnaires.items():
            assessments.append({
                'id': assessment_id,
                'title': config.get('title', assessment_id.upper()),
                'description': config.get('description', ''),
                'question_count': len(config.get('questions', [])),
                'estimated_time': config.get('estimated_time', '5-10 phút'),
                'category': config.get('category', 'general')
            })
        
        return jsonify({
            'assessments': assessments,
            'total_count': len(assessments)
        })
        
    except Exception as e:
        logger.error(f"Error listing assessments: {e}")
        return jsonify({
            'error': 'Failed to get assessment list'
        }), 500

@assessment_bp.route('/info/<assessment_type>', methods=['GET'])
def get_assessment_info(assessment_type):
    """
    Get detailed information about a specific assessment
    """
    try:
        if assessment_type not in questionnaires:
            return jsonify({
                'error': 'Assessment not found',
                'message': 'Không tìm thấy bộ đánh giá này'
            }), 404
        
        config = questionnaires[assessment_type]
        
        info = {
            'id': assessment_type,
            'title': config.get('title', assessment_type.upper()),
            'description': config.get('description', ''),
            'category': config.get('category', 'general'),
            'question_count': len(config.get('questions', [])),
            'estimated_time': config.get('estimated_time', '5-10 phút'),
            'scoring_info': config.get('scoring_info', {}),
            'disclaimer': config.get('disclaimer', ''),
            'instructions': config.get('instructions', [])
        }
        
        return jsonify(info)
        
    except Exception as e:
        logger.error(f"Error getting assessment info: {e}")
        return jsonify({
            'error': 'Failed to get assessment information'
        }), 500

@assessment_bp.route('/progress', methods=['POST'])
def get_progress():
    """
    Get assessment progress information
    
    Expected JSON:
    {
        "state": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided'
            }), 400
        
        state = data.get('state', {})
        assessment_state = state.get('assessment')
        
        if not assessment_state:
            return jsonify({
                'error': 'No active assessment',
                'message': 'Không có phiên đánh giá đang hoạt động'
            }), 400
        
        current_index = assessment_state.get('current_question_index', 0)
        total_questions = assessment_state.get('total_questions', 0)
        responses = assessment_state.get('responses', {})
        
        progress_info = {
            'current_question': current_index + 1,
            'total_questions': total_questions,
            'completed_questions': len(responses),
            'progress_percentage': (len(responses) / total_questions * 100) if total_questions > 0 else 0,
            'assessment_type': assessment_state.get('type'),
            'started_at': assessment_state.get('started_at'),
            'estimated_remaining_time': f"{(total_questions - len(responses)) * 1} phút"
        }
        
        return jsonify(progress_info)
        
    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        return jsonify({
            'error': 'Failed to get progress information'
        }), 500

@assessment_bp.route('/validate', methods=['POST'])
def validate_response():
    """
    Validate assessment response format
    
    Expected JSON:
    {
        "response": "user response",
        "question_type": "likert_scale"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided'
            }), 400
        
        response = data.get('response', '').strip()
        question_type = data.get('question_type', 'likert_scale')
        
        is_valid = validate_assessment_response(response, question_type)
        
        validation_result = {
            'is_valid': is_valid,
            'response': response,
            'question_type': question_type
        }
        
        if not is_valid:
            validation_result['suggestions'] = [
                'Vui lòng trả lời bằng số từ 0 đến 4',
                'Hoặc mô tả cảm giác của bạn bằng từ ngữ',
                'Ví dụ: "thường xuyên", "hiếm khi", "không bao giờ"'
            ]
        
        return jsonify(validation_result)
        
    except Exception as e:
        logger.error(f"Error validating response: {e}")
        return jsonify({
            'error': 'Validation failed'
        }), 500