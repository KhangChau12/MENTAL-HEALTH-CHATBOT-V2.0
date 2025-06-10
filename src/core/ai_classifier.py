"""
AI Classifier with Keyword Fallback
Robust classification system that solves the AI reliability issue
"""

import logging
import re
from typing import Dict, List, Optional
from ..services.together_ai import generate_chat_completion, extract_text_from_response

logger = logging.getLogger(__name__)

class AIClassifier:
    """AI-powered classification with robust fallback mechanisms"""
    
    def __init__(self):
        self.keyword_mappings = self._initialize_keyword_mappings()
        self.question_contexts = self._initialize_question_contexts()
    
    def classify_conversation_segment(self, message: str, history: List[Dict]) -> Dict[str, int]:
        """
        Classify conversation segment and return scores for relevant questions
        
        Args:
            message: Current user message
            history: Recent conversation history
            
        Returns:
            Dictionary mapping question_ids to severity scores (0-4)
        """
        scores = {}
        
        # Analyze the current message and recent history
        conversation_text = self._prepare_conversation_text(message, history)
        
        # Try to identify relevant mental health areas
        relevant_areas = self._identify_relevant_areas(conversation_text)
        
        for area in relevant_areas:
            question_ids = self._get_questions_for_area(area)
            
            for question_id in question_ids:
                try:
                    # Try AI classification first
                    score = self._classify_with_ai(conversation_text, question_id)
                    if score is not None:
                        scores[question_id] = score
                    else:
                        # Fallback to keyword classification
                        scores[question_id] = self._classify_with_keywords(conversation_text, question_id)
                except Exception as e:
                    logger.error(f"Classification error for {question_id}: {e}")
                    # Final fallback to keyword classification
                    scores[question_id] = self._classify_with_keywords(conversation_text, question_id)
        
        return scores
    
    def _prepare_conversation_text(self, message: str, history: List[Dict]) -> str:
        """Prepare conversation text for analysis"""
        texts = []
        
        # Add recent history (user messages only)
        for msg in history[-3:]:  # Last 3 messages
            if msg.get('role') == 'user':
                texts.append(msg.get('content', ''))
        
        # Add current message
        texts.append(message)
        
        return ' '.join(texts).lower()
    
    def _identify_relevant_areas(self, text: str) -> List[str]:
        """Identify which mental health areas are relevant to the conversation"""
        areas = []
        
        # Depression indicators
        depression_keywords = [
            'buồn', 'chán nản', 'tuyệt vọng', 'vô vọng', 'trầm cảm', 'sad', 'depressed', 'hopeless',
            'mệt mỏi', 'không hứng thú', 'mất động lực', 'tired', 'no interest', 'unmotivated'
        ]
        
        # Anxiety indicators  
        anxiety_keywords = [
            'lo lắng', 'hồi hộp', 'căng thẳng', 'sợ hãi', 'anxiety', 'worried', 'nervous', 'panic',
            'bồn chồn', 'bất an', 'restless', 'uneasy'
        ]
        
        # Stress indicators
        stress_keywords = [
            'căng thẳng', 'áp lực', 'quá tải', 'overwhelmed', 'pressure', 'stress',
            'không kiểm soát', 'out of control', 'racing thoughts'
        ]
        
        if any(keyword in text for keyword in depression_keywords):
            areas.append('depression')
        
        if any(keyword in text for keyword in anxiety_keywords):
            areas.append('anxiety')
            
        if any(keyword in text for keyword in stress_keywords):
            areas.append('stress')
        
        # If no specific area identified, default to depression (most common)
        if not areas:
            areas.append('depression')
        
        return areas
    
    def _get_questions_for_area(self, area: str) -> List[str]:
        """Get relevant question IDs for a mental health area"""
        question_mapping = {
            'depression': [
                'sad_feelings', 'lost_interest', 'sleep_issues', 'tired', 
                'appetite', 'worthless', 'concentration', 'psychomotor'
            ],
            'anxiety': [
                'worried', 'control_worry', 'worry_different', 'restless',
                'tired_easily', 'irritable', 'muscle_tension', 'sleep_difficulty'
            ],
            'stress': [
                'hard_wind_down', 'tend_overreact', 'upset_unexpected',
                'difficult_relax', 'down_sad', 'intolerant', 'stressed'
            ]
        }
        
        return question_mapping.get(area, [])
    
    def _classify_with_ai(self, conversation_text: str, question_id: str) -> Optional[int]:
        """
        Use AI to classify severity for a specific question
        
        Returns:
            Severity score 0-4, or None if AI classification fails
        """
        try:
            context = self.question_contexts.get(question_id, {})
            
            prompt = f"""TASK: Classify mental health symptom severity from conversation.

SYMPTOM: {context.get('description', question_id)}

SCALE:
0 = No symptoms/Never
1 = Minimal/Rarely  
2 = Mild/Sometimes
3 = Moderate/Often
4 = Severe/Always

CONVERSATION TEXT:
{conversation_text}

INSTRUCTIONS:
- Return ONLY a single number: 0, 1, 2, 3, or 4
- Base your assessment on evidence in the conversation
- If insufficient information, return 1
- No explanation needed

RESULT:"""

            messages = [
                {
                    "role": "system",
                    "content": "You are a mental health assessment expert. Classify symptom severity based on conversation content."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            response = generate_chat_completion(messages)
            if response:
                text = extract_text_from_response(response).strip()
                
                # Extract first number found
                match = re.search(r'[0-4]', text)
                if match:
                    return int(match.group())
            
            return None
            
        except Exception as e:
            logger.error(f"AI classification failed for {question_id}: {e}")
            return None
    
    def _classify_with_keywords(self, conversation_text: str, question_id: str) -> int:
        """
        Fallback keyword-based classification
        
        Returns:
            Severity score 0-4
        """
        keywords = self.keyword_mappings.get(question_id, {})
        
        # Check for keywords from high to low severity
        for severity in [4, 3, 2, 1, 0]:
            severity_keywords = keywords.get(severity, [])
            if any(keyword in conversation_text for keyword in severity_keywords):
                return severity
        
        # Default to minimal if no keywords found but area was identified
        return 1
    
    def _initialize_keyword_mappings(self) -> Dict[str, Dict[int, List[str]]]:
        """Initialize keyword mappings for fallback classification"""
        return {
            'sad_feelings': {
                4: ['cực kỳ buồn', 'tuyệt vọng hoàn toàn', 'extremely sad', 'completely hopeless'],
                3: ['rất buồn', 'thường xuyên buồn', 'very sad', 'frequently sad'],
                2: ['khá buồn', 'thỉnh thoảng buồn', 'somewhat sad', 'sometimes sad'],
                1: ['hơi buồn', 'ít khi buồn', 'slightly sad', 'rarely sad'],
                0: ['không buồn', 'vui vẻ', 'not sad', 'happy']
            },
            'lost_interest': {
                4: ['hoàn toàn mất hứng thú', 'không quan tâm gì', 'completely lost interest', 'no interest at all'],
                3: ['mất hứng thú nhiều', 'ít quan tâm', 'lost much interest', 'little interest'],
                2: ['giảm hứng thú', 'ít hứng thú hơn', 'decreased interest', 'less interested'],
                1: ['hơi mất hứng thú', 'slightly less interest'],
                0: ['vẫn hứng thú', 'quan tâm bình thường', 'still interested', 'normal interest']
            },
            'worried': {
                4: ['lo lắng liên tục', 'cực kỳ lo âu', 'constantly worried', 'extremely anxious'],
                3: ['thường xuyên lo', 'rất lo lắng', 'frequently worried', 'very anxious'],
                2: ['khá lo lắng', 'đôi khi lo', 'somewhat worried', 'sometimes anxious'],
                1: ['hơi lo', 'ít khi lo', 'slightly worried', 'rarely worried'],
                0: ['không lo', 'bình tĩnh', 'not worried', 'calm']
            },
            'tired': {
                4: ['kiệt sức hoàn toàn', 'mệt mỏi cực độ', 'completely exhausted', 'extremely tired'],
                3: ['rất mệt', 'thường xuyên mệt', 'very tired', 'frequently tired'],
                2: ['khá mệt', 'thỉnh thoảng mệt', 'quite tired', 'sometimes tired'],
                1: ['hơi mệt', 'ít khi mệt', 'slightly tired', 'rarely tired'],
                0: ['đầy năng lượng', 'không mệt', 'energetic', 'not tired']
            },
            'sleep_issues': {
                4: ['không ngủ được', 'mất ngủ hoàn toàn', 'cannot sleep', 'complete insomnia'],
                3: ['khó ngủ thường xuyên', 'frequently cannot sleep'],
                2: ['thỉnh thoảng khó ngủ', 'sometimes trouble sleeping'],
                1: ['hiếm khi khó ngủ', 'rarely trouble sleeping'],
                0: ['ngủ tốt', 'không vấn đề gì', 'sleep well', 'no problems']
            },
            'worthless': {
                4: ['hoàn toàn vô giá trị', 'completely worthless'],
                3: ['cảm thấy vô dụng', 'feel useless'],
                2: ['đôi khi cảm thấy vô nghĩa', 'sometimes feel meaningless'],
                1: ['hiếm khi tự ti', 'rarely feel inferior'],
                0: ['tự tin', 'có giá trị', 'confident', 'valuable']
            }
        }
    
    def _initialize_question_contexts(self) -> Dict[str, Dict[str, str]]:
        """Initialize question contexts for AI classification"""
        return {
            'sad_feelings': {
                'description': 'Feelings of sadness, depression, or hopelessness'
            },
            'lost_interest': {
                'description': 'Loss of interest or pleasure in activities'
            },
            'sleep_issues': {
                'description': 'Trouble falling asleep, staying asleep, or sleeping too much'
            },
            'tired': {
                'description': 'Feeling tired or having little energy'
            },
            'appetite': {
                'description': 'Poor appetite or overeating'
            },
            'worthless': {
                'description': 'Feeling bad about yourself or that you are a failure'
            },
            'concentration': {
                'description': 'Trouble concentrating on things'
            },
            'worried': {
                'description': 'Feeling nervous, anxious, or on edge'
            },
            'control_worry': {
                'description': 'Not being able to stop or control worrying'
            },
            'restless': {
                'description': 'Being so restless that it is hard to sit still'
            },
            'irritable': {
                'description': 'Being easily annoyed or irritable'
            }
        }