"""
Assessment Engine - Manages structured questionnaires and scoring
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .scoring import ScoringEngine
from ..utils.constants import AssessmentTypes, QuestionTypes
from data.questionnaires import questionnaires
from config import Config

logger = logging.getLogger(__name__)

class AssessmentEngine:
    """Manages assessment questionnaires and progression"""
    
    def __init__(self):
        self.scoring_engine = ScoringEngine()
        self.questionnaires = questionnaires
    
    def start_assessment(self, assessment_type: str, state: Dict) -> Dict:
        """
        Start a new assessment
        
        Args:
            assessment_type: Type of assessment (phq9, gad7, etc.)
            state: Current chat state
            
        Returns:
            Response with first question and updated state
        """
        try:
            # Validate assessment type
            if assessment_type not in self.questionnaires:
                logger.error(f"Invalid assessment type: {assessment_type}")
                assessment_type = AssessmentTypes.PHQ9
            
            questionnaire = self.questionnaires[assessment_type]
            first_question = questionnaire['questions'][0]
            
            # Initialize assessment state
            assessment_state = {
                'type': assessment_type,
                'current_question_index': 0,
                'responses': {},
                'started_at': datetime.now().isoformat(),
                'total_questions': len(questionnaire['questions'])
            }
            
            # Update main state
            new_state = {
                **state,
                'current_phase': 'assessment',
                'assessment': assessment_state
            }
            
            # Format first question
            question_text = self._format_question(first_question, 0, len(questionnaire['questions']))
            
            return {
                'message': question_text,
                'state': new_state,
                'metadata': {
                    'type': 'assessment_question',
                    'assessment_type': assessment_type,
                    'question_index': 0,
                    'total_questions': len(questionnaire['questions'])
                }
            }
            
        except Exception as e:
            logger.error(f"Error starting assessment: {e}")
            return self._create_error_response("Không thể bắt đầu đánh giá")
    
    def process_assessment_response(self, response: str, state: Dict) -> Dict:
        """
        Process user response to assessment question
        
        Args:
            response: User's response
            state: Current state with assessment info
            
        Returns:
            Next question or completion response
        """
        try:
            assessment_state = state.get('assessment', {})
            assessment_type = assessment_state.get('type')
            current_index = assessment_state.get('current_question_index', 0)
            
            # Validate assessment state
            if not assessment_type or assessment_type not in self.questionnaires:
                return self._create_error_response("Phiên đánh giá không hợp lệ")
            
            questionnaire = self.questionnaires[assessment_type]
            
            # Parse and validate response
            score = self._parse_response(response, questionnaire['questions'][current_index])
            if score is None:
                return self._request_clarification(current_index, questionnaire)
            
            # Store response
            question_id = questionnaire['questions'][current_index]['id']
            assessment_state['responses'][question_id] = {
                'score': score,
                'raw_response': response,
                'answered_at': datetime.now().isoformat()
            }
            
            # Check if assessment is complete
            next_index = current_index + 1
            if next_index >= len(questionnaire['questions']):
                return self._complete_assessment(assessment_state, state)
            
            # Move to next question
            assessment_state['current_question_index'] = next_index
            next_question = questionnaire['questions'][next_index]
            
            # Update state
            new_state = {
                **state,
                'assessment': assessment_state
            }
            
            # Format next question
            question_text = self._format_question(
                next_question, 
                next_index, 
                len(questionnaire['questions'])
            )
            
            return {
                'message': question_text,
                'state': new_state,
                'metadata': {
                    'type': 'assessment_question',
                    'assessment_type': assessment_type,
                    'question_index': next_index,
                    'total_questions': len(questionnaire['questions']),
                    'progress': (next_index / len(questionnaire['questions'])) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing assessment response: {e}")
            return self._create_error_response("Lỗi khi xử lý câu trả lời")
    
    def _parse_response(self, response: str, question: Dict) -> Optional[int]:
        """
        Parse user response to extract score
        
        Args:
            response: User's response
            question: Question configuration
            
        Returns:
            Score (0-4) or None if invalid
        """
        response = response.strip().lower()
        
        # Try to extract number directly
        import re
        number_match = re.search(r'\b([0-4])\b', response)
        if number_match:
            return int(number_match.group(1))
        
        # Try keyword matching for Vietnamese responses
        vietnamese_mappings = {
            0: ['không bao giờ', 'không', 'không có', 'chưa bao giờ', 'never', 'not at all'],
            1: ['hiếm khi', 'ít khi', 'thỉnh thoảng', 'several days', 'rarely'],
            2: ['thỉnh thoảng', 'đôi khi', 'vừa phải', 'more than half', 'sometimes'],
            3: ['thường xuyên', 'nhiều lần', 'gần như mỗi ngày', 'nearly every day', 'often'],
            4: ['luôn luôn', 'liên tục', 'mỗi ngày', 'always', 'every day']
        }
        
        # Check each score level
        for score, keywords in vietnamese_mappings.items():
            if any(keyword in response for keyword in keywords):
                return score
        
        # Try to match with answer options if provided
        if 'options' in question:
            for i, option in enumerate(question['options']):
                if option.lower() in response or str(i) in response:
                    return i
        
        return None
    
    def _format_question(self, question: Dict, index: int, total: int) -> str:
        """Format question with options and progress"""
        
        # Progress indicator
        progress = f"Câu {index + 1}/{total}"
        
        # Question text
        question_text = question['text']
        
        # Add options if available
        options_text = ""
        if 'options' in question:
            options_text = "\n\nTùy chọn:\n"
            for i, option in enumerate(question['options']):
                options_text += f"{i}. {option}\n"
        
        # Instructions
        instructions = "\n\nVui lòng trả lời bằng số (0-4) hoặc mô tả cảm giác của bạn."
        
        return f"**{progress}**\n\n{question_text}{options_text}{instructions}"
    
    def _request_clarification(self, current_index: int, questionnaire: Dict) -> Dict:
        """Request clarification for unclear response"""
        question = questionnaire['questions'][current_index]
        
        clarification_text = f"""Tôi chưa hiểu rõ câu trả lời của bạn. 

**Câu hỏi:** {question['text']}

Vui lòng trả lời bằng:
- Số từ 0 đến 4, hoặc
- Mô tả rõ ràng mức độ bạn trải qua"""
        
        return {
            'message': clarification_text,
            'state': {},  # Keep current state unchanged
            'metadata': {
                'type': 'clarification',
                'needs_clarification': True
            }
        }
    
    def _complete_assessment(self, assessment_state: Dict, full_state: Dict) -> Dict:
        """Complete assessment and calculate results"""
        try:
            assessment_type = assessment_state['type']
            responses = assessment_state['responses']
            
            # Calculate score and severity
            results = self.scoring_engine.calculate_score(assessment_type, responses)
            
            # Update state with results
            assessment_state.update({
                'completed_at': datetime.now().isoformat(),
                'results': results,
                'status': 'completed'
            })
            
            new_state = {
                **full_state,
                'assessment': assessment_state,
                'current_phase': 'results'
            }
            
            # Generate results message
            results_message = self._format_results(assessment_type, results)
            
            return {
                'message': results_message,
                'state': new_state,
                'metadata': {
                    'type': 'assessment_complete',
                    'assessment_type': assessment_type,
                    'results': results
                }
            }
            
        except Exception as e:
            logger.error(f"Error completing assessment: {e}")
            return self._create_error_response("Lỗi khi tính toán kết quả")
    
    def _format_results(self, assessment_type: str, results: Dict) -> str:
        """Format assessment results for display"""
        
        questionnaire = self.questionnaires.get(assessment_type, {})
        title = questionnaire.get('title', assessment_type.upper())
        
        score = results.get('total_score', 0)
        severity = results.get('severity', 'unknown')
        interpretation = results.get('interpretation', '')
        
        # Map severity to Vietnamese
        severity_mapping = {
            'minimal': 'Tối thiểu',
            'mild': 'Nhẹ',
            'moderate': 'Trung bình',
            'moderately_severe': 'Trung bình nặng',
            'severe': 'Nặng',
            'extremely_severe': 'Cực kỳ nặng',
            'normal': 'Bình thường'
        }
        
        severity_vn = severity_mapping.get(severity, severity)
        
        result_text = f"""**🎯 KẾT QUẢ ĐÁNH GIÁ - {title}**

**Điểm số:** {score}
**Mức độ:** {severity_vn}

**Giải thích:**
{interpretation}

**Lưu ý quan trọng:**
Đây chỉ là kết quả sàng lọc sơ bộ, không phải chẩn đoán y tế. Nếu bạn có những lo ngại về sức khỏe tâm thần, hãy tham khảo ý kiến chuyên gia.

Bạn có muốn xuất kết quả này không? Tôi có thể tạo báo cáo PDF hoặc JSON cho bạn."""
        
        return result_text
    
    def _create_error_response(self, message: str) -> Dict:
        """Create error response"""
        return {
            'message': message,
            'state': {},
            'metadata': {
                'type': 'error',
                'error': True
            }
        }