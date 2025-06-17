# positive_closure.py
"""
Positive Closure System - Hệ thống đóng gói tích cực cuộc trò chuyện
Khi AI không phát hiện vấn đề nghiêm trọng sau một số tin nhắn nhất định
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ClosureConfig:
    """Configuration cho positive closure system"""
    # Số tin nhắn tối thiểu trước khi có thể closure
    min_messages_for_closure: int = 6
    
    # Số tin nhắn tối đa trước khi force closure (tránh vòng lặp vô tận)
    max_messages_before_closure: int = 12
    
    # Threshold cho low severity để kích hoạt closure
    low_severity_threshold: float = 0.3
    
    # Số tin nhắn liên tiếp có severity thấp để trigger closure
    consecutive_low_severity_count: int = 3
    
    # Confidence threshold để đảm bảo AI phân tích chính xác
    min_confidence_for_closure: float = 0.6

class PositiveClosureManager:
    """Quản lý việc đóng gói tích cực cuộc trò chuyện"""
    
    def __init__(self, config: Optional[ClosureConfig] = None):
        self.config = config or ClosureConfig()
        
        # Closure message templates
        self.closure_templates = {
            'general_reassurance': [
                "Qua những gì chúng ta đã trò chuyện, tôi thấy bạn có vẻ đang xử lý tốt những cảm xúc của mình. Điều này thật tuyệt vời! 😊",
                "Dựa trên cuộc trò chuyện của chúng ta, tôi không thấy bạn có dấu hiệu nghiêm trọng nào về sức khỏe tâm thần. Đây là tin tốt!",
                "Tôi có thể thấy rằng bạn đang khá ổn định về mặt tinh thần. Những cảm xúc bạn chia sẻ là hoàn toàn bình thường trong cuộc sống."
            ],
            
            'continue_offer': [
                "Nếu bạn muốn tiếp tục trò chuyện, tôi vẫn sẵn sàng lắng nghe và đồng hành cùng bạn. 💙",
                "Dù không có vấn đề nghiêm trọng, tôi vẫn luôn ở đây để bạn có thể tâm sự bất cứ lúc nào.",
                "Bạn có thể coi tôi như một người bạn sẵn sàng lắng nghe - dù chỉ là những câu chuyện đời thường. 🤗"
            ],
            
            'positive_reinforcement': [
                "Việc bạn chủ động quan tâm đến sức khỏe tâm thần của mình cho thấy bạn là người rất tự giác và có trách nhiệm với bản thân.",
                "Khả năng nhận biết và chia sẻ cảm xúc của bạn là một điểm mạnh tuyệt vời.",
                "Bạn có một cách tiếp cận rất tích cực và cởi mở với những vấn đề cá nhân."
            ],
            
            'future_guidance': [
                "Hãy tiếp tục duy trì thói quen chăm sóc bản thân như hiện tại. Nếu trong tương lai có điều gì thay đổi, đừng ngần ngại tìm kiếm sự hỗ trợ.",
                "Nếu bạn cảm thấy cần thiết, bạn luôn có thể quay lại đây hoặc tìm kiếm sự hỗ trợ từ các chuyên gia tâm lý.",
                "Hãy nhớ rằng việc chăm sóc sức khỏe tâm thần là một hành trình dài. Bạn đang làm rất tốt!"
            ]
        }

    def should_trigger_closure(self, conversation_history: List[Dict], current_ai_analysis: Dict) -> Tuple[bool, str]:
        """
        Kiểm tra xem có nên kích hoạt positive closure không
        
        Args:
            conversation_history: Lịch sử cuộc trò chuyện
            current_ai_analysis: Kết quả AI analysis hiện tại
            
        Returns:
            (should_close, reason)
        """
        try:
            user_messages = [msg for msg in conversation_history if msg.get('role') == 'user']
            message_count = len(user_messages)
            
            # Rule 1: Kiểm tra số tin nhắn tối thiểu
            if message_count < self.config.min_messages_for_closure:
                return False, f"Chưa đủ tin nhắn ({message_count}/{self.config.min_messages_for_closure})"
            
            # Rule 2: Force closure nếu quá nhiều tin nhắn
            if message_count >= self.config.max_messages_before_closure:
                return True, f"Đã đạt giới hạn tin nhắn ({message_count}), force closure"
            
            # Rule 3: Kiểm tra severity hiện tại
            current_severity = current_ai_analysis.get('severity', 0.0)
            current_confidence = current_ai_analysis.get('confidence', 0.0)
            
            if current_severity > self.config.low_severity_threshold:
                return False, f"Severity quá cao ({current_severity})"
            
            if current_confidence < self.config.min_confidence_for_closure:
                return False, f"Confidence quá thấp ({current_confidence})"
            
            # Rule 4: Kiểm tra pattern của các tin nhắn gần đây
            recent_severities = self._extract_recent_severities(conversation_history)
            consecutive_low = self._count_consecutive_low_severity(recent_severities)
            
            if consecutive_low >= self.config.consecutive_low_severity_count:
                return True, f"Liên tiếp {consecutive_low} tin nhắn có severity thấp"
            
            # Rule 5: Kiểm tra content pattern - user có vẻ ổn định
            if self._detect_stable_pattern(conversation_history):
                return True, "Phát hiện pattern ổn định trong cuộc trò chuyện"
            
            return False, "Chưa đủ điều kiện closure"
            
        except Exception as e:
            logger.error(f"Error checking closure trigger: {e}")
            return False, f"Lỗi kiểm tra: {e}"

    def generate_closure_message(self, conversation_history: List[Dict], ai_analysis: Dict) -> str:
        """
        Tạo tin nhắn closure tích cực
        
        Args:
            conversation_history: Lịch sử cuộc trò chuyện
            ai_analysis: Kết quả AI analysis
            
        Returns:
            Closure message
        """
        try:
            # Phân tích context để tạo message phù hợp
            context_type = ai_analysis.get('type', 'normal_worry')
            severity = ai_analysis.get('severity', 0.0)
            message_count = len([msg for msg in conversation_history if msg.get('role') == 'user'])
            
            # Chọn template dựa trên context
            reassurance = self._select_template('general_reassurance', context_type)
            reinforcement = self._select_template('positive_reinforcement', context_type)
            continue_offer = self._select_template('continue_offer', context_type)
            guidance = self._select_template('future_guidance', context_type)
            
            # Tạo message kết hợp
            closure_message = f"""
{reassurance}

{reinforcement}

{continue_offer}

{guidance}

---
💡 **Tóm tắt đánh giá:** Sau {message_count} tin nhắn, tôi không phát hiện dấu hiệu nghiêm trọng nào cần can thiệp chuyên môn. Mức độ lo âu/stress của bạn ở ngưỡng bình thường ({severity:.1f}/1.0).
            """.strip()
            
            return closure_message
            
        except Exception as e:
            logger.error(f"Error generating closure message: {e}")
            return self._get_fallback_closure_message()

    def _extract_recent_severities(self, conversation_history: List[Dict], window_size: int = 5) -> List[float]:
        """Trích xuất severity scores của các tin nhắn gần đây"""
        severities = []
        
        # Giả định rằng metadata về AI analysis được lưu trong conversation state
        # Hoặc có thể re-analyze các tin nhắn gần đây
        for msg in conversation_history[-window_size:]:
            if msg.get('role') == 'user':
                # Lấy severity từ metadata hoặc re-analyze
                severity = msg.get('ai_analysis', {}).get('severity', 0.0)
                severities.append(severity)
        
        return severities

    def _count_consecutive_low_severity(self, severities: List[float]) -> int:
        """Đếm số tin nhắn liên tiếp có severity thấp"""
        consecutive = 0
        
        for severity in reversed(severities):  # Đếm ngược từ tin nhắn mới nhất
            if severity <= self.config.low_severity_threshold:
                consecutive += 1
            else:
                break
        
        return consecutive

    def _detect_stable_pattern(self, conversation_history: List[Dict]) -> bool:
        """
        Phát hiện pattern ổn định trong cuộc trò chuyện
        - User không mention các từ khóa nghiêm trọng
        - Tone tích cực hoặc trung tính
        - Không có escalation
        """
        try:
            user_messages = [msg['content'] for msg in conversation_history if msg.get('role') == 'user']
            
            # Từ khóa chỉ sự ổn định
            stable_keywords = [
                'ổn', 'bình thường', 'không sao', 'tốt', 'khá ổn', 'được rồi',
                'cũng tạm', 'không có gì', 'fine', 'okay', 'good', 'normal'
            ]
            
            # Từ khóa nghiêm trọng
            serious_keywords = [
                'tự tử', 'chết', 'không thể chịu nổi', 'tuyệt vọng', 'không còn hy vọng',
                'suicide', 'die', 'hopeless', 'can\'t take it', 'end it all'
            ]
            
            stable_count = 0
            serious_count = 0
            
            for message in user_messages[-3:]:  # Chỉ xét 3 tin nhắn gần nhất
                message_lower = message.lower()
                
                for keyword in stable_keywords:
                    if keyword in message_lower:
                        stable_count += 1
                        break
                
                for keyword in serious_keywords:
                    if keyword in message_lower:
                        serious_count += 1
                        break
            
            # Pattern ổn định nếu có keyword stable và không có keyword serious
            return stable_count > 0 and serious_count == 0
            
        except Exception as e:
            logger.error(f"Error detecting stable pattern: {e}")
            return False

    def _select_template(self, template_type: str, context_type: str) -> str:
        """Chọn template phù hợp với context"""
        templates = self.closure_templates.get(template_type, [])
        
        if not templates:
            return ""
        
        # Logic chọn template dựa trên context_type
        if context_type in ['normal_worry', 'situational_stress']:
            return templates[0]  # Template về lo lắng bình thường
        elif context_type in ['normal_sadness']:
            return templates[1] if len(templates) > 1 else templates[0]
        else:
            return templates[-1]  # Template chung

    def _get_fallback_closure_message(self) -> str:
        """Message closure dự phòng khi có lỗi"""
        return """
Qua cuộc trò chuyện này, tôi thấy bạn có vẻ đang ổn về mặt tinh thần. 😊

Nếu bạn muốn tiếp tục chia sẻ, tôi vẫn sẵn sàng lắng nghe. Việc bạn quan tâm đến sức khỏe tâm thần của mình là điều rất tích cực!

Hãy nhớ rằng nếu trong tương lai có bất kỳ thay đổi nào, bạn luôn có thể tìm kiếm sự hỗ trợ khi cần thiết.
        """.strip()

    def update_conversation_with_closure(self, conversation_history: List[Dict], closure_message: str) -> Dict:
        """
        Cập nhật conversation state với closure
        
        Args:
            conversation_history: Lịch sử hiện tại
            closure_message: Message closure
            
        Returns:
            Updated conversation dict
        """
        closure_entry = {
            'role': 'bot',
            'content': closure_message,
            'timestamp': datetime.now().isoformat(),
            'type': 'positive_closure',
            'metadata': {
                'closure_triggered': True,
                'closure_time': datetime.now().isoformat(),
                'assessment_result': 'no_serious_issues',
                'user_can_continue': True
            }
        }
        
        updated_history = conversation_history + [closure_entry]
        
        return {
            'history': updated_history,
            'state': {
                'closure_applied': True,
                'closure_type': 'positive_reassurance',
                'user_assessment': 'stable',
                'continue_chatting_allowed': True
            },
            'metadata': {
                'type': 'positive_closure',
                'should_show_continue_option': True,
                'assessment_summary': 'Không phát hiện vấn đề nghiêm trọng',
                'recommendations': [
                    'Tiếp tục duy trì thói quen chăm sóc bản thân',
                    'Tìm kiếm hỗ trợ khi cần thiết',
                    'Quan tâm đến sức khỏe tâm thần là điều tích cực'
                ]
            }
        }

# Integration với existing chat engine
class PositiveClosureIntegration:
    """Tích hợp Positive Closure vào chat engine hiện tại"""
    
    def __init__(self, chat_engine, closure_manager: Optional[PositiveClosureManager] = None):
        self.chat_engine = chat_engine
        self.closure_manager = closure_manager or PositiveClosureManager()

    def enhanced_process_message(self, message: str, history: List[Dict], state: Dict, use_ai: bool = True) -> Dict:
        """
        Enhanced message processing với positive closure check
        """
        # Xử lý message như bình thường
        result = self.chat_engine.process_message(message, history, state, use_ai)
        
        # Kiểm tra có cần positive closure không
        if not state.get('closure_applied', False):
            current_ai_analysis = state.get('last_ai_analysis', {})
            updated_history = result.get('history', history)
            
            should_close, reason = self.closure_manager.should_trigger_closure(
                updated_history, current_ai_analysis
            )
            
            if should_close:
                # Tạo closure message
                closure_message = self.closure_manager.generate_closure_message(
                    updated_history, current_ai_analysis
                )
                
                # Cập nhật result với closure
                closure_update = self.closure_manager.update_conversation_with_closure(
                    updated_history, closure_message
                )
                
                # Merge closure vào result
                result['message'] = closure_message
                result['history'] = closure_update['history']
                result['state'].update(closure_update['state'])
                result['metadata'].update(closure_update['metadata'])
                result['metadata']['closure_reason'] = reason
        
        return result

# Usage example trong chat engine
def integrate_positive_closure_to_chat_engine():
    """
    Hướng dẫn tích hợp vào chat engine hiện tại
    """
    # 1. Thêm vào src/core/chat_engine.py
    
    # from positive_closure import PositiveClosureManager
    
    # class ChatEngine:
    #     def __init__(self):
    #         # ... existing code ...
    #         self.closure_manager = PositiveClosureManager()
    
    #     def process_message(self, message, history, state, use_ai=True):
    #         # ... existing logic ...
    #         
    #         # Thêm closure check trước khi return
    #         if not state.get('closure_applied', False):
    #             should_close, reason = self.closure_manager.should_trigger_closure(
    #                 final_history, ai_context
    #             )
    #             
    #             if should_close:
    #                 closure_message = self.closure_manager.generate_closure_message(
    #                     final_history, ai_context
    #                 )
    #                 
    #                 # Override response với closure message
    #                 return {
    #                     'message': closure_message,
    #                     'history': final_history + [{'role': 'bot', 'content': closure_message}],
    #                     'state': {**state, 'closure_applied': True},
    #                     'metadata': {
    #                         'type': 'positive_closure',
    #                         'closure_reason': reason,
    #                         'continue_option': True
    #                     }
    #                 }
    #         
    #         return result
    
    pass

# Configuration có thể tùy chỉnh
DEFAULT_CONFIG = ClosureConfig(
    min_messages_for_closure=6,
    max_messages_before_closure=12,
    low_severity_threshold=0.3,
    consecutive_low_severity_count=3,
    min_confidence_for_closure=0.6
)

# Factory function
def create_positive_closure_manager(config: Optional[Dict] = None) -> PositiveClosureManager:
    """Tạo PositiveClosureManager với config tùy chỉnh"""
    if config:
        closure_config = ClosureConfig(**config)
    else:
        closure_config = DEFAULT_CONFIG
    
    return PositiveClosureManager(closure_config)