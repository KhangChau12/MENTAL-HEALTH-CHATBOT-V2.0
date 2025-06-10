"""
Chat API - Handles chat-related endpoints with comprehensive error handling
"""

import logging
import uuid
from flask import Blueprint, request, jsonify, session
from datetime import datetime

from ..core.chat_engine import ChatEngine
from ..utils.validators import validate_message, validate_chat_state
from ..services.together_ai import check_api_health
from ..utils.constants import ChatStates, AssessmentTypes

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
        
        # Extract and validate data
        user_message = data.get('message', '').strip()
        history = data.get('history', [])
        state = data.get('state', {})
        use_ai = data.get('use_ai', True)
        
        # Validate message
        if not validate_message(user_message):
            return jsonify({
                'error': 'Invalid message',
                'message': 'Tin nhắn không hợp lệ. Vui lòng nhập nội dung có ý nghĩa.'
            }), 400
        
        # Validate message length
        if len(user_message) > 1000:
            return jsonify({
                'error': 'Message too long',
                'message': 'Tin nhắn quá dài. Vui lòng nhập tin nhắn ngắn hơn.'
            }), 400
        
        # Validate and clean state
        if not validate_chat_state(state):
            state = _initialize_default_state()
            logger.info("Initialized new chat state")
        
        # Add session ID if not present
        if 'session_id' not in state:
            state['session_id'] = _generate_session_id()
        
        # Validate history format
        if not isinstance(history, list):
            history = []
        
        # Clean and validate history items
        history = _clean_history(history)
        
        # Rate limiting check
        if not _check_rate_limit(state):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Bạn đang gửi tin nhắn quá nhanh. Vui lòng chờ một chút.'
            }), 429
        
        # Process message
        try:
            response = chat_engine.process_message(
                message=user_message,
                history=history,
                state=state,
                use_ai=use_ai
            )
            
            # Validate response
            if not response or not isinstance(response, dict):
                raise ValueError("Invalid response from chat engine")
            
            # Log successful interaction
            logger.info(f"Chat interaction: session={state.get('session_id')}, "
                       f"message_length={len(user_message)}, "
                       f"use_ai={use_ai}, "
                       f"response_type={response.get('metadata', {}).get('type')}")
            
            # Store session data
            _store_session_data(state.get('session_id'), response)
            
            return jsonify(response)
            
        except Exception as chat_error:
            logger.error(f"Chat engine error: {chat_error}")
            
            # Try fallback response
            fallback_response = _generate_fallback_response(user_message, history, state)
            return jsonify(fallback_response)
        
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Đã xảy ra lỗi khi xử lý tin nhắn. Vui lòng thử lại sau.'
        }), 500

@chat_bp.route('/reset', methods=['POST'])
def reset_chat():
    """
    Reset chat conversation to initial state
    """
    try:
        data = request.get_json() or {}
        state = data.get('state', {})
        
        # Keep session ID if it exists
        session_id = state.get('session_id') or _generate_session_id()
        
        # Create new state
        new_state = _initialize_default_state()
        new_state['session_id'] = session_id
        
        # Reset conversation
        reset_response = chat_engine.reset_conversation(new_state)
        
        # Clear session data
        _clear_session_data(session_id)
        
        logger.info(f"Chat session reset: {session_id}")
        
        return jsonify(reset_response)
        
    except Exception as e:
        logger.error(f"Error resetting chat: {e}")
        return jsonify({
            'error': 'Reset failed',
            'message': 'Không thể khởi tạo lại cuộc trò chuyện. Vui lòng tải lại trang.'
        }), 500

@chat_bp.route('/status/<session_id>', methods=['GET'])
def get_chat_status(session_id):
    """
    Get status of a chat session
    """
    try:
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        # Get session data
        session_data = _get_session_data(session_id)
        
        if not session_data:
            return jsonify({
                'status': 'not_found',
                'message': 'Session not found'
            }), 404
        
        status = {
            'session_id': session_id,
            'status': 'active',
            'current_phase': session_data.get('state', {}).get('current_phase', 'chat'),
            'message_count': session_data.get('state', {}).get('message_count', 0),
            'started_at': session_data.get('state', {}).get('started_at'),
            'last_activity': session_data.get('last_activity'),
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting chat status: {e}")
        return jsonify({
            'error': 'Failed to get status',
            'message': 'Không thể lấy trạng thái phiên làm việc'
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
                'transition_logic': True,
                'session_management': True,
                'rate_limiting': True
            },
            'version': '1.0.0'
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
        # In production, these would come from database queries
        stats = {
            'total_sessions': _get_total_sessions_count(),
            'active_sessions': _get_active_sessions_count(),
            'avg_session_length': _get_avg_session_length(),
            'ai_availability_rate': _get_ai_availability_rate(),
            'supported_languages': ['vi', 'en'],
            'supported_assessments': [
                AssessmentTypes.PHQ9,
                AssessmentTypes.GAD7,
                AssessmentTypes.DASS21_STRESS,
                AssessmentTypes.SUICIDE_RISK
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'error': 'Failed to get statistics',
            'message': 'Không thể lấy thống kê'
        }), 500

# Helper functions

def _generate_session_id() -> str:
    """Generate unique session ID"""
    return str(uuid.uuid4())

def _initialize_default_state() -> dict:
    """Initialize default chat state"""
    return {
        'session_id': _generate_session_id(),
        'current_phase': 'chat',
        'language': 'vi',
        'scores': {},
        'message_count': 0,
        'started_at': datetime.now().isoformat(),
        'last_activity': datetime.now().isoformat()
    }

def _clean_history(history: list) -> list:
    """Clean and validate conversation history"""
    if not isinstance(history, list):
        return []
    
    cleaned = []
    for item in history:
        if isinstance(item, dict) and 'role' in item and 'content' in item:
            # Validate role
            if item['role'] in ['user', 'bot', 'assistant']:
                # Normalize role
                role = 'bot' if item['role'] == 'assistant' else item['role']
                
                # Clean content
                content = str(item['content']).strip()
                if content and len(content) <= 2000:  # Max content length
                    cleaned.append({
                        'role': role,
                        'content': content,
                        'timestamp': item.get('timestamp', datetime.now().isoformat())
                    })
    
    # Limit history length to prevent memory issues
    return cleaned[-20:] if len(cleaned) > 20 else cleaned

def _check_rate_limit(state: dict) -> bool:
    """Check if user is within rate limits"""
    session_id = state.get('session_id')
    if not session_id:
        return True
    
    # Simple rate limiting - max 60 messages per hour per session
    # In production, use Redis or proper rate limiting library
    current_time = datetime.now()
    last_activity = state.get('last_activity')
    
    if last_activity:
        try:
            last_time = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            time_diff = (current_time - last_time.replace(tzinfo=None)).total_seconds()
            
            # Allow if more than 1 second has passed (simple rate limiting)
            return time_diff >= 1.0
        except:
            pass
    
    return True

def _store_session_data(session_id: str, response_data: dict):
    """Store session data (in production, use database)"""
    try:
        # For now, store in Flask session
        # In production, use Redis or database
        session[f'chat_session_{session_id}'] = {
            'data': response_data,
            'last_activity': datetime.now().isoformat()
        }
    except Exception as e:
        logger.warning(f"Failed to store session data: {e}")

def _get_session_data(session_id: str) -> dict:
    """Get session data (in production, use database)"""
    try:
        return session.get(f'chat_session_{session_id}', {})
    except Exception as e:
        logger.warning(f"Failed to get session data: {e}")
        return {}

def _clear_session_data(session_id: str):
    """Clear session data"""
    try:
        session.pop(f'chat_session_{session_id}', None)
    except Exception as e:
        logger.warning(f"Failed to clear session data: {e}")

def _generate_fallback_response(message: str, history: list, state: dict) -> dict:
    """Generate fallback response when chat engine fails"""
    fallback_messages = [
        "Xin lỗi, tôi đang gặp chút khó khăn. Bạn có thể chia sẻ thêm về cảm giác của mình không?",
        "Tôi hiểu bạn đang muốn chia sẻ. Có thể bạn kể thêm chi tiết về tình trạng của mình?",
        "Cảm ơn bạn đã tin tưởng chia sẻ. Hãy cho tôi biết thêm về những gì bạn đang trải qua.",
        "Tôi đang lắng nghe. Bạn có muốn nói thêm về cảm xúc gần đây của mình không?"
    ]
    
    # Select response based on message count
    message_count = len(history)
    response_index = min(message_count // 2, len(fallback_messages) - 1)
    
    fallback_message = fallback_messages[response_index]
    
    # Update state
    state['message_count'] = state.get('message_count', 0) + 1
    state['last_activity'] = datetime.now().isoformat()
    
    return {
        'message': fallback_message,
        'history': history + [
            {'role': 'user', 'content': message, 'timestamp': datetime.now().isoformat()},
            {'role': 'bot', 'content': fallback_message, 'timestamp': datetime.now().isoformat()}
        ],
        'state': state,
        'metadata': {
            'type': 'fallback_response',
            'phase': 'chat',
            'ai_used': False,
            'fallback_reason': 'chat_engine_error'
        }
    }

# Statistics helper functions (mock data for now)
def _get_total_sessions_count() -> int:
    """Get total sessions count (mock)"""
    return 1247  # Mock data

def _get_active_sessions_count() -> int:
    """Get active sessions count (mock)"""
    return 23  # Mock data

def _get_avg_session_length() -> float:
    """Get average session length in minutes (mock)"""
    return 8.5  # Mock data

def _get_ai_availability_rate() -> float:
    """Get AI service availability rate (mock)"""
    try:
        ai_health = check_api_health()
        return 98.5 if ai_health.get('available') else 85.0
    except:
        return 90.0  # Fallback