"""
Chat API - Handles chat-related endpoints
"""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime

from ..core.chat_engine import ChatEngine
from ..utils.validators import validate_message, validate_chat_state
from ..services.together_ai import check_api_health

logger = logging.getLogger(__name__)

# Create blueprint
chat_bp = Blueprint('chat', __name__)

# Initialize chat engine
chat_engine = ChatEngine()

@chat_bp.route('/send', methods=['POST'])
def send_message():
    """
    Handle user message and return bot response
    
    Expected JSON:
    {
        "message": "user message",
        "history": [...],
        "state": {...},
        "use_ai": true
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Vui lòng gửi tin nhắn hợp lệ'
            }), 400
        
        # Extract data
        user_message = data.get('message', '').strip()
        history = data.get('history', [])
        state = data.get('state', {})
        use_ai = data.get('use_ai', True)
        
        # Validate message
        if not validate_message(user_message):
            return jsonify({
                'error': 'Invalid message',
                'message': 'Tin nhắn không hợp lệ. Vui lòng nhập nội dung.'
            }), 400
        
        # Validate and clean state
        if not validate_chat_state(state):
            state = _initialize_default_state()
        
        # Add session ID if not present
        if 'session_id' not in state:
            state['session_id'] = _generate_session_id()
        
        # Process message
        response = chat_engine.process_message(
            message=user_message,
            history=history,
            state=state,
            use_ai=use_ai
        )
        
        # Log interaction
        logger.info(f"Chat interaction: session={state.get('session_id')}, "
                   f"message_length={len(user_message)}, "
                   f"use_ai={use_ai}, "
                   f"response_type={response.get('metadata', {}).get('type')}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Đã xảy ra lỗi khi xử lý tin nhắn. Vui lòng thử lại.'
        }), 500

@chat_bp.route('/start', methods=['POST'])
def start_chat():
    """
    Initialize a new chat session
    
    Expected JSON:
    {
        "language": "vi",
        "mode": "ai"
    }
    """
    try:
        data = request.get_json() or {}
        
        language = data.get('language', 'vi')
        mode = data.get('mode', 'ai')
        
        # Create initial state
        state = {
            'session_id': _generate_session_id(),
            'current_phase': 'chat',
            'language': language,
            'mode': mode,
            'scores': {},
            'message_count': 0,
            'started_at': datetime.now().isoformat()
        }
        
        # Create welcome message
        if language == 'vi':
            welcome_message = """Xin chào! Tôi là trợ lý sức khỏe tâm thần của bạn. 

Tôi ở đây để lắng nghe và hỗ trợ bạn. Hãy chia sẻ với tôi về cảm giác hoặc những khó khăn mà bạn đang gặp phải.

*Lưu ý: Đây là công cụ sàng lọc sơ bộ, không thay thế cho tư vấn y tế chuyên nghiệp.*"""
        else:
            welcome_message = """Hello! I'm your mental health assistant.

I'm here to listen and support you. Please share with me how you're feeling or any difficulties you're experiencing.

*Note: This is a preliminary screening tool and does not replace professional medical consultation.*"""
        
        logger.info(f"New chat session started: {state['session_id']}, language={language}, mode={mode}")
        
        return jsonify({
            'message': welcome_message,
            'state': state,
            'metadata': {
                'type': 'welcome',
                'phase': 'chat',
                'session_started': True
            }
        })
        
    except Exception as e:
        logger.error(f"Error starting chat: {e}")
        return jsonify({
            'error': 'Failed to start chat',
            'message': 'Không thể khởi tạo cuộc trò chuyện. Vui lòng thử lại.'
        }), 500

@chat_bp.route('/reset', methods=['POST'])
def reset_chat():
    """
    Reset current chat session
    """
    try:
        # Create fresh state
        state = {
            'session_id': _generate_session_id(),
            'current_phase': 'chat',
            'language': 'vi',
            'scores': {},
            'message_count': 0,
            'started_at': datetime.now().isoformat()
        }
        
        reset_message = """Cuộc trò chuyện đã được khởi tạo lại. 

Hãy chia sẻ với tôi về tình trạng hiện tại của bạn."""
        
        logger.info(f"Chat session reset: {state['session_id']}")
        
        return jsonify({
            'message': reset_message,
            'state': state,
            'metadata': {
                'type': 'reset',
                'phase': 'chat',
                'session_reset': True
            }
        })
        
    except Exception as e:
        logger.error(f"Error resetting chat: {e}")
        return jsonify({
            'error': 'Reset failed',
            'message': 'Không thể khởi tạo lại cuộc trò chuyện.'
        }), 500

@chat_bp.route('/health', methods=['GET'])
def chat_health():
    """
    Check chat service health including AI availability
    """
    try:
        # Check AI service health
        ai_health = check_api_health()
        
        health_status = {
            'service': 'chat',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'ai_service': ai_health,
            'features': {
                'chat_engine': True,
                'ai_classification': ai_health.get('available', False),
                'keyword_fallback': True,
                'transition_logic': True
            }
        }
        
        # Determine overall status
        if not ai_health.get('available', False):
            health_status['status'] = 'degraded'
            health_status['message'] = 'AI service unavailable, using fallback responses'
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'service': 'chat',
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@chat_bp.route('/stats', methods=['GET'])
def chat_stats():
    """
    Get basic chat service statistics
    """
    try:
        # In a real application, these would come from a database
        # For now, return mock statistics
        stats = {
            'total_sessions': 0,  # Would be tracked in production
            'active_sessions': 0,  # Would be tracked in production
            'avg_session_length': 0,  # Would be calculated from data
            'ai_availability_rate': 95.0,  # Would be calculated from health checks
            'supported_languages': ['vi', 'en'],
            'supported_assessments': ['phq9', 'gad7', 'dass21_stress', 'suicide_risk']
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'error': 'Failed to get statistics'
        }), 500

def _generate_session_id() -> str:
    """Generate unique session ID"""
    import uuid
    return str(uuid.uuid4())

def _initialize_default_state() -> dict:
    """Initialize default chat state"""
    return {
        'session_id': _generate_session_id(),
        'current_phase': 'chat',
        'language': 'vi',
        'scores': {},
        'message_count': 0,
        'started_at': datetime.now().isoformat()
    }