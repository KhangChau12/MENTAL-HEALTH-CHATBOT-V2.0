"""
Mental Health Assessment Questionnaires
Standard validated questionnaires for mental health screening
"""

questionnaires = {
    "phq9": {
        "title": "PHQ-9 - Bộ câu hỏi sàng lọc Trầm cảm",
        "description": "Bộ câu hỏi Patient Health Questionnaire-9 được sử dụng rộng rãi để sàng lọc và đánh giá mức độ nghiêm trọng của trầm cảm.",
        "category": "depression",
        "estimated_time": "3-5 phút",
        "question_count": 9,
        "scoring_info": {
            "max_score": 27,
            "ranges": {
                "minimal": "0-4",
                "mild": "5-9", 
                "moderate": "10-14",
                "moderately_severe": "15-19",
                "severe": "20-27"
            }
        },
        "instructions": [
            "Trong 2 tuần qua, bạn có thường xuyên gặp phải các vấn đề sau không?",
            "Hãy trả lời dựa trên cảm giác thực tế của bạn",
            "Thang điểm: 0 = Không bao giờ, 1 = Vài ngày, 2 = Hơn một nửa số ngày, 3 = Gần như mỗi ngày"
        ],
        "disclaimer": "Đây là công cụ sàng lọc, không phải chẩn đoán y tế. Kết quả chỉ mang tính tham khảo.",
        "questions": [
            {
                "id": "phq9_q1",
                "text": "Ít hứng thú hoặc không vui thích khi làm việc gì đó?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)", 
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "interest"
            },
            {
                "id": "phq9_q2", 
                "text": "Cảm thấy buồn, chán nản hoặc tuyệt vọng?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)", 
                    "Gần như mỗi ngày (3)"
                ],
                "category": "mood"
            },
            {
                "id": "phq9_q3",
                "text": "Khó ngủ, ngủ không say, hoặc ngủ quá nhiều?",
                "type": "likert_scale", 
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "sleep"
            },
            {
                "id": "phq9_q4",
                "text": "Cảm thấy mệt mỏi hoặc ít năng lượng?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "energy"
            },
            {
                "id": "phq9_q5",
                "text": "Ăn kém hoặc ăn quá nhiều?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "appetite"
            },
            {
                "id": "phq9_q6",
                "text": "Cảm thấy tệ về bản thân - hoặc cảm thấy mình là kẻ thất bại hoặc đã làm cho gia đình thất vọng?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "self_worth"
            },
            {
                "id": "phq9_q7",
                "text": "Khó tập trung vào việc gì đó, chẳng hạn như đọc báo hoặc xem tivi?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "concentration"
            },
            {
                "id": "phq9_q8",
                "text": "Di chuyển hoặc nói chuyện chậm chạp đến mức người khác có thể nhận ra? Hoặc ngược lại - bồn chồn hoặc bất an hơn bình thường?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "psychomotor"
            },
            {
                "id": "phq9_q9",
                "text": "Có ý nghĩ rằng tốt hơn là chết đi hoặc tự làm hại bản thân theo cách nào đó?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "suicide_risk",
                "warning": "high_risk"
            }
        ]
    },
    
    "gad7": {
        "title": "GAD-7 - Bộ câu hỏi sàng lọc Lo âu",
        "description": "Bộ câu hỏi Generalized Anxiety Disorder-7 được sử dụng để sàng lọc và đánh giá mức độ nghiêm trọng của rối loạn lo âu.",
        "category": "anxiety",
        "estimated_time": "2-4 phút",
        "question_count": 7,
        "scoring_info": {
            "max_score": 21,
            "ranges": {
                "minimal": "0-4",
                "mild": "5-9",
                "moderate": "10-14", 
                "severe": "15-21"
            }
        },
        "instructions": [
            "Trong 2 tuần qua, bạn có thường xuyên gặp phải các vấn đề sau không?",
            "Thang điểm: 0 = Không bao giờ, 1 = Vài ngày, 2 = Hơn một nửa số ngày, 3 = Gần như mỗi ngày"
        ],
        "disclaimer": "Đây là công cụ sàng lọc, không phải chẩn đoán y tế.",
        "questions": [
            {
                "id": "gad7_q1",
                "text": "Cảm thấy lo lắng, bồn chồn hoặc căng thẳng?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "nervousness"
            },
            {
                "id": "gad7_q2",
                "text": "Không thể ngừng hoặc kiểm soát việc lo lắng?",
                "type": "likert_scale", 
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "worry_control"
            },
            {
                "id": "gad7_q3",
                "text": "Lo lắng quá nhiều về những điều khác nhau?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "excessive_worry"
            },
            {
                "id": "gad7_q4",
                "text": "Khó thư giãn?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "relaxation"
            },
            {
                "id": "gad7_q5",
                "text": "Bồn chồn đến mức khó ngồi yên?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "restlessness"
            },
            {
                "id": "gad7_q6",
                "text": "Dễ bực bội hoặc cáu kỉnh?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "irritability"
            },
            {
                "id": "gad7_q7",
                "text": "Cảm thấy sợ hãi như thể điều gì đó tệ hại sắp xảy ra?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Vài ngày (1)",
                    "Hơn một nửa số ngày (2)",
                    "Gần như mỗi ngày (3)"
                ],
                "category": "fear"
            }
        ]
    },
    
    "dass21_stress": {
        "title": "DASS-21 - Bộ câu hỏi sàng lọc Căng thẳng",
        "description": "Phần đánh giá căng thẳng của bộ câu hỏi Depression, Anxiety and Stress Scale-21.",
        "category": "stress",
        "estimated_time": "3-5 phút",
        "question_count": 7,
        "scoring_info": {
            "max_score": 21,
            "ranges": {
                "normal": "0-14",
                "mild": "15-18",
                "moderate": "19-25",
                "severe": "26-33",
                "extremely_severe": "34-42"
            }
        },
        "instructions": [
            "Vui lòng đọc từng câu và chọn số 0, 1, 2 hoặc 3 để cho biết mức độ mà câu đó áp dụng cho bạn trong tuần qua.",
            "Thang điểm: 0 = Không áp dụng cho tôi, 1 = Áp dụng cho tôi một phần/thỉnh thoảng, 2 = Áp dụng cho tôi ở mức độ đáng kể/thường xuyên, 3 = Áp dụng cho tôi rất nhiều/hầu hết thời gian"
        ],
        "disclaimer": "Đây là công cụ sàng lọc, không phải chẩn đoán y tế.",
        "questions": [
            {
                "id": "dass21_stress_q1",
                "text": "Tôi thấy khó thư giãn",
                "type": "likert_scale",
                "options": [
                    "Không áp dụng cho tôi (0)",
                    "Áp dụng một phần/thỉnh thoảng (1)",
                    "Áp dụng đáng kể/thường xuyên (2)",
                    "Áp dụng rất nhiều/hầu hết thời gian (3)"
                ],
                "category": "relaxation_difficulty"
            },
            {
                "id": "dass21_stress_q2",
                "text": "Tôi có xu hướng phản ứng thái quá với các tình huống",
                "type": "likert_scale",
                "options": [
                    "Không áp dụng cho tôi (0)",
                    "Áp dụng một phần/thỉnh thoảng (1)",
                    "Áp dụng đáng kể/thường xuyên (2)",
                    "Áp dụng rất nhiều/hầu hết thời gian (3)"
                ],
                "category": "overreaction"
            },
            {
                "id": "dass21_stress_q3",
                "text": "Tôi cảm thấy bực bội khi có điều gì đó bất ngờ xảy ra và làm gián đoạn những gì tôi đang làm",
                "type": "likert_scale",
                "options": [
                    "Không áp dụng cho tôi (0)",
                    "Áp dụng một phần/thỉnh thoảng (1)",
                    "Áp dụng đáng kể/thường xuyên (2)",
                    "Áp dụng rất nhiều/hầu hết thời gian (3)"
                ],
                "category": "disruption_upset"
            },
            {
                "id": "dass21_stress_q4",
                "text": "Tôi thấy khó thư giãn",
                "type": "likert_scale",
                "options": [
                    "Không áp dụng cho tôi (0)",
                    "Áp dụng một phần/thỉnh thoảng (1)",
                    "Áp dụng đáng kể/thường xuyên (2)",
                    "Áp dụng rất nhiều/hầu hết thời gian (3)"
                ],
                "category": "relaxation"
            },
            {
                "id": "dass21_stress_q5",
                "text": "Tôi thấy mình bị kích động",
                "type": "likert_scale",
                "options": [
                    "Không áp dụng cho tôi (0)",
                    "Áp dụng một phần/thỉnh thoảng (1)",
                    "Áp dụng đáng kể/thường xuyên (2)",
                    "Áp dụng rất nhiều/hầu hết thời gian (3)"
                ],
                "category": "agitation"
            },
            {
                "id": "dass21_stress_q6",
                "text": "Tôi thấy khó chịu khi bị gián đoạn",
                "type": "likert_scale",
                "options": [
                    "Không áp dụng cho tôi (0)",
                    "Áp dụng một phần/thỉnh thoảng (1)",
                    "Áp dụng đáng kể/thường xuyên (2)",
                    "Áp dụng rất nhiều/hầu hết thời gian (3)"
                ],
                "category": "interruption_intolerance"
            },
            {
                "id": "dass21_stress_q7",
                "text": "Tôi cảm thấy căng thẳng",
                "type": "likert_scale",
                "options": [
                    "Không áp dụng cho tôi (0)",
                    "Áp dụng một phần/thỉnh thoảng (1)",
                    "Áp dụng đáng kể/thường xuyên (2)",
                    "Áp dụng rất nhiều/hầu hết thời gian (3)"
                ],
                "category": "stress_feeling"
            }
        ]
    },
    
    "suicide_risk": {
        "title": "Đánh giá Nguy cơ Tự tử",
        "description": "Đánh giá sơ bộ các dấu hiệu nguy cơ tự tử và ý định tự làm hại bản thân.",
        "category": "suicide_risk",
        "estimated_time": "2-3 phút",
        "question_count": 5,
        "scoring_info": {
            "max_score": 15,
            "ranges": {
                "minimal": "0-3",
                "low": "4-7",
                "moderate": "8-11",
                "high": "12-15"
            }
        },
        "instructions": [
            "Những câu hỏi này rất quan trọng để đánh giá tình trạng an toàn của bạn.",
            "Vui lòng trả lời thật lòng. Tất cả thông tin sẽ được bảo mật.",
            "Nếu bạn đang có ý định tự làm hại bản thân, hãy tìm kiếm sự giúp đỡ ngay lập tức."
        ],
        "disclaimer": "Nếu bạn có ý định tự làm hại bản thân, vui lòng gọi đường dây nóng 1800-0011 hoặc đến cơ sở y tế gần nhất.",
        "emergency_info": {
            "hotline": "1800-0011",
            "emergency": "113",
            "text": "Nếu bạn đang gặp khủng hoảng, hãy gọi ngay:"
        },
        "questions": [
            {
                "id": "suicide_q1",
                "text": "Trong tháng qua, bạn có bao giờ nghĩ rằng tốt hơn là chết đi không?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Ít khi (1)",
                    "Thỉnh thoảng (2)",
                    "Thường xuyên (3)"
                ],
                "category": "death_wish",
                "warning": "high_risk"
            },
            {
                "id": "suicide_q2",
                "text": "Trong tháng qua, bạn có bao giờ nghĩ đến việc tự làm hại bản thân không?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Ít khi (1)",
                    "Thỉnh thoảng (2)",
                    "Thường xuyên (3)"
                ],
                "category": "self_harm",
                "warning": "high_risk"
            },
            {
                "id": "suicide_q3",
                "text": "Bạn có bao giờ lập kế hoạch cụ thể về cách tự làm hại bản thân không?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Nghĩ đến nhưng chưa có kế hoạch (1)",
                    "Có kế hoạch sơ bộ (2)",
                    "Có kế hoạch chi tiết (3)"
                ],
                "category": "suicide_plan",
                "warning": "high_risk"
            },
            {
                "id": "suicide_q4",
                "text": "Bạn cảm thấy cuộc sống của mình có ý nghĩa như thế nào?",
                "type": "likert_scale",
                "options": [
                    "Rất có ý nghĩa (0)",
                    "Có ý nghĩa (1)",
                    "Ít ý nghĩa (2)",
                    "Không có ý nghĩa (3)"
                ],
                "category": "life_meaning"
            },
            {
                "id": "suicide_q5",
                "text": "Bạn có cảm thấy mình là gánh nặng cho người khác không?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Ít khi (1)",
                    "Thỉnh thoảng (2)",
                    "Thường xuyên (3)"
                ],
                "category": "burden_feeling"
            }
        ]
    },
    
    "initial": {
        "title": "Sàng lọc Sức khỏe Tâm thần Ban đầu",
        "description": "Đánh giá sơ bộ để xác định các vấn đề sức khỏe tâm thần có thể có và định hướng đánh giá chi tiết.",
        "category": "general",
        "estimated_time": "3-5 phút",
        "question_count": 8,
        "scoring_info": {
            "max_score": 24,
            "ranges": {
                "minimal": "0-6",
                "mild": "7-12",
                "moderate": "13-18",
                "severe": "19-24"
            }
        },
        "instructions": [
            "Những câu hỏi này giúp tôi hiểu tình trạng sức khỏe tâm thần tổng quát của bạn.",
            "Hãy trả lời dựa trên cảm giác của bạn trong 2 tuần gần đây."
        ],
        "disclaimer": "Đây là đánh giá sơ bộ để định hướng, không phải chẩn đoán y tế.",
        "questions": [
            {
                "id": "initial_q1",
                "text": "Gần đây bạn có cảm thấy buồn, chán nản hoặc tuyệt vọng không?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Ít khi (1)",
                    "Thỉnh thoảng (2)",
                    "Thường xuyên (3)"
                ],
                "category": "depression_indicator"
            },
            {
                "id": "initial_q2",
                "text": "Bạn có thường xuyên cảm thấy lo lắng hoặc căng thẳng không?",
                "type": "likert_scale",
                "options": [
                    "Không bao giờ (0)",
                    "Ít khi (1)",
                    "Thỉnh thoảng (2)",
                    "Thường xuyên (3)"
                ],
                "category": "anxiety_indicator"
            },
            {
                "id": "initial_q3",
                "text": "Bạn có gặp khó khăn trong việc ngủ không?",
                "type": "likert_scale",
                "options": [
                    "Không có vấn đề (0)",
                    "Thỉnh thoảng khó ngủ (1)",
                    "Thường xuyên khó ngủ (2)",
                    "Rất khó ngủ (3)"
                ],
                "category": "sleep_issues"
            },
            {
                "id": "initial_q4",
                "text": "Mức năng lượng của bạn trong ngày như thế nào?",
                "type": "likert_scale",
                "options": [
                    "Đầy năng lượng (0)",
                    "Năng lượng bình thường (1)",
                    "Thường xuyên mệt mỏi (2)",
                    "Kiệt sức, không có năng lượng (3)"
                ],
                "category": "energy_level"
            },
            {
                "id": "initial_q5",
                "text": "Bạn có mất hứng thú với những hoạt động mà trước đây bạn thích không?",
                "type": "likert_scale",
                "options": [
                    "Vẫn hứng thú như trước (0)",
                    "Hơi giảm hứng thú (1)",
                    "Mất hứng thú đáng kể (2)",
                    "Hoàn toàn mất hứng thú (3)"
                ],
                "category": "interest_loss"
            },
            {
                "id": "initial_q6",
                "text": "Bạn có khó tập trung vào công việc hoặc học tập không?",
                "type": "likert_scale",
                "options": [
                    "Tập trung tốt (0)",
                    "Thỉnh thoảng khó tập trung (1)",
                    "Thường xuyên khó tập trung (2)",
                    "Rất khó tập trung (3)"
                ],
                "category": "concentration"
            },
            {
                "id": "initial_q7",
                "text": "Các mối quan hệ xã hội của bạn như thế nào gần đây?",
                "type": "likert_scale",
                "options": [
                    "Bình thường, tích cực (0)",
                    "Hơi giảm tương tác (1)",
                    "Tránh tiếp xúc với người khác (2)",
                    "Cô lập hoàn toàn (3)"
                ],
                "category": "social_functioning"
            },
            {
                "id": "initial_q8",
                "text": "Bạn có cảm thấy áp lực hoặc căng thẳng từ công việc/học tập/gia đình không?",
                "type": "likert_scale",
                "options": [
                    "Không có áp lực đặc biệt (0)",
                    "Áp lực nhẹ, có thể quản lý (1)",
                    "Áp lực đáng kể (2)",
                    "Áp lực quá lớn, khó chịu đựng (3)"
                ],
                "category": "stress_level"
            }
        ]
    }
}

# Helper function to get questionnaire by ID
def get_questionnaire(questionnaire_id):
    """
    Get questionnaire configuration by ID
    
    Args:
        questionnaire_id: ID of the questionnaire
        
    Returns:
        Questionnaire configuration dict or None
    """
    return questionnaires.get(questionnaire_id)

# Helper function to get all available questionnaires
def get_all_questionnaires():
    """
    Get all available questionnaires
    
    Returns:
        Dict of all questionnaires
    """
    return questionnaires

# Helper function to get questionnaires by category
def get_questionnaires_by_category(category):
    """
    Get questionnaires filtered by category
    
    Args:
        category: Category to filter by
        
    Returns:
        Dict of questionnaires in the specified category
    """
    return {
        qid: config for qid, config in questionnaires.items()
        if config.get('category') == category
    }