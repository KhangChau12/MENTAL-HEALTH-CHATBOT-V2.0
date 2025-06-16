"""
Chat Engine - SỬA ĐỔI để tích hợp transition logic mới
Updated to use AI-powered transition logic
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.services.together_client import get_together_client
from src.core.transition_logic import TransitionManager
from src.services.ai_context_analyzer import classify_emotional_context

logger = logging.getLogger(__name__)

class ChatEngine:
    """Main chat engine với AI-powered transition logic"""
    
    def __init__(self):
        self.client = get_together_client()
        self.transition_manager = TransitionManager()
        
        # Template responses
        self.templates = {
            'greeting': "Xin chào! Tôi ở đây để lắng nghe và hỗ trợ bạn. Hãy chia sẻ với tôi cảm giác của bạn gần đây.",
            'encouragement': "Cảm ơn bạn đã chia sẻ. Bạn có thể kể thêm về điều gì khiến bạn cảm thấy như vậy không?",
            'understanding': "Tôi hiểu. Điều này nghe có vẻ khó khăn với bạn. Bạn có muốn nói thêm về cảm giác này không?",
            'transition': "Cảm ơn bạn đã tin tưởng chia sẻ. Để hiểu rõ hơn tình trạng của bạn, tôi muốn đặt một số câu hỏi cụ thể. Bạn có sẵn sàng không?"
        }
    
    def process_message(self, message: str, history: List[Dict], state: Dict, use_ai: bool = True) -> Dict:
        """
        THAY ĐỔI: Sử dụng transition logic mới
        
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
            
            # NEW: Check if we should use AI analysis
            should_use_ai = self.should_use_ai_analysis(state['message_count'], state)
            
            # NEW: AI context analysis for response generation
            ai_context = None
            if should_use_ai and use_ai:
                try:
                    ai_context = classify_emotional_context(message, updated_history)
                    state['last_ai_analysis'] = ai_context
                    state['last_ai_analysis_time'] = datetime.now().isoformat()
                except Exception as e:
                    logger.warning(f"AI context analysis failed: {e}")
            
            # THAY ĐỔI: Sử dụng transition logic mới
            should_transition, assessment_type, reason = self.transition_manager.should_transition(
                updated_history, state
            )
            
            if should_transition:
                return self._handle_transition(assessment_type, reason, state, updated_history, ai_context)
            
            # Generate chat response
            if use_ai:
                bot_response = self._generate_ai_response(message, updated_history, state, ai_context)
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
                    'ai_context_available': ai_context is not None,
                    'message_count': state['message_count'],
                    'transition_checked': True,
                    'ai_severity': ai_context.get('severity', 0.0) if ai_context else 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._generate_error_response(history, state)

    def should_use_ai_analysis(self, message_count: int, state: Dict) -> bool:
        """
        THÊM MỚI: Quyết định khi nào dùng AI analysis
        
        Params:
            - message_count: Số tin nhắn trong conversation
            - state: Current state
        
        Return: True nếu nên dùng AI
        """
        # Dùng AI sau message thứ 3 (tránh overuse)
        if message_count < 3:
            return False
        
        # Skip nếu đã có recent analysis (trong vòng 2 messages)
        last_analysis_time = state.get('last_ai_analysis_time')
        if last_analysis_time:
            try:
                from datetime import datetime, timedelta
                last_time = datetime.fromisoformat(last_analysis_time)
                if datetime.now() - last_time < timedelta(minutes=1):
                    return False
            except:
                pass  # Ignore parsing errors
        
        # Always use nếu detect potential clinical signs trong state
        if state.get('potential_clinical_signs', False):
            return True
        
        # Use mỗi 2-3 messages
        return message_count % 2 == 0

    def _generate_ai_response(self, message: str, history: List[Dict], state: Dict, ai_context: Optional[Dict] = None) -> str:
        """
        THAY ĐỔI: Tích hợp AI context analysis
        Generate response using AI with context awareness
        """
        try:
            # Create context-aware system prompt
            system_prompt = self._create_system_prompt(state, ai_context)
            
            # Prepare conversation context (last 6 messages)
            recent_history = history[-6:] if len(history) > 6 else history
            
            # Convert to API format
            messages = [{"role": "system", "content": system_prompt}]
            
            for msg in recent_history:
                role = "user" if msg['role'] == 'user' else "assistant"
                messages.append({"role": role, "content": msg['content']})
            
            # Generate response
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # NEW: Add follow-up question if needed
            if ai_context and ai_context.get('needs_followup', False):
                followup = self.transition_manager.generate_followup_question(history)
                if followup and followup not in ai_response:
                    ai_response += f" {followup}"
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._generate_fallback_response(message, history, state)

    def _create_system_prompt(self, state: Dict, ai_context: Optional[Dict] = None) -> str:
        """Create context-aware system prompt"""
        base_prompt = """Bạn là một chatbot hỗ trợ sức khỏe tâm thần, luôn thể hiện sự đồng cảm và chuyên nghiệp.

NHIỆM VỤ:
- Lắng nghe và thấu hiểu người dùng
- Đặt câu hỏi mở để khuyến khích chia sẻ
- Không đưa ra chẩn đoán y tế
- Hướng dẫn tìm kiếm hỗ trợ chuyên nghiệp khi cần

PHONG CÁCH:
- Ấm áp, thấu hiểu, không phán xét
- Sử dụng ngôn ngữ đơn giản, dễ hiểu
- Tránh thuật ngữ y tế phức tạp
- Độ dài phản hồi: 2-3 câu"""

        # Add AI context if available
        if ai_context:
            severity = ai_context.get('severity', 0.0)
            context_type = ai_context.get('type', 'normal_worry')
            
            if severity > 0.6:
                base_prompt += f"\n\nNGỮ CẢNH: Người dùng đang có dấu hiệu {context_type} mức độ nghiêm trọng. Hãy thể hiện sự quan tâm đặc biệt và khuyến khích chia sẻ thêm."
            elif severity > 0.3:
                base_prompt += f"\n\nNGỮ CẢNH: Người dùng có dấu hiệu {context_type} mức độ trung bình. Hãy tỏ ra thấu hiểu và hỏi thêm thông tin."
            else:
                base_prompt += f"\n\nNGỮ CẢNH: Người dùng có {context_type} ở mức độ bình thường. Hãy lắng nghe và khuyến khích chia sẻ."
        
        return base_prompt

    def _handle_transition(self, assessment_type: str, reason: str, state: Dict, history: List[Dict], ai_context: Optional[Dict] = None) -> Dict:
        """Handle transition to assessment phase"""
        
        # Update state for transition
        state['current_phase'] = 'assessment'
        state['assessment_type'] = assessment_type
        state['transition_reason'] = reason
        state['transition_time'] = datetime.now().isoformat()
        
        # Create transition message
        transition_message = self.templates['transition']
        
        # Add context-specific message if AI analysis available
        if ai_context:
            severity = ai_context.get('severity', 0.0)
            if severity > 0.7:
                transition_message = "Tôi thấy bạn đang trải qua những khó khăn đáng kể. " + transition_message
            elif ai_context.get('type') == 'suicide_risk':
                transition_message = "Tôi quan tâm đến sự an toàn của bạn. " + transition_message
        
        # Add bot response to history
        final_history = history + [{'role': 'bot', 'content': transition_message}]
        
        return {
            'message': transition_message,
            'history': final_history,
            'state': state,
            'metadata': {
                'type': 'transition',
                'phase': 'assessment',
                'assessment_type': assessment_type,
                'reason': reason,
                'ai_severity': ai_context.get('severity', 0.0) if ai_context else 0.0,
                'transition_time': state['transition_time']
            }
        }

    def _generate_fallback_response(self, message: str, history: List[Dict], state: Dict) -> str:
        """Generate fallback response when AI is not available"""
        
        message_count = len([msg for msg in history if msg.get('role') == 'user'])
        
        # Simple rule-based responses
        message_lower = message.lower()
        
        if message_count == 1:
            return self.templates['greeting']
        elif any(word in message_lower for word in ['cảm ơn', 'thank']):
            return "Tôi luôn sẵn sàng lắng nghe bạn. Bạn còn muốn chia sẻ điều gì khác không?"
        elif any(word in message_lower for word in ['buồn', 'sad', 'khó khăn']):
            return self.templates['understanding']
        else:
            return self.templates['encouragement']

    def _generate_error_response(self, history: List[Dict], state: Dict) -> Dict:
        """Generate error response"""
        error_message = "Xin lỗi, có lỗi xảy ra. Bạn có thể thử lại không?"
        
        return {
            'message': error_message,
            'history': history + [{'role': 'bot', 'content': error_message}],
            'state': state,
            'metadata': {
                'type': 'error',
                'phase': state.get('current_phase', 'chat'),
                'ai_used': False
            }
        }

    def get_conversation_summary(self, history: List[Dict]) -> Dict:
        """Get summary of conversation for debugging/monitoring"""
        
        user_messages = [msg for msg in history if msg.get('role') == 'user']
        if not user_messages:
            return {'message_count': 0, 'summary': 'No user messages'}
        
        # Get last AI analysis if available
        try:
            last_message = user_messages[-1]['content']
            ai_analysis = classify_emotional_context(last_message, history)
        except:
            ai_analysis = {'severity': 0.0, 'type': 'unknown', 'confidence': 0.0}
        
        return {
            'message_count': len(user_messages),
            'avg_message_length': sum(len(msg['content']) for msg in user_messages) / len(user_messages),
            'ai_severity': ai_analysis.get('severity', 0.0),
            'ai_type': ai_analysis.get('type', 'unknown'),
            'ai_confidence': ai_analysis.get('confidence', 0.0),
            'summary': f"Conversation with {len(user_messages)} messages, AI detected {ai_analysis.get('type', 'unknown')}"
        }

# Factory function
def create_chat_engine() -> ChatEngine:
    """Create and return a configured ChatEngine instance"""
    return ChatEngine()