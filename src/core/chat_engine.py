"""
Chat Engine - Core conversation management with improved transition logic
Solves the main issue of unreliable chat-to-poll transitions
"""

import logging
import json
import re
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
        self.thresholds = getattr(Config, 'TRANSITION_THRESHOLDS', {
            'depression_score': 0.6,
            'anxiety_score': 0.6,
            'stress_score': 0.6,
            'suicide_risk_score': 0.3
        })
        
        # Keywords for category scoring
        self.category_keywords = {
            'depression': [
                'buồn', 'chán nản', 'tuyệt vọng', 'không vui', 'trầm cảm', 
                'mệt mỏi', 'không muốn', 'thất vọng', 'cô đơn', 'trống rỗng',
                'sad', 'depressed', 'hopeless', 'empty', 'tired', 'worthless'
            ],
            'anxiety': [
                'lo lắng', 'căng thẳng', 'bồn chồn', 'sợ hãi', 'hoảng loạn',
                'tim đập nhanh', 'khó thở', 'run rẩy', 'không yên', 'lo âu',
                'anxious', 'worried', 'nervous', 'panic', 'restless', 'scared'
            ],
            'stress': [
                'stress', 'áp lực', 'quá tải', 'kiệt sức', 'không thể chịu đựng',
                'overwhelmed', 'pressure', 'exhausted', 'burned out', 'overloaded'
            ],
            'suicide_risk': [
                'chết', 'tự tử', 'kết thúc', 'không muốn sống', 'biến mất',
                'làm hại bản thân', 'suicide', 'kill myself', 'end it all', 
                'don\'t want to live', 'hurt myself', 'die'
            ]
        }
    
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
            
            category_scores = self._calculate_category_scores(history, state)
            state['scores'] = category_scores
            
            # Check if any category score exceeds threshold
            for category, score in category_scores.items():
                threshold = self.thresholds.get(f"{category}_score", 0.6)
                if score >= threshold:
                    assessment_type = self._map_category_to_assessment(category)
                    return True, assessment_type, f"high_{category}_score"
        
        return False, None, "continue_chat"
    
    def _calculate_category_scores(self, history: List[Dict], state: Dict) -> Dict[str, float]:
        """
        Calculate emotional category scores based on conversation content
        
        Args:
            history: Conversation history
            state: Current chat state
            
        Returns:
            Dictionary of category scores (0.0 to 1.0)
        """
        # Combine all user messages
        user_messages = [msg['content'].lower() for msg in history if msg.get('role') == 'user']
        all_text = ' '.join(user_messages)
        
        scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0.0
            total_keywords = len(keywords)
            
            # Count keyword matches
            matched_keywords = 0
            for keyword in keywords:
                if keyword.lower() in all_text:
                    matched_keywords += 1
            
            # Base score from keyword frequency
            if total_keywords > 0:
                score = matched_keywords / total_keywords
            
            # Apply message frequency weighting
            message_weight = min(len(user_messages) / Config.MIN_MESSAGES_BEFORE_TRANSITION, 1.0)
            score *= message_weight
            
            # Apply intensity multiplier for repeated mentions
            intensity_multiplier = self._calculate_intensity_multiplier(all_text, keywords)
            score *= intensity_multiplier
            
            # Ensure score is between 0 and 1
            scores[category] = min(max(score, 0.0), 1.0)
        
        # Store additional metadata
        scores['_metadata'] = {
            'message_count': len(user_messages),
            'total_words': len(all_text.split()),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return scores
    
    def _calculate_intensity_multiplier(self, text: str, keywords: List[str]) -> float:
        """Calculate intensity multiplier based on keyword repetition and context"""
        total_mentions = 0
        for keyword in keywords:
            total_mentions += text.count(keyword.lower())
        
        # More mentions = higher intensity (capped at 2.0)
        if total_mentions == 0:
            return 0.0
        elif total_mentions == 1:
            return 1.0
        elif total_mentions <= 3:
            return 1.3
        elif total_mentions <= 5:
            return 1.6
        else:
            return 2.0
    
    def _has_suicide_risk(self, history: List[Dict], state: Dict) -> bool:
        """Check for immediate suicide risk indicators"""
        user_messages = [msg['content'].lower() for msg in history if msg.get('role') == 'user']
        all_text = ' '.join(user_messages)
        
        high_risk_keywords = [
            'tự tử', 'chết', 'kết thúc cuộc đời', 'không muốn sống nữa',
            'suicide', 'kill myself', 'end my life', 'want to die'
        ]
        
        for keyword in high_risk_keywords:
            if keyword in all_text:
                return True
        
        return False
    
    def _select_best_assessment(self, scores: Dict) -> str:
        """Select the most appropriate assessment based on scores"""
        if not scores:
            return AssessmentTypes.PHQ9  # Default to depression screening
        
        # Remove metadata if present
        clean_scores = {k: v for k, v in scores.items() if not k.startswith('_')}
        
        if not clean_scores:
            return AssessmentTypes.PHQ9
        
        # Find highest scoring category
        max_category = max(clean_scores, key=clean_scores.get)
        return self._map_category_to_assessment(max_category)
    
    def _map_category_to_assessment(self, category: str) -> str:
        """Map emotional category to appropriate assessment type"""
        mapping = {
            'depression': AssessmentTypes.PHQ9,
            'anxiety': AssessmentTypes.GAD7,
            'stress': AssessmentTypes.DASS21_STRESS,
            'suicide_risk': AssessmentTypes.SUICIDE_RISK
        }
        return mapping.get(category, AssessmentTypes.PHQ9)


class ChatEngine:
    """Enhanced chat engine with improved AI integration and transition logic"""
    
    def __init__(self):
        self.transition_manager = TransitionManager()
        self.assessment_engine = AssessmentEngine()
        
        # Fallback responses for when AI is unavailable
        self.fallback_responses = {
            'welcome': "Xin chào! Tôi ở đây để lắng nghe và hỗ trợ bạn. Hãy chia sẻ với tôi cảm giác của bạn gần đây.",
            'encouragement': "Cảm ơn bạn đã chia sẻ. Bạn có thể kể thêm về điều gì khiến bạn cảm thấy như vậy không?",
            'understanding': "Tôi hiểu. Điều này nghe có vẻ khó khăn với bạn. Bạn có muốn nói thêm về cảm giác này không?",
            'transition': "Cảm ơn bạn đã tin tường chia sẻ. Để hiểu rõ hơn tình trạng của bạn, tôi muốn đặt một số câu hỏi cụ thể. Bạn có sẵn sàng không?"
        }
    
    def process_message(self, message: str, history: List[Dict], state: Dict, use_ai: bool = True) -> Dict:
        """
        Process user message and generate appropriate response
        
        Args:
            message: User's message
            history: Conversation history
            state: Current session state
            use_ai: Whether to use AI for response generation
            
        Returns:
            Response dictionary with message, updated state, and metadata
        """
        try:
            # Update state
            state['message_count'] = state.get('message_count', 0) + 1
            state['last_message_time'] = datetime.now().isoformat()
            
            # Add user message to history
            updated_history = history + [{'role': 'user', 'content': message}]
            
            # Check if we should transition to assessment
            should_transition, assessment_type, reason = self.transition_manager.should_transition(
                updated_history, state
            )
            
            if should_transition:
                return self._handle_transition(assessment_type, reason, state, updated_history)
            
            # Generate chat response
            if use_ai:
                bot_response = self._generate_ai_response(message, updated_history, state)
            else:
                bot_response = self._generate_fallback_response(message, updated_history, state)
            
            # Add bot response to history
            final_history = updated_history + [{'role': 'bot', 'content': bot_response}]
            
            return {
                'message': bot_response,
                'history': final_history,
                'state': state,
                'metadata': {
                    'type': 'chat_response',
                    'phase': 'chat',
                    'ai_used': use_ai,
                    'message_count': state['message_count'],
                    'scores': state.get('scores', {})
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._generate_error_response(history, state)
    
    def _generate_ai_response(self, message: str, history: List[Dict], state: Dict) -> str:
        """Generate response using AI"""
        try:
            # Create context-aware system prompt
            system_prompt = self._create_system_prompt(state)
            
            # Prepare messages for AI
            ai_messages = [{'role': 'system', 'content': system_prompt}]
            
            # Add relevant conversation history (last 6 messages to stay within context limits)
            recent_history = history[-6:] if len(history) > 6 else history
            ai_messages.extend(recent_history)
            
            # Generate response
            response = generate_chat_completion(
                messages=ai_messages,
                max_tokens=150,
                temperature=0.7
            )
            
            if response:
                return extract_text_from_response(response)
            else:
                return self._generate_fallback_response(message, history, state)
                
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return self._generate_fallback_response(message, history, state)
    
    def _create_system_prompt(self, state: Dict) -> str:
        """Create context-aware system prompt for AI"""
        base_prompt = """Bạn là một trợ lý sức khỏe tâm thần chuyên nghiệp và đầy empathy. 
Hãy:
- Lắng nghe một cách chân thành và không phán xét
- Đặt câu hỏi mở để khuyến khích chia sẻ
- Thể hiện sự đồng cảm và hiểu biết
- Giữ câu trả lời ngắn gọn (1-2 câu)
- Không đưa ra chẩn đoán y tế
- Tập trung vào cảm xúc và trải nghiệm của người dùng"""
        
        # Add context based on current scores
        scores = state.get('scores', {})
        if scores:
            context = "\nDựa trên cuộc trò chuyện, có vẻ người dùng đang trải qua:"
            for category, score in scores.items():
                if not category.startswith('_') and score > 0.4:
                    context += f"\n- {category}: mức độ {score:.1f}"
            base_prompt += context
        
        return base_prompt
    
    def _generate_fallback_response(self, message: str, history: List[Dict], state: Dict) -> str:
        """Generate fallback response when AI is unavailable"""
        message_count = len(history)
        
        if message_count <= 1:
            return self.fallback_responses['welcome']
        elif message_count <= 3:
            return self.fallback_responses['encouragement']
        elif message_count <= 6:
            return self.fallback_responses['understanding']
        else:
            return self.fallback_responses['transition']
    
    def _handle_transition(self, assessment_type: str, reason: str, state: Dict, history: List[Dict]) -> Dict:
        """Handle transition from chat to assessment"""
        state['current_phase'] = 'assessment'
        state['assessment_type'] = assessment_type
        state['transition_reason'] = reason
        
        transition_message = self._generate_transition_message(assessment_type, reason)
        
        # Start assessment
        assessment_data = self.assessment_engine.start_assessment(assessment_type, state)
        
        return {
            'message': transition_message,
            'history': history + [{'role': 'bot', 'content': transition_message}],
            'state': state,
            'assessment': assessment_data,
            'metadata': {
                'type': 'transition',
                'phase': 'transition',
                'assessment_type': assessment_type,
                'reason': reason,
                'should_show_poll': True
            }
        }
    
    def _generate_transition_message(self, assessment_type: str, reason: str) -> str:
        """Generate appropriate transition message"""
        messages = {
            AssessmentTypes.PHQ9: "Cảm ơn bạn đã chia sẻ. Để hiểu rõ hơn về tâm trạng của bạn, tôi muốn đặt một số câu hỏi về trầm cảm.",
            AssessmentTypes.GAD7: "Tôi nhận thấy bạn có vẻ đang lo lắng. Hãy cùng đánh giá mức độ lo âu qua một số câu hỏi.",
            AssessmentTypes.DASS21_STRESS: "Có vẻ bạn đang trải qua căng thẳng. Tôi muốn đánh giá mức độ stress của bạn.",
            AssessmentTypes.SUICIDE_RISK: "Tôi quan tâm đến sự an toàn của bạn. Hãy để tôi đặt một số câu hỏi quan trọng."
        }
        
        return messages.get(assessment_type, 
            "Cảm ơn bạn đã chia sẻ. Bây giờ tôi muốn đánh giá chi tiết hơn qua một số câu hỏi cụ thể.")
    
    def _generate_error_response(self, history: List[Dict], state: Dict) -> Dict:
        """Generate error response when something goes wrong"""
        error_message = "Xin lỗi, tôi gặp chút khó khăn. Bạn có thể thử lại không?"
        
        return {
            'message': error_message,
            'history': history + [{'role': 'bot', 'content': error_message}],
            'state': state,
            'metadata': {
                'type': 'error',
                'phase': 'chat'
            }
        }
    
    def reset_conversation(self, state: Dict) -> Dict:
        """Reset conversation to initial state"""
        new_state = {
            'session_id': state.get('session_id'),
            'current_phase': 'chat',
            'language': state.get('language', 'vi'),
            'message_count': 0,
            'scores': {},
            'started_at': datetime.now().isoformat()
        }
        
        welcome_message = self.fallback_responses['welcome']
        
        return {
            'message': welcome_message,
            'history': [{'role': 'bot', 'content': welcome_message}],
            'state': new_state,
            'metadata': {
                'type': 'reset',
                'phase': 'chat'
            }
        }