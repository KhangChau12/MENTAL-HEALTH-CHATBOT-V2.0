"""
Conversation Analyzer - Phân tích độ sâu cuộc trò chuyện và temporal indicators
Đánh giá chất lượng và mức độ personal sharing trong conversation
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationAnalyzer:
    """Phân tích độ sâu cuộc trò chuyện và temporal indicators"""
    
    def __init__(self):
        # Personal sharing indicators
        self.personal_indicators = {
            'pronouns': ['tôi', 'mình', 'em', 'con', 'i', 'me', 'my', 'myself'],
            'emotional_expressions': [
                'cảm thấy', 'suy nghĩ', 'lo lắng', 'buồn', 'vui', 'giận',
                'feel', 'think', 'worry', 'sad', 'happy', 'angry'
            ],
            'sharing_markers': [
                'chia sẻ', 'nói thật', 'thực ra', 'thường', 'luôn luôn',
                'share', 'honestly', 'actually', 'usually', 'always'
            ],
            'vulnerability_markers': [
                'khó khăn', 'đau khổ', 'không biết', 'bối rối', 'hoang mang',
                'difficult', 'struggling', 'confused', 'lost', 'helpless'
            ]
        }
        
        # Temporal indicators mapping
        self.temporal_patterns = {
            # Ngắn hạn (severity thấp)
            r'\b(hôm nay|hôm qua|sáng nay|chiều nay|tối nay)\b': 0.1,
            r'\b(today|yesterday|this morning|this afternoon|tonight)\b': 0.1,
            
            # Trung hạn (severity trung bình)
            r'\b(tuần này|tuần trước|mấy ngày|vài ngày)\b': 0.4,
            r'\b(this week|last week|few days|several days)\b': 0.4,
            r'\b(\d+\s*ngày)\b': 0.3,
            
            # Dài hạn (severity cao)
            r'\b(2\s*tuần|hai tuần|mấy tuần)\b': 0.8,
            r'\b(tháng này|tháng trước|mấy tháng)\b': 0.7,
            r'\b(2\s*weeks|two weeks|few weeks|few months)\b': 0.8,
            r'\b(\d+\s*tháng|\d+\s*months)\b': 0.8,
            
            # Rất dài hạn (severity rất cao)
            r'\b(suốt|liên tục|mãi mãi|từ lúc|kể từ)\b': 0.9,
            r'\b(constantly|continuously|always|since|ever since)\b': 0.9,
        }

    def analyze_message_depth(self, message: str) -> float:
        """
        Đánh giá độ sâu của một tin nhắn đơn lẻ
        
        Params:
            - message: Nội dung tin nhắn
        
        Return: Depth score 0.0-1.0
        """
        if not message or not message.strip():
            return 0.0
        
        message_lower = message.lower()
        scores = []
        
        # 1. Độ dài tin nhắn (30% weight)
        length_score = min(len(message) / 100, 1.0)  # Normalize to 100 chars
        scores.append(('length', length_score, 0.3))
        
        # 2. Personal pronoun usage (25% weight)
        pronoun_count = sum(1 for pronoun in self.personal_indicators['pronouns'] 
                          if pronoun in message_lower)
        pronoun_score = min(pronoun_count / 3, 1.0)  # Normalize to 3 uses
        scores.append(('pronouns', pronoun_score, 0.25))
        
        # 3. Emotional expression (25% weight)
        emotion_count = sum(1 for emotion in self.personal_indicators['emotional_expressions']
                          if emotion in message_lower)
        emotion_score = min(emotion_count / 2, 1.0)  # Normalize to 2 expressions
        scores.append(('emotions', emotion_score, 0.25))
        
        # 4. Vulnerability markers (20% weight)
        vulnerability_count = sum(1 for marker in self.personal_indicators['vulnerability_markers']
                                if marker in message_lower)
        vulnerability_score = min(vulnerability_count / 2, 1.0)
        scores.append(('vulnerability', vulnerability_score, 0.2))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        
        logger.debug(f"Message depth analysis: {scores} -> {total_score:.2f}")
        return total_score

    def calculate_progressive_depth(self, history: List[Dict]) -> float:
        """
        Tính độ sâu tích lũy qua cuộc trò chuyện
        
        Params:
            - history: Lịch sử tin nhắn
        
        Return: Overall depth score 0.0-1.0
        """
        if not history:
            return 0.0
        
        # Lấy chỉ user messages
        user_messages = [msg for msg in history if msg.get('role') == 'user']
        if not user_messages:
            return 0.0
        
        # Tính depth cho từng message
        message_depths = []
        for i, msg in enumerate(user_messages):
            depth = self.analyze_message_depth(msg['content'])
            
            # Recent messages có weight cao hơn
            recency_weight = 1.0 + (i / len(user_messages)) * 0.5  # 1.0 to 1.5
            weighted_depth = depth * recency_weight
            message_depths.append(weighted_depth)
        
        # Tính progressive depth
        if len(message_depths) == 1:
            return message_depths[0]
        
        # Weight recent messages more heavily
        weights = [1.0 + i * 0.3 for i in range(len(message_depths))]  # Increasing weights
        weighted_sum = sum(depth * weight for depth, weight in zip(message_depths, weights))
        total_weight = sum(weights)
        
        progressive_depth = weighted_sum / total_weight
        
        # Cap at 1.0
        return min(progressive_depth, 1.0)

    def detect_temporal_indicators(self, text: str) -> List[str]:
        """
        Phát hiện các từ chỉ thời gian
        
        Params:
            - text: Text để phân tích
        
        Return: List temporal indicators ['2 tuần', 'gần đây', 'suốt tháng']
        """
        if not text:
            return []
        
        indicators = []
        text_lower = text.lower()
        
        for pattern, _ in self.temporal_patterns.items():
            matches = re.findall(pattern, text_lower)
            indicators.extend(matches)
        
        # Remove duplicates while preserving order
        unique_indicators = []
        for indicator in indicators:
            if indicator not in unique_indicators:
                unique_indicators.append(indicator)
        
        logger.debug(f"Detected temporal indicators: {unique_indicators}")
        return unique_indicators

    def score_duration_severity(self, indicators: List[str]) -> float:
        """
        Chuyển temporal indicators thành severity score
        
        Params:
            - indicators: List từ detect_temporal_indicators()
        
        Return: Duration severity score 0.0-1.0
        """
        if not indicators:
            return 0.0
        
        scores = []
        text_to_match = ' '.join(indicators).lower()
        
        for pattern, severity in self.temporal_patterns.items():
            if re.search(pattern, text_to_match):
                scores.append(severity)
        
        if not scores:
            return 0.0
        
        # Sử dụng max score (worst case scenario)
        max_score = max(scores)
        
        # Bonus nếu có nhiều indicators
        if len(indicators) > 1:
            max_score = min(max_score * 1.2, 1.0)
        
        logger.debug(f"Duration severity: {indicators} -> {max_score:.2f}")
        return max_score

    def analyze_conversation_context(self, history: List[Dict]) -> Dict:
        """
        Phân tích toàn diện context của cuộc trò chuyện
        
        Params:
            - history: Lịch sử cuộc trò chuyện
        
        Return: Dict chứa tất cả analysis results
        """
        user_messages = [msg for msg in history if msg.get('role') == 'user']
        
        if not user_messages:
            return {
                'depth_score': 0.0,
                'duration_score': 0.0,
                'message_count': 0,
                'temporal_indicators': [],
                'avg_message_length': 0,
                'personal_sharing_level': 'low'
            }
        
        # Combine all user text for temporal analysis
        combined_text = ' '.join([msg['content'] for msg in user_messages])
        
        # Calculate metrics
        depth_score = self.calculate_progressive_depth(history)
        temporal_indicators = self.detect_temporal_indicators(combined_text)
        duration_score = self.score_duration_severity(temporal_indicators)
        
        # Additional metrics
        avg_length = sum(len(msg['content']) for msg in user_messages) / len(user_messages)
        
        # Determine personal sharing level
        if depth_score >= 0.7:
            sharing_level = 'high'
        elif depth_score >= 0.4:
            sharing_level = 'medium'
        else:
            sharing_level = 'low'
        
        return {
            'depth_score': depth_score,
            'duration_score': duration_score,
            'message_count': len(user_messages),
            'temporal_indicators': temporal_indicators,
            'avg_message_length': avg_length,
            'personal_sharing_level': sharing_level
        }

# Convenience functions
def analyze_message_depth(message: str) -> float:
    """Convenience function để phân tích một message"""
    analyzer = ConversationAnalyzer()
    return analyzer.analyze_message_depth(message)

def calculate_progressive_depth(history: List[Dict]) -> float:
    """Convenience function để tính progressive depth"""
    analyzer = ConversationAnalyzer()
    return analyzer.calculate_progressive_depth(history)

def detect_temporal_indicators(text: str) -> List[str]:
    """Convenience function để detect temporal indicators"""
    analyzer = ConversationAnalyzer()
    return analyzer.detect_temporal_indicators(text)

def score_duration_severity(indicators: List[str]) -> float:
    """Convenience function để score duration severity"""
    analyzer = ConversationAnalyzer()
    return analyzer.score_duration_severity(indicators)