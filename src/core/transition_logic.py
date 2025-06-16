"""
Transition Logic - AI-Powered Context Analysis + Simplified Factors
THAY ĐỔI HOÀN TOÀN: Sử dụng AI thay vì keyword matching
"""

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from src.services.ai_context_analyzer import classify_emotional_context
from src.core.conversation_analyzer import ConversationAnalyzer

logger = logging.getLogger(__name__)

class SimplifiedTransitionLogic:
    """Logic quyết định chuyển đổi được đơn giản hóa với AI context analysis"""
    
    def __init__(self):
        self.conversation_analyzer = ConversationAnalyzer()
        
        # Thresholds từ config
        self.thresholds = {
            'overall_threshold': 0.65,  # Tăng từ 0.4 hiện tại
            'ai_weight': 0.5,
            'depth_weight': 0.3,
            'duration_weight': 0.2,
            'minimum_messages': 4  # Tối thiểu 4 tin nhắn mới check transition
        }
        
        # Assessment type mapping based on AI analysis
        self.assessment_mapping = {
            'clinical_anxiety': 'gad7',
            'depression_signs': 'phq9',
            'chronic_stress': 'dass21_stress',
            'suicide_risk': 'suicide_risk',
            'normal_worry': 'gad7',  # Default fallback
            'normal_sadness': 'phq9',  # Default fallback
            'situational_stress': 'dass21_stress'  # Default fallback
        }

    def analyze_with_ai_context(self, text: str, conversation_history: List[Dict]) -> Dict:
        """
        Thay thế keyword matching bằng AI analysis
        
        Params:
            - text: Tin nhắn hiện tại
            - conversation_history: Lịch sử cuộc trò chuyện
        
        Return: {
            'severity': float,
            'type': str,
            'reasoning': str,
            'needs_followup': bool
        }
        """
        try:
            # Gọi AI context analyzer
            ai_result = classify_emotional_context(text, conversation_history)
            
            # Validate và process results
            severity = max(0.0, min(1.0, ai_result.get('severity', 0.0)))
            context_type = ai_result.get('type', 'normal_worry')
            reasoning = ai_result.get('reasoning', 'AI analysis completed')
            confidence = ai_result.get('confidence', 0.0)
            
            # Business logic layer
            needs_followup = severity < 0.5 and confidence > 0.6
            
            # Special handling cho suicide risk
            if context_type == 'suicide_risk':
                severity = max(severity, 0.9)  # Force high severity
                needs_followup = False  # Skip followup, go straight to assessment
            
            return {
                'severity': severity,
                'type': context_type,
                'reasoning': reasoning,
                'confidence': confidence,
                'needs_followup': needs_followup
            }
            
        except Exception as e:
            logger.error(f"Error in AI context analysis: {e}")
            # Fallback to safe defaults
            return {
                'severity': 0.0,
                'type': 'normal_worry',
                'reasoning': f'AI analysis failed: {str(e)}',
                'confidence': 0.0,
                'needs_followup': True
            }

    def calculate_conversation_depth(self, history: List[Dict]) -> float:
        """
        Đánh giá độ sâu cuộc trò chuyện
        
        Params:
            - history: Lịch sử tin nhắn
        
        Return: Depth score 0.0-1.0
        """
        try:
            # Gọi conversation analyzer
            depth_score = self.conversation_analyzer.calculate_progressive_depth(history)
            
            # Apply business rules
            user_messages = [msg for msg in history if msg.get('role') == 'user']
            message_count = len(user_messages)
            
            # Minimum messages requirement
            if message_count < 3:
                depth_score *= 0.5  # Penalize very short conversations
            
            # Normalize score
            return max(0.0, min(1.0, depth_score))
            
        except Exception as e:
            logger.error(f"Error calculating conversation depth: {e}")
            return 0.0

    def extract_duration_indicators(self, history: List[Dict]) -> float:
        """
        Phát hiện dấu hiệu về thời gian kéo dài
        
        Params:
            - history: Lịch sử tin nhắn
        
        Return: Duration score 0.0-1.0
        """
        try:
            # Combine text từ tất cả user messages
            user_messages = [msg for msg in history if msg.get('role') == 'user']
            if not user_messages:
                return 0.0
            
            combined_text = ' '.join([msg['content'] for msg in user_messages])
            
            # Gọi conversation analyzer
            temporal_indicators = self.conversation_analyzer.detect_temporal_indicators(combined_text)
            duration_score = self.conversation_analyzer.score_duration_severity(temporal_indicators)
            
            return duration_score
            
        except Exception as e:
            logger.error(f"Error extracting duration indicators: {e}")
            return 0.0

    def simplified_transition_decision(self, ai_severity: float, depth: float, duration: float) -> Tuple[bool, str]:
        """
        Quyết định chuyển đổi chỉ dựa trên 3 factors
        
        Params:
            - ai_severity: AI analysis severity score
            - depth: Conversation depth score  
            - duration: Duration indicators score
        
        Return: (should_transition: bool, assessment_type: str)
        """
        # Weighted sum: AI(50%) + Depth(30%) + Duration(20%)
        weighted_score = (
            ai_severity * self.thresholds['ai_weight'] +
            depth * self.thresholds['depth_weight'] +
            duration * self.thresholds['duration_weight']
        )
        
        should_transition = weighted_score >= self.thresholds['overall_threshold']
        
        # Determine assessment type based on highest contributing factor
        if ai_severity >= depth and ai_severity >= duration:
            # AI severity is highest - use AI recommendation
            assessment_type = 'phq9'  # Default, will be overridden later
        elif duration >= depth:
            # Duration is highest - chronic issues
            assessment_type = 'dass21_stress'
        else:
            # Depth is highest - general assessment
            assessment_type = 'gad7'
        
        logger.info(f"Transition decision: AI={ai_severity:.2f}, Depth={depth:.2f}, "
                   f"Duration={duration:.2f}, Weighted={weighted_score:.2f}, "
                   f"Decision={should_transition}, Type={assessment_type}")
        
        return should_transition, assessment_type

    def generate_smart_followup(self, ai_analysis: Dict, current_depth: float) -> str:
        """
        Tạo câu hỏi follow-up thông minh
        
        Params:
            - ai_analysis: Result từ AI analysis
            - current_depth: Current conversation depth
        
        Return: Follow-up message string
        """
        context_type = ai_analysis.get('type', 'normal_worry')
        severity = ai_analysis.get('severity', 0.0)
        
        # Follow-up templates based on context type
        followup_templates = {
            'normal_worry': [
                "Bạn có thể chia sẻ cụ thể hơn về điều gì đang khiến bạn lo lắng không?",
                "Điều này đã ảnh hưởng đến cuộc sống hàng ngày của bạn như thế nào?",
                "Bạn đã thử cách nào để giải quyết vấn đề này chưa?"
            ],
            'normal_sadness': [
                "Cảm giác buồn này có kéo dài từ lúc nào không?",
                "Bạn có muốn chia sẻ về nguyên nhân khiến bạn cảm thấy buồn?",
                "Bạn có làm được những việc bình thường như trước đây không?"
            ],
            'situational_stress': [
                "Tình huống này đã diễn ra trong bao lâu rồi?",
                "Bạn cảm thấy stress này ảnh hưởng đến giấc ngủ hay ăn uống không?",
                "Có ai bạn có thể tâm sự về vấn đề này không?"
            ],
            'clinical_anxiety': [
                "Cảm giác lo âu này có xuất hiện khi không có lý do rõ ràng không?",
                "Bạn có gặp các triệu chứng như tim đập nhanh, khó thở không?",
                "Điều này có làm bạn tránh né các hoạt động bình thường không?"
            ],
            'depression_signs': [
                "Bạn có mất hứng thú với những việc từng thích làm không?",
                "Giấc ngủ và cảm giác năng lượng của bạn có thay đổi không?",
                "Bạn có cảm thấy tuyệt vọng về tương lai không?"
            ],
            'chronic_stress': [
                "Tình trạng này đã kéo dài bao lâu rồi?",
                "Bạn có thấy khó khăn trong việc thư giãn hay nghỉ ngơi không?",
                "Stress này có ảnh hưởng đến công việc hay học tập không?"
            ]
        }
        
        # Get appropriate questions
        questions = followup_templates.get(context_type, followup_templates['normal_worry'])
        
        # Choose question based on current depth
        if current_depth < 0.3:
            # Low depth - encourage general sharing
            question = questions[0]
        elif current_depth < 0.6:
            # Medium depth - probe specifics
            question = questions[1] if len(questions) > 1 else questions[0]
        else:
            # High depth - ask about impact
            question = questions[-1]
        
        # Add appropriate prefix based on severity
        if severity > 0.6:
            prefix = "Tôi hiểu đây là điều khó khăn với bạn. "
        elif severity > 0.3:
            prefix = "Cảm ơn bạn đã chia sẻ. "
        else:
            prefix = ""
        
        return prefix + question

    def should_transition_to_assessment(self, current_message: str, conversation_history: List[Dict]) -> Tuple[bool, str, str]:
        """
        Main entry point - quyết định có nên chuyển sang assessment không
        
        Params:
            - current_message: Tin nhắn hiện tại
            - conversation_history: Lịch sử cuộc trò chuyện
        
        Return: (should_transition, assessment_type, reasoning)
        """
        try:
            # Check minimum message requirement
            user_messages = [msg for msg in conversation_history if msg.get('role') == 'user']
            if len(user_messages) < self.thresholds['minimum_messages']:
                return False, '', f"Cần thêm {self.thresholds['minimum_messages'] - len(user_messages)} tin nhắn nữa"
            
            # 1. AI Context Analysis (50% weight)
            ai_analysis = self.analyze_with_ai_context(current_message, conversation_history)
            ai_severity = ai_analysis['severity']
            context_type = ai_analysis['type']
            
            # 2. Conversation Depth Analysis (30% weight)
            depth_score = self.calculate_conversation_depth(conversation_history)
            
            # 3. Duration Analysis (20% weight)
            duration_score = self.extract_duration_indicators(conversation_history)
            
            # 4. Make decision
            should_transition, base_assessment_type = self.simplified_transition_decision(
                ai_severity, depth_score, duration_score
            )
            
            # 5. Map AI context type to specific assessment
            final_assessment_type = self.assessment_mapping.get(context_type, base_assessment_type)
            
            # 6. Generate reasoning
            reasoning = self._generate_transition_reasoning(
                ai_analysis, depth_score, duration_score, should_transition
            )
            
            return should_transition, final_assessment_type, reasoning
            
        except Exception as e:
            logger.error(f"Error in transition decision: {e}")
            return False, '', f"Lỗi trong quá trình phân tích: {str(e)}"

    def _generate_transition_reasoning(self, ai_analysis: Dict, depth: float, duration: float, decision: bool) -> str:
        """Generate human-readable reasoning for the transition decision"""
        
        reasoning_parts = []
        
        if decision:
            reasoning_parts.append("Quyết định chuyển sang đánh giá vì:")
            
            # AI analysis reasoning
            if ai_analysis['severity'] > 0.4:
                reasoning_parts.append(f"- AI phát hiện dấu hiệu {ai_analysis['type']} (mức độ: {ai_analysis['severity']:.1f})")
            
            # Depth reasoning
            if depth > 0.4:
                reasoning_parts.append(f"- Cuộc trò chuyện có độ sâu cao ({depth:.1f}) - bạn đã chia sẻ nhiều thông tin cá nhân")
            
            # Duration reasoning
            if duration > 0.4:
                reasoning_parts.append(f"- Phát hiện dấu hiệu kéo dài thời gian ({duration:.1f})")
            
        else:
            reasoning_parts.append("Tiếp tục trò chuyện vì:")
            reasoning_parts.append(f"- Chưa đủ dấu hiệu để đánh giá (AI: {ai_analysis['severity']:.1f}, Depth: {depth:.1f}, Duration: {duration:.1f})")
        
        return " ".join(reasoning_parts)

# Main transition manager class
class TransitionManager:
    """Wrapper class để tương thích với code hiện tại"""
    
    def __init__(self):
        self.logic = SimplifiedTransitionLogic()
    
    def should_transition(self, messages: List[Dict], conversation_state: Dict) -> Tuple[bool, str, str]:
        """
        Main method cho transition check
        
        Params:
            - messages: Conversation history
            - conversation_state: Current state
        
        Return: (should_transition, assessment_type, reasoning)
        """
        if not messages:
            return False, '', 'Không có tin nhắn để phân tích'
        
        # Get current message
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        if not user_messages:
            return False, '', 'Không có tin nhắn từ user'
        
        current_message = user_messages[-1]['content']
        
        return self.logic.should_transition_to_assessment(current_message, messages)
    
    def generate_followup_question(self, messages: List[Dict]) -> str:
        """Generate smart followup question"""
        if not messages:
            return "Bạn có thể chia sẻ thêm với tôi không?"
        
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        if not user_messages:
            return "Hãy cho tôi biết thêm về cảm giác của bạn."
        
        current_message = user_messages[-1]['content']
        ai_analysis = self.logic.analyze_with_ai_context(current_message, messages)
        current_depth = self.logic.calculate_conversation_depth(messages)
        
        return self.logic.generate_smart_followup(ai_analysis, current_depth)

# Factory function
def create_transition_manager() -> TransitionManager:
    """Create and return a configured TransitionManager instance"""
    return TransitionManager()

# Convenience functions for backward compatibility
def should_transition_to_assessment(message: str, history: List[Dict]) -> Tuple[bool, str]:
    """Convenience function for quick transition check"""
    manager = create_transition_manager()
    should_transition, assessment_type, _ = manager.should_transition(history + [{'role': 'user', 'content': message}], {})
    return should_transition, assessment_type

def analyze_conversation_depth(history: List[Dict]) -> float:
    """Convenience function for depth analysis"""
    logic = SimplifiedTransitionLogic()
    return logic.calculate_conversation_depth(history)

def extract_duration_score(history: List[Dict]) -> float:
    """Convenience function for duration analysis"""
    logic = SimplifiedTransitionLogic()
    return logic.extract_duration_indicators(history)

def get_ai_context_analysis(message: str, history: List[Dict]) -> Dict:
    """Convenience function for AI context analysis"""
    logic = SimplifiedTransitionLogic()
    return logic.analyze_with_ai_context(message, history)

# Debugging and monitoring functions
def analyze_transition_decision_details(message: str, history: List[Dict]) -> Dict:
    """
    Detailed analysis for debugging transition decisions
    Returns all factors and intermediate calculations
    """
    try:
        logic = SimplifiedTransitionLogic()
        
        # Get all analysis components
        ai_analysis = logic.analyze_with_ai_context(message, history)
        depth_score = logic.calculate_conversation_depth(history)
        duration_score = logic.extract_duration_indicators(history)
        
        # Calculate weighted score
        weighted_score = (
            ai_analysis['severity'] * logic.thresholds['ai_weight'] +
            depth_score * logic.thresholds['depth_weight'] +
            duration_score * logic.thresholds['duration_weight']
        )
        
        should_transition = weighted_score >= logic.thresholds['overall_threshold']
        
        # Determine assessment type
        context_type = ai_analysis.get('type', 'normal_worry')
        assessment_type = logic.assessment_mapping.get(context_type, 'phq9')
        
        return {
            'message': message,
            'user_message_count': len([msg for msg in history if msg.get('role') == 'user']),
            'ai_analysis': {
                'severity': ai_analysis['severity'],
                'type': ai_analysis['type'],
                'reasoning': ai_analysis['reasoning'],
                'confidence': ai_analysis['confidence'],
                'weighted_contribution': ai_analysis['severity'] * logic.thresholds['ai_weight']
            },
            'depth_analysis': {
                'score': depth_score,
                'weighted_contribution': depth_score * logic.thresholds['depth_weight']
            },
            'duration_analysis': {
                'score': duration_score,
                'weighted_contribution': duration_score * logic.thresholds['duration_weight']
            },
            'decision': {
                'total_weighted_score': weighted_score,
                'threshold': logic.thresholds['overall_threshold'],
                'should_transition': should_transition,
                'assessment_type': assessment_type,
                'margin': weighted_score - logic.thresholds['overall_threshold']
            },
            'weights': logic.thresholds,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in detailed transition analysis: {e}")
        return {
            'error': str(e),
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

def get_transition_explanation(message: str, history: List[Dict]) -> str:
    """
    Generate human-readable explanation of transition decision
    """
    try:
        details = analyze_transition_decision_details(message, history)
        
        if 'error' in details:
            return f"Không thể phân tích: {details['error']}"
        
        explanation_parts = []
        
        # Overall decision
        if details['decision']['should_transition']:
            explanation_parts.append(f"✅ CHUYỂN SANG ĐÁNH GIÁ {details['decision']['assessment_type'].upper()}")
        else:
            explanation_parts.append("❌ TIẾP TỤC TRÒ CHUYỆN")
        
        # Score breakdown
        explanation_parts.append(f"📊 Điểm tổng: {details['decision']['total_weighted_score']:.3f}/{details['decision']['threshold']}")
        
        # Factor contributions
        explanation_parts.append("🔍 Phân tích chi tiết:")
        explanation_parts.append(f"   • AI Analysis: {details['ai_analysis']['severity']:.2f} x {details['weights']['ai_weight']} = {details['ai_analysis']['weighted_contribution']:.3f}")
        explanation_parts.append(f"     Type: {details['ai_analysis']['type']}")
        explanation_parts.append(f"     Reasoning: {details['ai_analysis']['reasoning']}")
        
        explanation_parts.append(f"   • Conversation Depth: {details['depth_analysis']['score']:.2f} x {details['weights']['depth_weight']} = {details['depth_analysis']['weighted_contribution']:.3f}")
        
        explanation_parts.append(f"   • Duration Indicators: {details['duration_analysis']['score']:.2f} x {details['weights']['duration_weight']} = {details['duration_analysis']['weighted_contribution']:.3f}")
        
        # Decision margin
        margin = details['decision']['margin']
        if margin > 0:
            explanation_parts.append(f"📈 Vượt threshold: +{margin:.3f}")
        else:
            explanation_parts.append(f"📉 Dưới threshold: {margin:.3f}")
        
        return "\n".join(explanation_parts)
        
    except Exception as e:
        logger.error(f"Error generating transition explanation: {e}")
        return f"Lỗi tạo giải thích: {str(e)}"

# Configuration and tuning functions
def update_transition_thresholds(new_thresholds: Dict) -> bool:
    """
    Update transition thresholds dynamically
    For A/B testing and optimization
    """
    try:
        logic = SimplifiedTransitionLogic()
        
        # Validate new thresholds
        if 'overall_threshold' in new_thresholds:
            if not 0.0 <= new_thresholds['overall_threshold'] <= 1.0:
                raise ValueError("overall_threshold must be between 0.0 and 1.0")
            logic.thresholds['overall_threshold'] = new_thresholds['overall_threshold']
        
        # Validate and update weights
        weight_keys = ['ai_weight', 'depth_weight', 'duration_weight']
        if any(key in new_thresholds for key in weight_keys):
            # Update weights
            for key in weight_keys:
                if key in new_thresholds:
                    logic.thresholds[key] = new_thresholds[key]
            
            # Validate weights sum to 1.0
            weight_sum = sum(logic.thresholds[key] for key in weight_keys)
            if abs(weight_sum - 1.0) > 0.01:
                raise ValueError(f"Weights must sum to 1.0, current sum: {weight_sum}")
        
        logger.info(f"Updated transition thresholds: {logic.thresholds}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating transition thresholds: {e}")
        return False

def get_current_transition_config() -> Dict:
    """Get current transition configuration"""
    logic = SimplifiedTransitionLogic()
    return {
        'thresholds': logic.thresholds.copy(),
        'assessment_mapping': logic.assessment_mapping.copy(),
        'version': 'ai_powered_v1.0'
    }

# Performance monitoring functions
def calculate_transition_metrics(conversation_logs: List[Dict]) -> Dict:
    """
    Calculate transition performance metrics from conversation logs
    For monitoring false positive/negative rates
    """
    try:
        metrics = {
            'total_conversations': len(conversation_logs),
            'transitions_made': 0,
            'ai_analysis_success_rate': 0,
            'average_messages_before_transition': 0,
            'assessment_type_distribution': {},
            'ai_severity_distribution': {'low': 0, 'medium': 0, 'high': 0},
            'depth_score_distribution': {'low': 0, 'medium': 0, 'high': 0},
            'duration_score_distribution': {'low': 0, 'medium': 0, 'high': 0}
        }
        
        if not conversation_logs:
            return metrics
        
        transitions = []
        ai_successes = 0
        
        for log in conversation_logs:
            # Count transitions
            if log.get('transitioned', False):
                metrics['transitions_made'] += 1
                transitions.append(log.get('message_count_at_transition', 0))
                
                # Assessment type distribution
                assessment_type = log.get('assessment_type', 'unknown')
                metrics['assessment_type_distribution'][assessment_type] = \
                    metrics['assessment_type_distribution'].get(assessment_type, 0) + 1
            
            # AI analysis success rate
            if log.get('ai_analysis_successful', False):
                ai_successes += 1
                
                # Score distributions
                ai_severity = log.get('ai_severity', 0.0)
                if ai_severity < 0.3:
                    metrics['ai_severity_distribution']['low'] += 1
                elif ai_severity < 0.7:
                    metrics['ai_severity_distribution']['medium'] += 1
                else:
                    metrics['ai_severity_distribution']['high'] += 1
            
            # Depth and duration distributions
            depth_score = log.get('depth_score', 0.0)
            duration_score = log.get('duration_score', 0.0)
            
            if depth_score < 0.3:
                metrics['depth_score_distribution']['low'] += 1
            elif depth_score < 0.7:
                metrics['depth_score_distribution']['medium'] += 1
            else:
                metrics['depth_score_distribution']['high'] += 1
                
            if duration_score < 0.3:
                metrics['duration_score_distribution']['low'] += 1
            elif duration_score < 0.7:
                metrics['duration_score_distribution']['medium'] += 1
            else:
                metrics['duration_score_distribution']['high'] += 1
        
        # Calculate rates
        metrics['transition_rate'] = metrics['transitions_made'] / metrics['total_conversations']
        metrics['ai_analysis_success_rate'] = ai_successes / metrics['total_conversations']
        
        if transitions:
            metrics['average_messages_before_transition'] = sum(transitions) / len(transitions)
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating transition metrics: {e}")
        return {'error': str(e)}

# Export all public functions
__all__ = [
    'SimplifiedTransitionLogic',
    'TransitionManager', 
    'create_transition_manager',
    'should_transition_to_assessment',
    'analyze_conversation_depth',
    'extract_duration_score',
    'get_ai_context_analysis',
    'analyze_transition_decision_details',
    'get_transition_explanation',
    'update_transition_thresholds',
    'get_current_transition_config',
    'calculate_transition_metrics'
]
