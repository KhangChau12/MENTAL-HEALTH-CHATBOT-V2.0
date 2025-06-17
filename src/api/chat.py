"""
Chat API - SỬA ĐỔI NHỎ để tương thích với transition logic mới
Updated to handle AI analysis errors and fallbacks
"""

from flask import Blueprint, request, jsonify, session
import logging
from typing import Dict, List, Any, Optional
import traceback
from datetime import datetime

from src.core.chat_engine import create_chat_engine
from src.services.ai_context_analyzer import initialize_ai_analyzer
from src.utils.validators import validate_message, validate_chat_state
from src.utils.constants import ERROR_MESSAGES, SUCCESS_MESSAGES

logger = logging.getLogger(__name__)

# Create Blueprint
chat_bp = Blueprint('chat', __name__)

# Initialize services
chat_engine = None
ai_analyzer_initialized = False

def initialize_chat_services():
    """Initialize chat services"""
    global chat_engine, ai_analyzer_initialized
    
    try:
        # Initialize chat engine
        chat_engine = create_chat_engine()
        logger.info("Chat engine initialized successfully")
        
        # Initialize AI analyzer
        ai_analyzer_initialized = initialize_ai_analyzer()
        if ai_analyzer_initialized:
            logger.info("AI analyzer initialized successfully")
        else:
            logger.warning("AI analyzer failed to initialize - using fallback mode")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize chat services: {e}")
        return False

# Initialize on module load
initialize_chat_services()
@chat_bp.route('/send', methods=['POST'])
@chat_bp.route('/send_message', methods=['POST'])
def send_message():
    """
    THAY ĐỔI NHỎ: Update error handling cho AI analysis
    Send message endpoint with enhanced error handling
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'success': False
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'success': False
            }), 400
        
        # Extract required fields
        message = data.get('message', '').strip()
        history = data.get('history', [])
        state = data.get('state', {})
        use_ai = data.get('use_ai', True)
        
        # Validate input
        if not validate_message(message):
            return jsonify({
                'error': 'Invalid message format or content',
                'success': False
            }), 400
        
        if not validate_chat_state(state):
            return jsonify({
                'error': 'Invalid chat state format',
                'success': False
            }), 400
        
        # Initialize default state if empty
        if not state:
            state = {
                'current_phase': 'chat',
                'message_count': 0,
                'session_id': session.get('session_id', 'default'),
                'language': 'vi',
                'created_at': datetime.now().isoformat(),
                'ai_analysis_count': 0,
                'fallback_mode': False
            }
        
        # Check if chat engine is available
        if not chat_engine:
            logger.error("Chat engine not initialized")
            return jsonify({
                'error': 'Chat engine not available',
                'success': False,
                'fallback_available': True
            }), 503
        
        # NEW: Handle AI service timeout
        try:
            # Process message with timeout handling
            result = process_message_with_timeout(
                message=message,
                history=history,
                state=state,
                use_ai=use_ai and ai_analyzer_initialized,
                timeout_seconds=30
            )
            
        except TimeoutError:
            logger.warning("AI analysis timeout - falling back to basic mode")
            state['fallback_mode'] = True
            result = chat_engine.process_message(
                message=message,
                history=history,
                state=state,
                use_ai=False  # Force fallback mode
            )
        
        except Exception as ai_error:
            logger.error(f"AI analysis error: {ai_error}")
            # NEW: Fallback to old logic nếu AI service down
            state['fallback_mode'] = True
            state['last_error'] = str(ai_error)
            
            try:
                result = chat_engine.process_message(
                    message=message,
                    history=history,
                    state=state,
                    use_ai=False  # Disable AI on error
                )
                
                # Add warning to response
                result['warning'] = "AI analysis unavailable - using basic mode"
                
            except Exception as fallback_error:
                logger.error(f"Fallback processing also failed: {fallback_error}")
                return jsonify({
                    'error': 'Both AI and fallback processing failed',
                    'success': False,
                    'details': {
                        'ai_error': str(ai_error),
                        'fallback_error': str(fallback_error)
                    }
                }), 500
        
        # Validate result
        if not result or 'message' not in result:
            logger.error("Invalid result from chat engine")
            return jsonify({
                'error': 'Invalid response from chat engine',
                'success': False
            }), 500
        
        # NEW: Add metadata về AI usage
        response_data = {
            'message': result['message'],
            'history': result.get('history', history),
            'state': result.get('state', state),
            'metadata': result.get('metadata', {}),
            'success': True
        }
        
        # Add AI-specific metadata
        response_data['ai_info'] = {
            'ai_analyzer_available': ai_analyzer_initialized,
            'ai_used': result.get('metadata', {}).get('ai_used', False),
            'fallback_mode': state.get('fallback_mode', False),
            'ai_severity': result.get('metadata', {}).get('ai_severity', 0.0)
        }
        
        # Add warning if in fallback mode
        if state.get('fallback_mode'):
            response_data['warning'] = 'Using fallback mode due to AI service issues'
        
        # Log successful processing
        logger.info(f"Message processed successfully: AI={response_data['ai_info']['ai_used']}, "
                   f"Fallback={response_data['ai_info']['fallback_mode']}")
        
        return jsonify(response_data)
        
    except Exception as e:
        # Comprehensive error handling
        error_details = {
            'error': 'Internal server error during message processing',
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc() if logger.level == logging.DEBUG else None
        }
        
        logger.error(f"Unhandled error in send_message: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify(error_details), 500

def process_message_with_timeout(message: str, history: List[Dict], state: Dict, use_ai: bool, timeout_seconds: int = 30) -> Dict:
    """
    NEW: Process message với timeout handling
    """
    import signal
    import threading
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
    
    def process_message_worker():
        """Worker function to process message"""
        return chat_engine.process_message(
            message=message,
            history=history,
            state=state,
            use_ai=use_ai
        )
    
    # Use ThreadPoolExecutor for timeout handling
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(process_message_worker)
        try:
            result = future.result(timeout=timeout_seconds)
            return result
        except FutureTimeoutError:
            logger.warning(f"Message processing timeout after {timeout_seconds} seconds")
            raise TimeoutError(f"Processing timeout after {timeout_seconds} seconds")

@chat_bp.route('/get_followup', methods=['POST'])
def get_followup():
    """
    NEW: Get smart followup question endpoint
    """
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'success': False
            }), 400
        
        data = request.get_json()
        history = data.get('history', [])
        
        if not history:
            return jsonify({
                'error': 'History is required',
                'success': False
            }), 400
        
        if not chat_engine:
            return jsonify({
                'error': 'Chat engine not available',
                'success': False
            }), 503
        
        # Generate followup question
        try:
            followup = chat_engine.transition_manager.generate_followup_question(history)
            
            return jsonify({
                'followup_question': followup,
                'success': True,
                'ai_generated': ai_analyzer_initialized
            })
            
        except Exception as e:
            logger.error(f"Error generating followup: {e}")
            
            # Fallback followup questions
            fallback_questions = [
                "Bạn có thể chia sẻ thêm với tôi không?",
                "Hãy cho tôi biết thêm về cảm giác của bạn.",
                "Điều gì khiến bạn cảm thấy như vậy?",
                "Bạn có muốn nói thêm về vấn đề này không?"
            ]
            
            import random
            fallback = random.choice(fallback_questions)
            
            return jsonify({
                'followup_question': fallback,
                'success': True,
                'ai_generated': False,
                'warning': 'Using fallback followup question'
            })
            
    except Exception as e:
        logger.error(f"Error in get_followup: {e}")
        return jsonify({
            'error': 'Failed to generate followup question',
            'success': False
        }), 500

@chat_bp.route('/check_transition', methods=['POST'])
def check_transition():
    """
    NEW: Explicitly check if should transition to assessment
    """
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'success': False
            }), 400
        
        data = request.get_json()
        history = data.get('history', [])
        state = data.get('state', {})
        
        if not history:
            return jsonify({
                'error': 'History is required',
                'success': False
            }), 400
        
        if not chat_engine:
            return jsonify({
                'error': 'Chat engine not available',
                'success': False
            }), 503
        
        # Check transition
        try:
            should_transition, assessment_type, reason = chat_engine.transition_manager.should_transition(
                history, state
            )
            
            return jsonify({
                'should_transition': should_transition,
                'assessment_type': assessment_type,
                'reason': reason,
                'success': True,
                'ai_powered': ai_analyzer_initialized
            })
            
        except Exception as e:
            logger.error(f"Error checking transition: {e}")
            return jsonify({
                'should_transition': False,
                'assessment_type': '',
                'reason': f'Transition check failed: {str(e)}',
                'success': False
            })
            
    except Exception as e:
        logger.error(f"Error in check_transition: {e}")
        return jsonify({
            'error': 'Failed to check transition status',
            'success': False
        }), 500

@chat_bp.route('/conversation_summary', methods=['POST'])
def get_conversation_summary():
    """
    NEW: Get conversation analysis summary
    """
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'success': False
            }), 400
        
        data = request.get_json()
        history = data.get('history', [])
        
        if not history:
            return jsonify({
                'error': 'History is required',
                'success': False
            }), 400
        
        if not chat_engine:
            return jsonify({
                'error': 'Chat engine not available',
                'success': False
            }), 503
        
        # Get conversation summary
        try:
            summary = chat_engine.get_conversation_summary(history)
            
            return jsonify({
                'summary': summary,
                'success': True,
                'ai_powered': ai_analyzer_initialized
            })
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            
            # Basic fallback summary
            user_messages = [msg for msg in history if msg.get('role') == 'user']
            fallback_summary = {
                'message_count': len(user_messages),
                'avg_message_length': sum(len(msg['content']) for msg in user_messages) / len(user_messages) if user_messages else 0,
                'summary': f'Basic conversation with {len(user_messages)} user messages'
            }
            
            return jsonify({
                'summary': fallback_summary,
                'success': True,
                'ai_powered': False,
                'warning': 'Using basic summary due to analysis error'
            })
            
    except Exception as e:
        logger.error(f"Error in get_conversation_summary: {e}")
        return jsonify({
            'error': 'Failed to get conversation summary',
            'success': False
        }), 500

@chat_bp.route('/health', methods=['GET'])
def health_check():
    """
    NEW: Health check endpoint
    """
    try:
        health_status = {
            'chat_engine_available': chat_engine is not None,
            'ai_analyzer_available': ai_analyzer_initialized,
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy'
        }
        
        # Test basic functionality if possible
        if chat_engine:
            try:
                # Quick test
                test_result = chat_engine.get_conversation_summary([])
                health_status['chat_engine_test'] = 'passed'
            except:
                health_status['chat_engine_test'] = 'failed'
                health_status['status'] = 'degraded'
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Error handlers
@chat_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'success': False
    }), 404

@chat_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed',
        'success': False
    }), 405

@chat_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'success': False
    }), 500

# Initialize services when blueprint is registered
def init_services():
    """Initialize services during app startup"""
    if not initialize_chat_services():
        logger.error("Failed to initialize chat services during app startup")

# Register initialization function with Flask app
def register_init_services(app):
    """Register initialization services with the Flask app"""
    with app.app_context():
        init_services()