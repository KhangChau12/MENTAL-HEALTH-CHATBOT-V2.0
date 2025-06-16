"""
AI Context Analyzer - Phân tích ngữ cảnh cảm xúc bằng AI
Thay thế keyword matching bằng AI analysis thông minh
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any
from src.services.together_client import get_together_client

logger = logging.getLogger(__name__)

class AIContextAnalyzer:
    """Service chuyên phân tích ngữ cảnh cảm xúc bằng AI"""
    
    def __init__(self):
        self.client = None
        self.initialized = False
        
    def initialize_ai_analyzer(self) -> bool:
        """
        Khởi tạo AI analyzer service
        Return: True nếu khởi tạo thành công
        """
        try:
            self.client = get_together_client()
            if self.client is None:
                logger.error("Failed to get Together AI client")
                return False
                
            # Test connection với một request đơn giản
            test_response = self.client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
                temperature=0.3
            )
            
            if test_response:
                self.initialized = True
                logger.info("AI Context Analyzer initialized successfully")
                return True
            else:
                logger.error("AI test request failed")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing AI analyzer: {e}")
            return False

    def classify_emotional_context(self, text: str, history: List[Dict]) -> Dict:
        """
        Phân loại ngữ cảnh cảm xúc bằng AI
        
        Params:
            - text: Tin nhắn hiện tại của user
            - history: Lịch sử cuộc trò chuyện
        
        Return: {
            'severity': float (0.0-1.0),
            'type': str ('normal_worry'|'clinical_anxiety'|'depression_signs'|...),
            'reasoning': str,
            'confidence': float
        }
        """
        if not self.initialized:
            logger.warning("AI analyzer not initialized, returning default values")
            return {
                'severity': 0.0,
                'type': 'normal_worry',
                'reasoning': 'AI analyzer not available',
                'confidence': 0.0
            }
        
        try:
            # Tạo prompt có cấu trúc
            prompt = self.create_context_analysis_prompt(text, history)
            
            # Gọi AI
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            # Parse response
            ai_response = response.choices[0].message.content
            return self.parse_ai_analysis_response(ai_response)
            
        except Exception as e:
            logger.error(f"Error in AI emotional context analysis: {e}")
            return {
                'severity': 0.0,
                'type': 'normal_worry',
                'reasoning': f'AI analysis failed: {str(e)}',
                'confidence': 0.0
            }

    def create_context_analysis_prompt(self, text: str, history: List[Dict]) -> str:
        """
        Tạo prompt cho AI để phân tích ngữ cảnh
        
        Params:
            - text: Tin nhắn cần phân tích
            - history: Context từ cuộc trò chuyện
        
        Return: Prompt string có cấu trúc
        """
        # Lấy context từ lịch sử (3 tin nhắn gần nhất)
        recent_history = ""
        user_messages = [msg for msg in history if msg.get('role') == 'user']
        if user_messages:
            recent_messages = user_messages[-3:]
            recent_history = "\n".join([f"- {msg['content']}" for msg in recent_messages])
        
        prompt = f"""
Bạn là chuyên gia tâm lý, hãy phân tích tin nhắn sau để phân biệt giữa cảm xúc bình thường và dấu hiệu bệnh lý.

LỊCH SỬ CUỘC TRÒ CHUYỆN:
{recent_history}

TIN NHẮN HIỆN Tại: "{text}"

Hãy phân tích và trả lời theo format JSON chính xác sau:
{{
    "severity": [số từ 0.0 đến 1.0],
    "type": "[một trong: normal_worry, normal_sadness, situational_stress, clinical_anxiety, depression_signs, chronic_stress, suicide_risk]",
    "reasoning": "[giải thích ngắn gọn]",
    "confidence": [số từ 0.0 đến 1.0]
}}

HƯỚNG DẪN PHÂN LOẠI:
- normal_worry: Lo lắng về việc cụ thể (thi cử, công việc, tương lai)
- normal_sadness: Buồn do sự kiện cụ thể (chia tay, thất bại)
- situational_stress: Stress có nguyên nhân rõ ràng và tạm thời
- clinical_anxiety: Lo âu không có lý do rõ ràng, kéo dài, ảnh hưởng cuộc sống
- depression_signs: Buồn chán kéo dài, mất hứng thú, cảm giác vô vọng
- chronic_stress: Stress kéo dài nhiều tuần/tháng
- suicide_risk: Có ý định tự hại bản thân

SEVERITY SCORE:
- 0.0-0.3: Cảm xúc bình thường, tạm thời
- 0.4-0.6: Cần quan tâm, theo dõi
- 0.7-0.9: Có dấu hiệu bệnh lý, cần đánh giá
- 0.9-1.0: Nguy hiểm, cần can thiệp ngay

CHỈ TRẢ LỜI JSON, KHÔNG GIẢI THÍCH THÊM.
"""
        return prompt

    def parse_ai_analysis_response(self, response: str) -> Dict:
        """
        Parse response từ AI thành format chuẩn
        
        Params:
            - response: Raw response từ AI
        
        Return: Structured Dict
        """
        try:
            # Tìm JSON trong response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                # Validate và normalize
                validated_result = {
                    'severity': float(result.get('severity', 0.0)),
                    'type': str(result.get('type', 'normal_worry')),
                    'reasoning': str(result.get('reasoning', '')),
                    'confidence': float(result.get('confidence', 0.0))
                }
                
                # Ensure values are in valid ranges
                validated_result['severity'] = max(0.0, min(1.0, validated_result['severity']))
                validated_result['confidence'] = max(0.0, min(1.0, validated_result['confidence']))
                
                # Validate type
                valid_types = [
                    'normal_worry', 'normal_sadness', 'situational_stress',
                    'clinical_anxiety', 'depression_signs', 'chronic_stress', 'suicide_risk'
                ]
                if validated_result['type'] not in valid_types:
                    validated_result['type'] = 'normal_worry'
                
                return validated_result
            else:
                logger.warning("No JSON found in AI response")
                return self._get_default_response()
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return self._get_default_response()
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return self._get_default_response()

    def _get_default_response(self) -> Dict:
        """Return default response when parsing fails"""
        return {
            'severity': 0.0,
            'type': 'normal_worry',
            'reasoning': 'Unable to parse AI response',
            'confidence': 0.0
        }

# Global instance
ai_context_analyzer = AIContextAnalyzer()

def initialize_ai_analyzer() -> bool:
    """Initialize the global AI analyzer instance"""
    return ai_context_analyzer.initialize_ai_analyzer()

def classify_emotional_context(text: str, history: List[Dict]) -> Dict:
    """Convenience function to use global analyzer"""
    return ai_context_analyzer.classify_emotional_context(text, history)