"""
Scoring Engine - Calculate assessment scores and severity levels
"""

import logging
from typing import Dict, List, Optional, Tuple
from config import Config

logger = logging.getLogger(__name__)

class ScoringEngine:
    """Calculate scores and determine severity levels for mental health assessments"""
    
    def __init__(self):
        self.scoring_ranges = Config.SCORING_RANGES
        self.interpretations = self._initialize_interpretations()
    
    def calculate_score(self, assessment_type: str, responses: Dict) -> Dict:
        """
        Calculate total score and determine severity level
        
        Args:
            assessment_type: Type of assessment (phq9, gad7, etc.)
            responses: Dictionary of question responses with scores
            
        Returns:
            Dictionary with score, severity, and interpretation
        """
        try:
            # Calculate total score
            total_score = sum(response['score'] for response in responses.values())
            
            # Determine severity based on assessment type
            severity = self._determine_severity(assessment_type, total_score)
            
            # Get interpretation
            interpretation = self._get_interpretation(assessment_type, severity)
            
            # Generate recommendations
            recommendations = self._get_recommendations(assessment_type, severity, total_score)
            
            # Check for high-risk indicators
            risk_level = self._assess_risk_level(assessment_type, responses, total_score)
            
            return {
                'total_score': total_score,
                'severity': severity,
                'interpretation': interpretation,
                'recommendations': recommendations,
                'risk_level': risk_level,
                'breakdown': self._create_score_breakdown(responses),
                'calculated_at': None  # Will be set by calling function
            }
            
        except Exception as e:
            logger.error(f"Error calculating score for {assessment_type}: {e}")
            return self._create_default_results()
    
    def _determine_severity(self, assessment_type: str, total_score: int) -> str:
        """Determine severity level based on total score"""
        
        ranges = self.scoring_ranges.get(assessment_type, {})
        
        for severity, (min_score, max_score) in ranges.items():
            if min_score <= total_score <= max_score:
                return severity
        
        # Fallback for unknown ranges
        if total_score == 0:
            return 'minimal'
        elif total_score <= 5:
            return 'mild'
        elif total_score <= 10:
            return 'moderate'
        else:
            return 'severe'
    
    def _get_interpretation(self, assessment_type: str, severity: str) -> str:
        """Get detailed interpretation for the assessment results"""
        
        interpretations = self.interpretations.get(assessment_type, {})
        return interpretations.get(severity, "Kết quả cần được đánh giá bởi chuyên gia.")
    
    def _get_recommendations(self, assessment_type: str, severity: str, score: int) -> List[str]:
        """Generate recommendations based on assessment results"""
        
        recommendations = []
        
        # General recommendations based on severity
        if severity in ['minimal', 'normal']:
            recommendations.extend([
                "Duy trì lối sống lành mạnh với chế độ ăn uống cân bằng và tập thể dục đều đặn",
                "Thực hành kỹ thuật quản lý căng thẳng như thiền định hoặc yoga",
                "Duy trì mối quan hệ xã hội tích cực"
            ])
        
        elif severity == 'mild':
            recommendations.extend([
                "Theo dõi tình trạng tâm lý của bạn trong vài tuần tới",
                "Tìm hiểu các kỹ thuật tự chăm sóc sức khỏe tâm thần",
                "Cân nhắc tham gia các hoạt động giải trí và thư giãn",
                "Nếu triệu chứng không cải thiện, hãy tham khảo ý kiến chuyên gia"
            ])
        
        elif severity in ['moderate', 'moderately_severe']:
            recommendations.extend([
                "Khuyến khích tham khảo ý kiến từ chuyên gia sức khỏe tâm thần",
                "Cân nhắc liệu pháp tâm lý nhận thức hành vi (CBT)",
                "Tham gia các nhóm hỗ trợ hoặc cộng đồng có cùng tình trạng",
                "Thiết lập thói quen hàng ngày có cấu trúc và mục tiêu rõ ràng"
            ])
        
        elif severity in ['severe', 'extremely_severe']:
            recommendations.extend([
                "⚠️ Khuyến khích mạnh mẽ tìm kiếm sự hỗ trợ chuyên nghiệp ngay lập tức",
                "Liên hệ với bác sĩ tâm thần hoặc chuyên gia sức khỏe tâm thần",
                "Cân nhắc điều trị kết hợp (thuốc + tâm lý trị liệu)",
                "Tìm kiếm sự hỗ trợ từ gia đình và bạn bè",
                "Nếu có ý định tự làm hại bản thân, hãy gọi đường dây nóng khẩn cấp"
            ])
        
        # Assessment-specific recommendations
        if assessment_type == 'phq9':
            if score >= 10:
                recommendations.append("Cân nhắc đánh giá thêm về nguy cơ tự tử")
        
        elif assessment_type == 'gad7':
            if score >= 10:
                recommendations.extend([
                    "Thực hành kỹ thuật thở sâu và thư giãn cơ bắp",
                    "Học các chiến lược quản lý lo âu và căng thẳng"
                ])
        
        elif assessment_type == 'dass21_stress':
            if score >= 19:
                recommendations.extend([
                    "Đánh giá và giảm các nguồn căng thẳng trong cuộc sống",
                    "Học kỹ năng quản lý thời gian và ưu tiên công việc"
                ])
        
        return recommendations
    
    def _assess_risk_level(self, assessment_type: str, responses: Dict, total_score: int) -> str:
        """Assess overall risk level based on responses and score"""
        
        # Check for high-risk responses
        high_risk_questions = {
            'phq9': ['suicide_thoughts', 'death_wish'],
            'gad7': [],
            'dass21_stress': []
        }
        
        high_risk_ids = high_risk_questions.get(assessment_type, [])
        
        # Check for concerning responses
        for question_id, response in responses.items():
            if question_id in high_risk_ids and response['score'] >= 2:
                return 'high'
        
        # Risk based on total score
        if assessment_type == 'phq9':
            if total_score >= 20:
                return 'high'
            elif total_score >= 15:
                return 'moderate'
            elif total_score >= 5:
                return 'low'
        
        elif assessment_type == 'gad7':
            if total_score >= 15:
                return 'high'
            elif total_score >= 10:
                return 'moderate'
            elif total_score >= 5:
                return 'low'
        
        elif assessment_type == 'dass21_stress':
            if total_score >= 34:
                return 'high'
            elif total_score >= 19:
                return 'moderate'
            elif total_score >= 15:
                return 'low'
        
        return 'minimal'
    
    def _create_score_breakdown(self, responses: Dict) -> Dict:
        """Create detailed breakdown of responses"""
        breakdown = {}
        
        for question_id, response in responses.items():
            breakdown[question_id] = {
                'score': response['score'],
                'answered_at': response.get('answered_at'),
                'raw_response': response.get('raw_response', '')
            }
        
        return breakdown
    
    def _create_default_results(self) -> Dict:
        """Create default results when calculation fails"""
        return {
            'total_score': 0,
            'severity': 'unknown',
            'interpretation': 'Không thể tính toán kết quả. Vui lòng thử lại.',
            'recommendations': ['Tham khảo ý kiến chuyên gia sức khỏe tâm thần'],
            'risk_level': 'unknown',
            'breakdown': {},
            'error': True
        }
    
    def _initialize_interpretations(self) -> Dict[str, Dict[str, str]]:
        """Initialize interpretation texts for different severities"""
        return {
            'phq9': {
                'minimal': """Kết quả cho thấy mức độ trầm cảm tối thiểu. Bạn đang có sức khỏe tâm thần tương đối tốt. 
                
Điều này có nghĩa là bạn hiếm khi hoặc không trải qua các triệu chứng trầm cảm như buồn bã, mất hứng thú hoặc cảm giác vô vọng.""",
                
                'mild': """Kết quả cho thấy mức độ trầm cảm nhẹ. Bạn có thể đang trải qua một số triệu chứng trầm cảm nhưng chưa ảnh hưởng nghiêm trọng đến cuộc sống hàng ngày.
                
Đây là thời điểm tốt để chú ý đến sức khỏe tâm thần và thực hiện các biện pháp tự chăm sóc.""",
                
                'moderate': """Kết quả cho thấy mức độ trầm cảm trung bình. Các triệu chứng có thể đang ảnh hưởng đến công việc, học tập hoặc các mối quan hệ của bạn.
                
Khuyến khích tìm kiếm sự hỗ trợ từ chuyên gia để được đánh giá và tư vấn thêm.""",
                
                'moderately_severe': """Kết quả cho thấy mức độ trầm cảm khá nghiêm trọng. Các triệu chứng có thể đang gây ra khó khăn đáng kể trong cuộc sống hàng ngày.
                
Rất khuyến khích tham khảo ý kiến từ chuyên gia sức khỏe tâm thần để được hỗ trợ và điều trị phù hợp.""",
                
                'severe': """Kết quả cho thấy mức độ trầm cảm nghiêm trọng. Đây là tình trạng cần được can thiệp chuyên nghiệp ngay lập tức.
                
Vui lòng liên hệ với bác sĩ hoặc chuyên gia sức khỏe tâm thần để được đánh giá và điều trị kịp thời."""
            },
            
            'gad7': {
                'minimal': """Kết quả cho thấy mức độ lo âu tối thiểu. Bạn hiếm khi trải qua lo lắng hoặc căng thẳng quá mức.
                
Đây là dấu hiệu tích cực cho thấy bạn đang quản lý tốt căng thẳng trong cuộc sống.""",
                
                'mild': """Kết quả cho thấy mức độ lo âu nhẹ. Bạn có thể thỉnh thoảng cảm thấy lo lắng nhưng vẫn có thể kiểm soát được.
                
Học các kỹ thuật thư giãn có thể giúp bạn quản lý tốt hơn những cảm giác này.""",
                
                'moderate': """Kết quả cho thấy mức độ lo âu trung bình. Lo lắng có thể đang ảnh hưởng đến một số khía cạnh trong cuộc sống của bạn.
                
Cân nhắc tìm hiểu các phương pháp quản lý lo âu hoặc tham khảo ý kiến chuyên gia.""",
                
                'severe': """Kết quả cho thấy mức độ lo âu nghiêm trọng. Lo lắng có thể đang gây ra khó khăn đáng kể trong cuộc sống hàng ngày.
                
Khuyến khích mạnh mẽ tìm kiếm sự hỗ trợ từ chuyên gia sức khỏe tâm thần."""
            },
            
            'dass21_stress': {
                'normal': """Kết quả cho thấy mức độ căng thẳng bình thường. Bạn đang quản lý tốt các áp lực trong cuộc sống.
                
Hãy tiếp tục duy trì các thói quen tích cực hiện tại.""",
                
                'mild': """Kết quả cho thấy mức độ căng thẳng nhẹ. Bạn có thể đang trải qua một số áp lực nhưng vẫn trong tầm kiểm soát.
                
Thực hành các kỹ thuật giảm stress có thể giúp ích.""",
                
                'moderate': """Kết quả cho thấy mức độ căng thẳng trung bình. Áp lực có thể đang ảnh hưởng đến sức khỏe và hiệu suất của bạn.
                
Cân nhắc đánh giá lại các nguồn căng thẳng và tìm cách giảm thiểu.""",
                
                'severe': """Kết quả cho thầy mức độ căng thẳng nghiêm trọng. Bạn có thể đang trải qua quá nhiều áp lực.
                
Khuyến khích tìm kiếm sự hỗ trợ để học cách quản lý căng thẳng hiệu quả hơn.""",
                
                'extremely_severe': """Kết quả cho thấy mức độ căng thẳng cực kỳ cao. Đây là tình trạng cần được can thiệp ngay lập tức.
                
Vui lòng tìm kiếm sự hỗ trợ chuyên nghiệp để bảo vệ sức khỏe tâm thần của bạn."""
            }
        }