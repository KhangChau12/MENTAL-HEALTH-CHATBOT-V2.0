"""
Transition Logic - Advanced system for determining when to transition from chat to assessment
Fixes the main issue of unreliable chat-to-poll transitions
"""

import logging
import re
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TransitionResult:
    """Result of transition analysis"""
    should_transition: bool
    assessment_type: str
    confidence: float
    reason: str
    triggered_rules: List[str]
    emotional_indicators: Dict[str, float]

class EmotionalIndicatorAnalyzer:
    """Analyzes text for emotional indicators and mental health signals"""
    
    def __init__(self):
        self.emotion_patterns = {
            'depression': {
                'keywords': [
                    'buồn', 'chán nản', 'tuyệt vọng', 'không vui', 'trầm cảm', 
                    'mệt mỏi', 'không muốn', 'thất vọng', 'cô đơn', 'trống rỗng',
                    'không ý nghĩa', 'vô dụng', 'thất bại', 'tội lỗi',
                    'sad', 'depressed', 'hopeless', 'empty', 'tired', 'worthless',
                    'meaningless', 'useless', 'failure', 'guilty'
                ],
                'phrases': [
                    'không còn hy vọng', 'cuộc sống vô nghĩa', 'tôi là gánh nặng',
                    'không ai quan tâm', 'tôi không xứng đáng', 'mọi thứ đều tồi tệ',
                    'no hope left', 'life is meaningless', 'i am a burden',
                    'nobody cares', 'i don\'t deserve', 'everything is terrible'
                ],
                'intensity_multipliers': {
                    'rất': 1.5, 'cực kỳ': 2.0, 'hoàn toàn': 1.8,
                    'very': 1.5, 'extremely': 2.0, 'completely': 1.8
                }
            },
            
            'anxiety': {
                'keywords': [
                    'lo lắng', 'căng thẳng', 'bồn chồn', 'sợ hãi', 'hoảng loạn',
                    'tim đập nhanh', 'khó thở', 'run rẩy', 'không yên', 'lo âu',
                    'nervous', 'anxious', 'worried', 'panic', 'restless', 'scared',
                    'heart racing', 'breathless', 'shaking', 'uneasy'
                ],
                'phrases': [
                    'không thể ngừng suy nghĩ', 'luôn lo lắng', 'sợ điều tồi tệ',
                    'tim đập như trống', 'thở không ra hơi', 'tay chân run rẩy',
                    'can\'t stop thinking', 'always worried', 'fear the worst',
                    'heart pounds', 'can\'t breathe', 'hands shaking'
                ],
                'intensity_multipliers': {
                    'liên tục': 1.8, 'không ngừng': 2.0, 'suốt ngày': 1.6,
                    'constantly': 1.8, 'non-stop': 2.0, 'all day': 1.6
                }
            },
            
            'stress': {
                'keywords': [
                    'stress', 'áp lực', 'quá tải', 'kiệt sức', 'không thể chịu đựng',
                    'burned out', 'overwhelmed', 'pressure', 'exhausted', 'overloaded',
                    'không kéo nổi', 'sắp sụp đổ', 'quá sức', 'căng như dây đàn'
                ],
                'phrases': [
                    'không thể chịu đựng thêm', 'quá nhiều việc', 'sắp bị điên',
                    'áp lực từ mọi phía', 'không còn sức', 'sắp sụp đổ',
                    'can\'t take anymore', 'too much work', 'going crazy',
                    'pressure from everywhere', 'no energy left', 'about to collapse'
                ],
                'intensity_multipliers': {
                    'quá': 1.6, 'cực kỳ': 2.0, 'không thể': 1.8,
                    'too': 1.6, 'extremely': 2.0, 'can\'t': 1.8
                }
            },
            
            'suicide_risk': {
                'keywords': [
                    'chết', 'tự tử', 'kết thúc', 'không muốn sống', 'biến mất',
                    'làm hại bản thân', 'tự làm hại', 'không muốn ở đây nữa',
                    'suicide', 'kill myself', 'end it all', 'don\'t want to live',
                    'hurt myself', 'self harm', 'don\'t want to be here'
                ],
                'phrases': [
                    'muốn chết', 'không muốn sống nữa', 'kết thúc tất cả',
                    'làm hại bản thân', 'tự tử', 'biến mất khỏi đây',
                    'want to die', 'don\'t want to live anymore', 'end it all',
                    'hurt myself', 'kill myself', 'disappear from here'
                ],
                'intensity_multipliers': {
                    'thật sự': 2.5, 'nghiêm túc': 3.0, 'quyết tâm': 2.8,
                    'really': 2.5, 'seriously': 3.0, 'determined': 2.8
                }
            }
        }
        
        # Sleep and physical symptoms
        self.physical_indicators = {
            'sleep_issues': [
                'không ngủ được', 'mất ngủ', 'ngủ không say', 'thức đêm',
                'ngủ quá nhiều', 'khó ngủ', 'giấc ngủ không sâu',
                'can\'t sleep', 'insomnia', 'sleepless', 'restless sleep',
                'oversleeping', 'sleep too much', 'light sleep'
            ],
            'appetite_changes': [
                'không muốn ăn', 'mất cảm giác đói', 'ăn quá nhiều',
                'thay đổi khẩu vị', 'không ngon miệng',
                'no appetite', 'don\'t want to eat', 'eating too much',
                'taste changes', 'food doesn\'t taste good'
            ],
            'energy_loss': [
                'mệt mỏi', 'kiệt sức', 'không có năng lượng', 'uể oải',
                'lười biếng', 'không muốn làm gì', 'chán nản',
                'tired', 'exhausted', 'no energy', 'lethargic',
                'lazy', 'don\'t want to do anything', 'unmotivated'
            ]
        }
    
    def analyze_emotional_indicators(self, text: str) -> Dict[str, float]:
        """
        Analyze text for emotional indicators
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with emotional category scores (0.0 to 1.0)
        """
        text_lower = text.lower()
        results = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = self._calculate_emotion_score(text_lower, patterns)
            results[emotion] = min(score, 1.0)  # Cap at 1.0
        
        # Add physical indicator scores
        for category, keywords in self.physical_indicators.items():
            score = self._calculate_keyword_score(text_lower, keywords)
            results[category] = min(score, 1.0)
        
        return results
    
    def _calculate_emotion_score(self, text: str, patterns: Dict) -> float:
        """Calculate score for a specific emotion category"""
        score = 0.0
        
        # Keyword matching
        keyword_matches = 0
        for keyword in patterns['keywords']:
            if keyword in text:
                keyword_matches += 1
        
        # Base score from keywords
        if patterns['keywords']:
            keyword_score = keyword_matches / len(patterns['keywords'])
            score += keyword_score * 0.6  # 60% weight for keywords
        
        # Phrase matching (higher weight)
        phrase_matches = 0
        for phrase in patterns['phrases']:
            if phrase in text:
                phrase_matches += 1
        
        if patterns['phrases']:
            phrase_score = phrase_matches / len(patterns['phrases'])
            score += phrase_score * 0.4  # 40% weight for phrases
        
        # Apply intensity multipliers
        for intensity, multiplier in patterns['intensity_multipliers'].items():
            if intensity in text:
                score *= multiplier
                break  # Apply only first matched intensity
        
        return score
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate score based on keyword presence"""
        matches = sum(1 for keyword in keywords if keyword in text)
        return matches / len(keywords) if keywords else 0.0

class TransitionRuleEngine:
    """Rule-based engine for determining when to transition"""
    
    def __init__(self):
        self.emotion_analyzer = EmotionalIndicatorAnalyzer()
        
        # Transition thresholds
        self.thresholds = {
            'suicide_risk': 0.2,      # Very low threshold for safety
            'depression': 0.4,        # Moderate threshold
            'anxiety': 0.4,           # Moderate threshold
            'stress': 0.5,            # Higher threshold
            'combined_score': 0.3,    # Combined emotional distress
            'message_count': 6,       # Minimum messages before transition
            'max_messages': 12,       # Force transition point
            'time_based': 300         # 5 minutes conversation time
        }
        
        # Assessment type mapping
        self.assessment_mapping = {
            'suicide_risk': 'suicide_risk',
            'depression': 'phq9',
            'anxiety': 'gad7',
            'stress': 'dass21_stress'
        }
    
    def evaluate_transition(
        self, 
        messages: List[Dict], 
        conversation_state: Dict
    ) -> TransitionResult:
        """
        Evaluate whether conversation should transition to assessment
        
        Args:
            messages: List of conversation messages
            conversation_state: Current conversation state
            
        Returns:
            TransitionResult with decision and metadata
        """
        # Extract user messages
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        combined_text = ' '.join([msg['content'] for msg in user_messages])
        
        # Rule evaluations
        triggered_rules = []
        confidence_factors = []
        
        # Rule 1: Message count based
        message_count = len(user_messages)
        if message_count >= self.thresholds['max_messages']:
            triggered_rules.append('max_messages_reached')
            confidence_factors.append(1.0)
        
        # Rule 2: Emotional analysis
        emotional_scores = self.emotion_analyzer.analyze_emotional_indicators(combined_text)
        
        # Rule 3: Suicide risk check (highest priority)
        if emotional_scores.get('suicide_risk', 0) >= self.thresholds['suicide_risk']:
            return TransitionResult(
                should_transition=True,
                assessment_type='suicide_risk',
                confidence=1.0,
                reason='High suicide risk detected',
                triggered_rules=['suicide_risk_detected'],
                emotional_indicators=emotional_scores
            )
        
        # Rule 4: Individual emotion thresholds
        primary_emotion = None
        max_emotion_score = 0
        
        for emotion in ['depression', 'anxiety', 'stress']:
            score = emotional_scores.get(emotion, 0)
            if score >= self.thresholds[emotion]:
                triggered_rules.append(f'high_{emotion}_score')
                confidence_factors.append(score)
                
                if score > max_emotion_score:
                    max_emotion_score = score
                    primary_emotion = emotion
        
        # Rule 5: Combined emotional distress
        combined_score = self._calculate_combined_emotional_score(emotional_scores)
        if combined_score >= self.thresholds['combined_score']:
            triggered_rules.append('combined_emotional_distress')
            confidence_factors.append(combined_score)
        
        # Rule 6: Time-based transition (if conversation is long enough)
        conversation_duration = self._get_conversation_duration(conversation_state)
        if (conversation_duration >= self.thresholds['time_based'] and 
            message_count >= self.thresholds['message_count']):
            triggered_rules.append('time_based_transition')
            confidence_factors.append(0.6)
        
        # Rule 7: Progressive transition for sufficient conversation
        if (message_count >= self.thresholds['message_count'] and 
            combined_score >= 0.2):  # Lower threshold for longer conversations
            triggered_rules.append('progressive_transition')
            confidence_factors.append(0.5)
        
        # Decision logic
        should_transition = len(triggered_rules) > 0
        confidence = max(confidence_factors) if confidence_factors else 0.0
        
        # Determine assessment type
        assessment_type = self._determine_assessment_type(
            primary_emotion, emotional_scores, triggered_rules
        )
        
        # Generate reason
        reason = self._generate_transition_reason(triggered_rules, primary_emotion)
        
        return TransitionResult(
            should_transition=should_transition,
            assessment_type=assessment_type,
            confidence=confidence,
            reason=reason,
            triggered_rules=triggered_rules,
            emotional_indicators=emotional_scores
        )
    
    def _calculate_combined_emotional_score(self, emotional_scores: Dict[str, float]) -> float:
        """Calculate combined emotional distress score"""
        primary_emotions = ['depression', 'anxiety', 'stress']
        primary_scores = [emotional_scores.get(emotion, 0) for emotion in primary_emotions]
        
        # Weighted average with emphasis on highest scores
        if not primary_scores:
            return 0.0
        
        # Sort scores in descending order
        sorted_scores = sorted(primary_scores, reverse=True)
        
        # Weighted calculation: highest score gets more weight
        weights = [0.5, 0.3, 0.2]  # Weights for top 3 scores
        weighted_sum = sum(score * weight for score, weight in zip(sorted_scores, weights))
        
        # Add physical symptoms bonus
        physical_bonus = 0
        physical_categories = ['sleep_issues', 'appetite_changes', 'energy_loss']
        for category in physical_categories:
            if emotional_scores.get(category, 0) > 0.3:
                physical_bonus += 0.1
        
        return min(weighted_sum + physical_bonus, 1.0)
    
    def _get_conversation_duration(self, conversation_state: Dict) -> int:
        """Get conversation duration in seconds"""
        started_at = conversation_state.get('started_at')
        if not started_at:
            return 0
        
        try:
            start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            duration = (datetime.now() - start_time.replace(tzinfo=None)).total_seconds()
            return int(duration)
        except:
            return 0
    
    def _determine_assessment_type(
        self, 
        primary_emotion: Optional[str], 
        emotional_scores: Dict[str, float],
        triggered_rules: List[str]
    ) -> str:
        """Determine the most appropriate assessment type"""
        
        # Check for suicide risk first
        if 'suicide_risk_detected' in triggered_rules:
            return 'suicide_risk'
        
        # Use primary emotion if identified
        if primary_emotion:
            return self.assessment_mapping.get(primary_emotion, 'phq9')
        
        # Fallback logic based on highest score
        emotion_scores = {
            emotion: emotional_scores.get(emotion, 0) 
            for emotion in ['depression', 'anxiety', 'stress']
        }
        
        if not any(emotion_scores.values()):
            return 'phq9'  # Default to depression screening
        
        highest_emotion = max(emotion_scores, key=emotion_scores.get)
        return self.assessment_mapping.get(highest_emotion, 'phq9')
    
    def _generate_transition_reason(
        self, 
        triggered_rules: List[str], 
        primary_emotion: Optional[str]
    ) -> str:
        """Generate human-readable transition reason"""
        
        if 'suicide_risk_detected' in triggered_rules:
            return "Phát hiện dấu hiệu nguy cơ tự tử - cần đánh giá ngay lập tức"
        
        if 'max_messages_reached' in triggered_rules:
            return "Đã đạt số tin nhắn tối đa - chuyển sang đánh giá chi tiết"
        
        emotion_reasons = {
            'depression': "Phát hiện dấu hiệu trầm cảm - cần đánh giá PHQ-9",
            'anxiety': "Phát hiện dấu hiệu lo âu - cần đánh giá GAD-7", 
            'stress': "Phát hiện dấu hiệu căng thẳng - cần đánh giá DASS-21"
        }
        
        if primary_emotion and f'high_{primary_emotion}_score' in triggered_rules:
            return emotion_reasons.get(primary_emotion, "Cần đánh giá chuyên sâu")
        
        if 'combined_emotional_distress' in triggered_rules:
            return "Phát hiện nhiều dấu hiệu căng thẳng cảm xúc - cần đánh giá tổng hợp"
        
        if 'progressive_transition' in triggered_rules:
            return "Cuộc trò chuyện đủ dài với dấu hiệu cảm xúc - chuyển sang đánh giá"
        
        if 'time_based_transition' in triggered_rules:
            return "Đã trò chuyện đủ lâu - chuyển sang giai đoạn đánh giá"
        
        return "Cần chuyển sang đánh giá để hiểu rõ hơn tình trạng của bạn"

class ConversationAnalyzer:
    """Advanced conversation analysis for transition decisions"""
    
    def __init__(self):
        self.rule_engine = TransitionRuleEngine()
        
        # Pattern recognition for conversation flow
        self.conversation_patterns = {
            'repetitive_complaints': [
                r'tôi đã nói rồi', r'như tôi đã kể', r'lại cảm thấy',
                r'vẫn như vậy', r'không thay đổi gì'
            ],
            'escalating_distress': [
                r'ngày càng tệ', r'tệ hơn', r'không còn hy vọng',
                r'worse', r'getting worse', r'no hope'
            ],
            'ready_for_assessment': [
                r'tôi cần giúp đỡ', r'làm sao để', r'có cách nào',
                r'i need help', r'how can i', r'is there a way'
            ]
        }
    
    def analyze_conversation_readiness(
        self, 
        messages: List[Dict], 
        conversation_state: Dict
    ) -> Dict[str, Any]:
        """
        Analyze conversation for readiness indicators
        
        Returns:
            Dictionary with readiness analysis
        """
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        combined_text = ' '.join([msg['content'] for msg in user_messages])
        
        readiness_indicators = {}
        
        # Check for conversation patterns
        for pattern_name, patterns in self.conversation_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, combined_text, re.IGNORECASE))
            readiness_indicators[pattern_name] = matches > 0
        
        # Analyze conversation progression
        readiness_indicators.update({
            'sufficient_context': len(user_messages) >= 4,
            'emotional_disclosure': self._has_emotional_disclosure(user_messages),
            'help_seeking_behavior': self._detect_help_seeking(combined_text),
            'conversation_depth': self._assess_conversation_depth(user_messages)
        })
        
        return readiness_indicators
    
    def _has_emotional_disclosure(self, messages: List[Dict]) -> bool:
        """Check if user has disclosed emotional information"""
        emotional_keywords = [
            'cảm thấy', 'tôi', 'mình', 'cảm xúc', 'tâm trạng',
            'feel', 'i', 'me', 'emotion', 'mood', 'feeling'
        ]
        
        for msg in messages:
            content = msg['content'].lower()
            if any(keyword in content for keyword in emotional_keywords):
                return True
        return False
    
    def _detect_help_seeking(self, text: str) -> bool:
        """Detect help-seeking language"""
        help_patterns = [
            r'giúp tôi', r'làm sao', r'có cách nào', r'tôi nên',
            r'help me', r'how do i', r'what should i', r'can you help'
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in help_patterns)
    
    def _assess_conversation_depth(self, messages: List[Dict]) -> float:
        """Assess the depth of conversation (0.0 to 1.0)"""
        if not messages:
            return 0.0
        
        # Factors for conversation depth
        factors = []
        
        # Average message length
        avg_length = sum(len(msg['content']) for msg in messages) / len(messages)
        length_score = min(avg_length / 100, 1.0)  # Normalize to 100 chars
        factors.append(length_score)
        
        # Message count factor
        count_score = min(len(messages) / 8, 1.0)  # Normalize to 8 messages
        factors.append(count_score)
        
        # Personal pronoun usage (indicates personal sharing)
        combined_text = ' '.join([msg['content'] for msg in messages]).lower()
        personal_pronouns = ['tôi', 'mình', 'em', 'i', 'me', 'my', 'myself']
        pronoun_count = sum(combined_text.count(pronoun) for pronoun in personal_pronouns)
        pronoun_score = min(pronoun_count / 10, 1.0)  # Normalize to 10 uses
        factors.append(pronoun_score)
        
        return sum(factors) / len(factors)

class TransitionManager:
    """Main transition management system"""
    
    def __init__(self):
        self.conversation_analyzer = ConversationAnalyzer()
        self.rule_engine = TransitionRuleEngine()
    
    def should_transition(
        self, 
        messages: List[Dict], 
        conversation_state: Dict,
        force_evaluation: bool = False
    ) -> TransitionResult:
        """
        Main method to determine if conversation should transition
        
        Args:
            messages: Conversation history
            conversation_state: Current state
            force_evaluation: Force evaluation regardless of message count
            
        Returns:
            TransitionResult with decision and metadata
        """
        
        # Quick checks first
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        
        if not user_messages and not force_evaluation:
            return TransitionResult(
                should_transition=False,
                assessment_type='phq9',
                confidence=0.0,
                reason='No user messages to analyze',
                triggered_rules=[],
                emotional_indicators={}
            )
        
        # Analyze conversation readiness
        readiness = self.conversation_analyzer.analyze_conversation_readiness(
            messages, conversation_state
        )
        
        # Get rule-based evaluation
        transition_result = self.rule_engine.evaluate_transition(
            messages, conversation_state
        )
        
        # Adjust confidence based on readiness indicators
        readiness_boost = self._calculate_readiness_boost(readiness)
        transition_result.confidence = min(
            transition_result.confidence + readiness_boost, 1.0
        )
        
        # Add readiness context to the result
        if hasattr(transition_result, 'metadata'):
            transition_result.metadata.update(readiness)
        else:
            # If metadata doesn't exist, create it
            transition_result.metadata = readiness
        
        # Log transition decision
        logger.info(
            f"Transition evaluation: should_transition={transition_result.should_transition}, "
            f"type={transition_result.assessment_type}, "
            f"confidence={transition_result.confidence:.2f}, "
            f"rules={transition_result.triggered_rules}"
        )
        
        return transition_result
    
    def _calculate_readiness_boost(self, readiness: Dict[str, Any]) -> float:
        """Calculate confidence boost based on readiness indicators"""
        boost = 0.0
        
        if readiness.get('help_seeking_behavior'):
            boost += 0.2
        
        if readiness.get('emotional_disclosure'):
            boost += 0.1
        
        if readiness.get('ready_for_assessment'):
            boost += 0.15
        
        depth_score = readiness.get('conversation_depth', 0)
        boost += depth_score * 0.1
        
        return boost
    
    def get_transition_explanation(self, transition_result: TransitionResult) -> str:
        """
        Generate detailed explanation for the transition decision
        
        Args:
            transition_result: Result from transition evaluation
            
        Returns:
            Human-readable explanation
        """
        if not transition_result.should_transition:
            return "Cuộc trò chuyện chưa đủ thông tin để chuyển sang đánh giá."
        
        explanation_parts = [f"Lý do chuyển đổi: {transition_result.reason}"]
        
        # Add emotional indicators
        strong_indicators = [
            emotion for emotion, score in transition_result.emotional_indicators.items()
            if score > 0.4 and not emotion.startswith('_')
        ]
        
        if strong_indicators:
            explanation_parts.append(
                f"Các dấu hiệu cảm xúc quan trọng: {', '.join(strong_indicators)}"
            )
        
        # Add confidence level
        confidence_level = "cao" if transition_result.confidence > 0.7 else "trung bình" if transition_result.confidence > 0.4 else "thấp"
        explanation_parts.append(f"Độ tin cậy: {confidence_level} ({transition_result.confidence:.1%})")
        
        return ". ".join(explanation_parts)

# Factory function for easy integration
def create_transition_manager() -> TransitionManager:
    """Create and return a configured TransitionManager instance"""
    return TransitionManager()

# Utility function for quick transition check
def quick_transition_check(
    messages: List[Dict], 
    conversation_state: Dict
) -> Tuple[bool, str]:
    """
    Quick utility function for transition checking
    
    Returns:
        (should_transition, assessment_type)
    """
    manager = create_transition_manager()
    result = manager.should_transition(messages, conversation_state)
    return result.should_transition, result.assessment_type