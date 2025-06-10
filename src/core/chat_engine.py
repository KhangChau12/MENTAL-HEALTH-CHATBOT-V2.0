"""
Chat Engine - Core conversation management with improved transition logic
Solves the main issue of unreliable chat-to-poll transitions
"""

import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..services.together_ai import generate_chat_completion, extract_text_from_response
from .ai_classifier import AIClassifier
from .assessment_engine import AssessmentEngine
from ..utils.validators import validate_message, validate_chat_state
from ..utils.constants import ChatStates, AssessmentTypes
from config import Config

logger = logging.getLogger(__name__)

class TransitionManager:
    """Manages transitions from chat to assessment"""
    
    def __init__(self):
        self.classifier = AIClassifier()
        self.assessment_engine = AssessmentEngine()
        self.thresholds = Config.TRANSITION_THRESHOLDS
    
    def should_transition(self, history: List[Dict], state: Dict) -> Tuple[bool, Optional[str], str]:
        """
        Determine if conversation should transition to assessment
        
        Args:
            history: Conversation history
            state: Current chat state
            
        Returns:
            (should_transition, assessment_type, reason)
        """
        message_count = len(history)
        
        # Rule 1: Force transition after max messages
        if message_count >= Config.MAX_CONVERSATION_LENGTH:
            assessment_type = self._select_best_assessment(state.get('scores', {}))
            return True, assessment_type, "max_messages_reached"
        
        # Rule 2: Check for suicide risk (immediate transition)
        if self._has_suicide_risk(history, state):
            return True, AssessmentTypes.SUICIDE_RISK, "suicide_risk_detected"
        
        # Rule 3: Periodic evaluation after minimum messages
        if (message_count >= Config.MIN_MESSAGES_BEFORE_TRANSITION and 
            message_count % Config.TRANSITION_CHECK_INTERVAL == 0):
            
            category_scores = self._calculate_category_scores(state.get('scores', {}))
            assessment_type = self._check_threshold_transition(category_scores)
            
            if assessment_type:
                return True, assessment_type, "threshold_met"
        
        return False, None, "continue_conversation"
    
    def _has_suicide_risk(self, history: List[Dict], state: Dict) -> bool:
        """Check for suicide risk indicators"""
        scores = state.get('scores', {})
        
        # Check for explicit suicide-related scores
        suicide_indicators = ['life_not_worth', 'death_thoughts', 'self_harm']
        for indicator in suicide_indicators:
            if scores.get(indicator, 0) >= 3:
                return True
        
        # Check recent messages for urgent keywords
        recent_messages = history[-3:] if len(history) >= 3 else history
        urgent_keywords = [
            'tự tử', 'chết', 'kết thúc cuộc đời', 'không muốn sống',
            'suicide', 'kill myself', 'end my life', 'want to die'
        ]
        
        for msg in recent_messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '').lower()
                if any(keyword in content for keyword in urgent_keywords):
                    return True
        
        return False
    
    def _calculate_category_scores(self, scores: Dict) -> Dict[str, float]:
        """Calculate aggregated scores by category"""
        category_mapping = {
            'depression': ['sad_feelings', 'lost_interest', 'worthless', 'tired', 'concentration'],
            'anxiety': ['worried', 'anxious', 'restless', 'panic', 'nervous'],
            'stress': ['overwhelmed', 'pressure', 'irritable', 'tense', 'racing_thoughts']
        }
        
        category_scores = {}
        for category, question_ids in category_mapping.items():
            relevant_scores = [scores.get(qid, 0) for qid in question_ids if qid in scores]
            if relevant_scores:
                category_scores[category] = sum(relevant_scores) / len(relevant_scores)
            else:
                category_scores[category] = 0
        
        return category_scores
    
    def _check_threshold_transition(self, category_scores: Dict[str, float]) -> Optional[str]:
        """Check if any category meets transition threshold"""
        assessment_mapping = {
            'depression': AssessmentTypes.PHQ9,
            'anxiety': AssessmentTypes.GAD7,
            'stress': AssessmentTypes.DASS21_STRESS
        }
        
        # Find highest scoring category that meets threshold
        eligible_categories = []
        for category, score in category_scores.items():
            if score >= self.thresholds.get(category, 3):
                eligible_categories.append((category, score))
        
        if eligible_categories:
            # Return assessment type for highest scoring category
            best_category = max(eligible_categories, key=lambda x: x[1])[0]
            return assessment_mapping.get(best_category, AssessmentTypes.PHQ9)
        
        return None
    
    def _select_best_assessment(self, scores: Dict) -> str:
        """Select most appropriate assessment when forced to transition"""
        category_scores = self._calculate_category_scores(scores)
        
        if not category_scores or all(score == 0 for score in category_scores.values()):
            return AssessmentTypes.PHQ9  # Default
        
        # Return assessment for highest scoring category
        best_category = max(category_scores.items(), key=lambda x: x[1])[0]
        assessment_mapping = {
            'depression': AssessmentTypes.PHQ9,
            'anxiety': AssessmentTypes.GAD7,
            'stress': AssessmentTypes.DASS21_STRESS
        }
        
        return assessment_mapping.get(best_category, AssessmentTypes.PHQ9)

class ChatEngine:
    """Main chat engine with improved conversation management"""
    
    def __init__(self):
        self.transition_manager = TransitionManager()
        self.classifier = AIClassifier()
        self.assessment_engine = AssessmentEngine()
        
    def process_message(self, message: str, history: List[Dict], state: Dict, use_ai: bool = True) -> Dict:
        """
        Process user message and return response
        
        Args:
            message: User's message
            history: Conversation history
            state: Current chat state
            use_ai: Whether to use AI for response generation
            
        Returns:
            Response dictionary with message, new_state, and metadata
        """
        try:
            # Validate inputs
            if not validate_message(message):
                return self._create_error_response("Invalid message")
            
            if not validate_chat_state(state):
                state = self._initialize_default_state()
            
            # Add user message to history
            updated_history = history + [{
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            }]
            
            # Check for transition
            should_transition, assessment_type, reason = self.transition_manager.should_transition(
                updated_history, state
            )
            
            if should_transition:
                return self._handle_transition(assessment_type, reason, updated_history, state)
            
            # Continue conversation
            return self._continue_conversation(message, updated_history, state, use_ai)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._create_error_response("Đã xảy ra lỗi khi xử lý tin nhắn của bạn")
    
    def _handle_transition(self, assessment_type: str, reason: str, history: List[Dict], state: Dict) -> Dict:
        """Handle transition from chat to assessment"""
        logger.info(f"Transitioning to {assessment_type}, reason: {reason}")
        
        # Generate appropriate transition message
        transition_messages = {
            "max_messages_reached": "Cảm ơn bạn đã chia sẻ nhiều thông tin. Bây giờ tôi muốn đánh giá chi tiết hơn thông qua một số câu hỏi cụ thể.",
            "threshold_met": "Dựa trên những gì bạn chia sẻ, tôi nghĩ chúng ta nên đánh giá chi tiết hơn. Tôi sẽ hỏi bạn một số câu hỏi cụ thể.",
            "suicide_risk_detected": "Tôi rất quan tâm đến những gì bạn chia sẻ. Để hỗ trợ bạn tốt nhất, tôi cần đánh giá tình hình ngay."
        }
        
        transition_message = transition_messages.get(reason, "Chúng ta hãy chuyển sang đánh giá chi tiết hơn.")
        
        # Update state for assessment mode
        new_state = {
            **state,
            'current_phase': 'assessment',
            'assessment_type': assessment_type,
            'conversation_summary': self._summarize_conversation(history),
            'transition_reason': reason,
            'assessment_started_at': datetime.now().isoformat()
        }
        
        # Start assessment
        assessment_response = self.assessment_engine.start_assessment(assessment_type, new_state)
        
        # Combine transition message with first assessment question
        combined_message = f"{transition_message}\n\n{assessment_response['message']}"
        
        return {
            'message': combined_message,
            'state': assessment_response['state'],
            'metadata': {
                'type': 'transition',
                'assessment_type': assessment_type,
                'reason': reason,
                'phase': 'assessment'
            }
        }
    
    def _continue_conversation(self, message: str, history: List[Dict], state: Dict, use_ai: bool) -> Dict:
        """Continue natural conversation"""
        
        # Update scores based on conversation
        self._update_conversation_scores(message, history, state)
        
        # Generate response
        if use_ai:
            response_text = self._generate_ai_response(message, history, state)
        else:
            response_text = self._generate_fallback_response(message, state)
        
        # Update state
        new_state = {
            **state,
            'message_count': len(history),
            'last_updated': datetime.now().isoformat()
        }
        
        return {
            'message': response_text,
            'state': new_state,
            'metadata': {
                'type': 'conversation',
                'phase': 'chat',
                'message_count': len(history)
            }
        }
    
    def _update_conversation_scores(self, message: str, history: List[Dict], state: Dict):
        """Update conversation scores based on latest message"""
        try:
            # Use AI classifier to score the message
            scores = self.classifier.classify_conversation_segment(message, history[-5:])
            
            # Update state scores
            current_scores = state.get('scores', {})
            for question_id, score in scores.items():
                current_scores[question_id] = max(current_scores.get(question_id, 0), score)
            
            state['scores'] = current_scores
            
        except Exception as e:
            logger.error(f"Error updating conversation scores: {e}")
    
    def _generate_ai_response(self, message: str, history: List[Dict], state: Dict) -> str:
        """Generate AI response using Together AI"""
        try:
            # Create context-appropriate prompt
            system_prompt = self._create_system_prompt(state)
            
            # Prepare messages for AI
            messages = []
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            # Add recent conversation history (last 10 messages)
            recent_history = history[-10:] if len(history) > 10 else history
            for msg in recent_history:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
            
            # Generate response
            response = generate_chat_completion(messages)
            if response:
                return extract_text_from_response(response)
            else:
                return self._generate_fallback_response(message, state)
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._generate_fallback_response(message, state)
    
    def _create_system_prompt(self, state: Dict) -> str:
        """Create appropriate system prompt based on conversation state"""
        return """Bạn là một chuyên gia tâm lý học với nhiều năm kinh nghiệm tư vấn. 
        
Nhiệm vụ của bạn:
- Lắng nghe và thấu hiểu những khó khăn của người dùng
- Đặt câu hỏi nhẹ nhàng để hiểu rõ hơn về tình trạng tâm lý
- Thể hiện sự đồng cảm và quan tâm chân thành
- Tránh đưa ra chẩn đoán y tế hoặc lời khuyên điều trị cụ thể

Phong cách giao tiếp:
- Ấm áp, thân thiện nhưng chuyên nghiệp
- Sử dụng ngôn ngữ đơn giản, dễ hiểu
- Đặt một câu hỏi nhẹ nhàng ở cuối để khuyến khích chia sẻ
- Phản hồi ngắn gọn (2-3 câu)

Lưu ý quan trọng:
- Luôn khuyến khích người dùng tìm kiếm sự hỗ trợ từ chuyên gia khi cần thiết
- Nếu phát hiện dấu hiệu nghiêm trọng, thể hiện sự quan tâm và khuyến khích tìm kiếm giúp đỡ ngay lập tức"""
    
    def _generate_fallback_response(self, message: str, state: Dict) -> str:
        """Generate fallback response when AI is unavailable"""
        fallback_responses = [
            "Cảm ơn bạn đã chia sẻ. Tôi hiểu điều này không dễ dàng gì. Bạn có thể kể thêm về cảm giác của mình không?",
            "Tôi có thể cảm nhận được những khó khăn bạn đang trải qua. Những điều này ảnh hưởng như thế nào đến cuộc sống hàng ngày của bạn?",
            "Cảm ơn bạn đã tin tưởng chia sẻ với tôi. Tình trạng này đã kéo dài trong bao lâu rồi?",
            "Tôi hiểu cảm giác của bạn. Có điều gì đã thay đổi gần đây trong cuộc sống khiến bạn cảm thấy như vậy không?"
        ]
        
        import random
        return random.choice(fallback_responses)
    
    def _summarize_conversation(self, history: List[Dict]) -> str:
        """Create a brief summary of the conversation"""
        user_messages = [msg['content'] for msg in history if msg.get('role') == 'user']
        if not user_messages:
            return "Người dùng chưa chia sẻ thông tin cụ thể."
        
        # Simple summarization - can be enhanced with AI
        key_points = []
        if len(user_messages) > 0:
            key_points.append(f"Đã trao đổi {len(user_messages)} tin nhắn")
        
        return "; ".join(key_points) if key_points else "Cuộc trò chuyện sơ bộ"
    
    def _initialize_default_state(self) -> Dict:
        """Initialize default chat state"""
        return {
            'session_id': None,
            'current_phase': 'chat',
            'scores': {},
            'message_count': 0,
            'started_at': datetime.now().isoformat(),
            'language': 'vi'
        }
    
    def _create_error_response(self, error_message: str) -> Dict:
        """Create error response"""
        return {
            'message': error_message,
            'state': {},
            'metadata': {
                'type': 'error',
                'error': True
            }
        }