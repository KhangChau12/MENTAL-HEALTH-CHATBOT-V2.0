/**
 * Assessment.js - Logic assessment interface
 * Handles structured questionnaire flow for Mental Health Assessment
 */

class AssessmentInterface {
    constructor() {
        // DOM Elements
        this.questionCard = document.getElementById('question-card');
        this.loadingState = document.getElementById('loading-state');
        this.completionScreen = document.getElementById('completion-screen');
        this.questionNumber = document.getElementById('question-number');
        this.questionCategory = document.getElementById('question-category');
        this.questionText = document.getElementById('question-text');
        this.questionDescription = document.getElementById('question-description');
        this.answerOptions = document.getElementById('answer-options');
        this.prevButton = document.getElementById('prev-button');
        this.nextButton = document.getElementById('next-button');
        this.progressBar = document.getElementById('progress-bar');
        this.progressText = document.getElementById('progress-text');
        this.assessmentTitle = document.getElementById('assessment-title');
        this.assessmentSubtitle = document.getElementById('assessment-subtitle');
        
        // State variables
        this.currentQuestionIndex = 0;
        this.currentAssessmentType = this.getAssessmentTypeFromURL() || 'initial_screening';
        this.answers = {};
        this.assessmentData = {};
        this.isLoading = false;
        this.sessionId = this.generateSessionId();
        
        this.init();
    }
    
    init() {
        this.loadAssessmentData();
        this.setupEventListeners();
        this.loadStoredAnswers();
        this.startAssessment();
    }
    
    generateSessionId() {
        return 'assessment_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    getAssessmentTypeFromURL() {
        const params = new URLSearchParams(window.location.search);
        return params.get('type') || 'phq9';
    }
    
    loadStoredAnswers() {
        try {
            const stored = localStorage.getItem(`assessment_${this.currentAssessmentType}_answers`);
            if (stored) {
                this.answers = JSON.parse(stored);
            }
        } catch (e) {
            console.warn('Could not load stored answers:', e);
            this.answers = {};
        }
    }
    
    saveAnswers() {
        try {
            localStorage.setItem(
                `assessment_${this.currentAssessmentType}_answers`, 
                JSON.stringify(this.answers)
            );
        } catch (e) {
            console.warn('Could not save answers:', e);
        }
    }
    
    setupEventListeners() {
        if (this.prevButton) {
            this.prevButton.addEventListener('click', () => this.handlePreviousQuestion());
        }
        
        if (this.nextButton) {
            this.nextButton.addEventListener('click', () => this.handleNextQuestion());
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft' && !this.prevButton?.disabled) {
                this.handlePreviousQuestion();
            } else if (e.key === 'ArrowRight' && !this.nextButton?.disabled) {
                this.handleNextQuestion();
            } else if (e.key >= '1' && e.key <= '9') {
                const optionIndex = parseInt(e.key) - 1;
                const options = document.querySelectorAll('.answer-option');
                if (options[optionIndex]) {
                    this.selectOption(optionIndex);
                }
            }
        });
    }
    
    loadAssessmentData() {
        // Complete assessment configurations
        this.assessmentData = {
            initial_screening: {
                title: "Sàng lọc ban đầu",
                description: "Xác định các vấn đề chính về sức khỏe tâm thần",
                questions: [
                    {
                        id: "mood_weeks",
                        text: "Trong 2 tuần qua, bạn có cảm thấy buồn bã, chán nản hoặc tuyệt vọng không?",
                        category: "mood",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "interest_loss",
                        text: "Bạn có ít hứng thú hoặc không vui thích khi làm việc gì đó không?",
                        category: "interest",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "anxiety_worry",
                        text: "Bạn có cảm thấy bồn chồn, lo lắng hoặc căng thẳng không?",
                        category: "anxiety",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "sleep_problems",
                        text: "Bạn có gặp vấn đề về giấc ngủ (khó ngủ, ngủ không say, hoặc ngủ quá nhiều) không?",
                        category: "sleep",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "energy_fatigue",
                        text: "Bạn có cảm thấy mệt mỏi hoặc thiếu năng lượng không?",
                        category: "energy",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    }
                ]
            },
            
            phq9: {
                title: "PHQ-9 - Đánh giá Trầm cảm",
                description: "Bộ câu hỏi tiêu chuẩn đánh giá mức độ trầm cảm",
                instructions: "Trong 2 tuần qua, bạn có thường xuyên gặp phải các vấn đề sau không?",
                questions: [
                    {
                        id: "phq9_1",
                        text: "Ít hứng thú hoặc không vui thích khi làm việc gì đó",
                        category: "interest",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "phq9_2",
                        text: "Cảm thấy buồn, chán nản hoặc tuyệt vọng",
                        category: "mood",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "phq9_3",
                        text: "Khó ngủ, ngủ không say, hoặc ngủ quá nhiều",
                        category: "sleep",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "phq9_4",
                        text: "Cảm thấy mệt mỏi hoặc thiếu năng lượng",
                        category: "energy",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "phq9_5",
                        text: "Ăn kém hoặc ăn quá nhiều",
                        category: "appetite",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "phq9_6",
                        text: "Cảm thấy tệ về bản thân - hoặc cảm thấy mình là kẻ thất bại hoặc đã làm gia đình thất vọng",
                        category: "self_worth",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "phq9_7",
                        text: "Khó tập trung vào việc gì đó, chẳng hạn như đọc báo hoặc xem tivi",
                        category: "concentration",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "phq9_8",
                        text: "Di chuyển hoặc nói chuyện chậm chạp đến mức người khác có thể nhận ra? Hoặc ngược lại - bồn chồn hoặc bất an hơn bình thường",
                        category: "psychomotor",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "phq9_9",
                        text: "Có ý nghĩ rằng tốt hơn là chết đi hoặc tự làm hại bản thân theo cách nào đó",
                        category: "suicide_risk",
                        warning: "high_risk",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    }
                ]
            },
            
            gad7: {
                title: "GAD-7 - Đánh giá Lo âu",
                description: "Bộ câu hỏi tiêu chuẩn đánh giá mức độ lo âu",
                instructions: "Trong 2 tuần qua, bạn có thường xuyên gặp phải các vấn đề sau không?",
                questions: [
                    {
                        id: "gad7_1",
                        text: "Cảm thấy bồn chồn, lo lắng hoặc căng thẳng",
                        category: "anxiety",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "gad7_2",
                        text: "Không thể ngừng lo lắng hoặc kiểm soát việc lo lắng",
                        category: "worry_control",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "gad7_3",
                        text: "Lo lắng quá nhiều về những điều khác nhau",
                        category: "excessive_worry",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "gad7_4",
                        text: "Khó thư giãn",
                        category: "relaxation",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "gad7_5",
                        text: "Bồn chồn đến mức khó ngồi yên",
                        category: "restlessness",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "gad7_6",
                        text: "Dễ dàng trở nên khó chịu hoặc cáu kỉnh",
                        category: "irritability",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "gad7_7",
                        text: "Cảm thấy sợ hãi như thể điều gì đó tồi tệ sắp xảy ra",
                        category: "fear",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    }
                ]
            },
            
            dass21_stress: {
                title: "DASS-21 - Đánh giá Căng thẳng",
                description: "Bộ câu hỏi đánh giá mức độ căng thẳng",
                instructions: "Trong tuần qua, bạn có trải qua các tình huống sau không?",
                questions: [
                    {
                        id: "dass21_stress_1",
                        text: "Cảm thấy khó thư giãn",
                        category: "tension",
                        options: [
                            { value: 0, text: "Không áp dụng cho tôi" },
                            { value: 1, text: "Áp dụng ít khi" },
                            { value: 2, text: "Áp dụng một phần/thỉnh thoảng" },
                            { value: 3, text: "Áp dụng nhiều/phần lớn thời gian" }
                        ]
                    },
                    {
                        id: "dass21_stress_2",
                        text: "Có xu hướng phản ứng thái quá với các tình huống",
                        category: "overreaction",
                        options: [
                            { value: 0, text: "Không áp dụng cho tôi" },
                            { value: 1, text: "Áp dụng ít khi" },
                            { value: 2, text: "Áp dụng một phần/thỉnh thoảng" },
                            { value: 3, text: "Áp dụng nhiều/phần lớn thời gian" }
                        ]
                    },
                    {
                        id: "dass21_stress_3",
                        text: "Cảm thấy căng thẳng",
                        category: "tension",
                        options: [
                            { value: 0, text: "Không áp dụng cho tôi" },
                            { value: 1, text: "Áp dụng ít khi" },
                            { value: 2, text: "Áp dụng một phần/thỉnh thoảng" },
                            { value: 3, text: "Áp dụng nhiều/phần lớn thời gian" }
                        ]
                    },
                    {
                        id: "dass21_stress_4",
                        text: "Cảm thấy bồn chồn",
                        category: "agitation",
                        options: [
                            { value: 0, text: "Không áp dụng cho tôi" },
                            { value: 1, text: "Áp dụng ít khi" },
                            { value: 2, text: "Áp dụng một phần/thỉnh thoảng" },
                            { value: 3, text: "Áp dụng nhiều/phần lớn thời gian" }
                        ]
                    },
                    {
                        id: "dass21_stress_5",
                        text: "Thấy khó chịu khi bị làm gián đoạn",
                        category: "irritability",
                        options: [
                            { value: 0, text: "Không áp dụng cho tôi" },
                            { value: 1, text: "Áp dụng ít khi" },
                            { value: 2, text: "Áp dụng một phần/thỉnh thoảng" },
                            { value: 3, text: "Áp dụng nhiều/phần lớn thời gian" }
                        ]
                    },
                    {
                        id: "dass21_stress_6",
                        text: "Dễ dàng bị kích động",
                        category: "irritability",
                        options: [
                            { value: 0, text: "Không áp dụng cho tôi" },
                            { value: 1, text: "Áp dụng ít khi" },
                            { value: 2, text: "Áp dụng một phần/thỉnh thoảng" },
                            { value: 3, text: "Áp dụng nhiều/phần lớn thời gian" }
                        ]
                    },
                    {
                        id: "dass21_stress_7",
                        text: "Cảm thấy khó chịu khi không thể hoàn thành công việc ngay lập tức",
                        category: "impatience",
                        options: [
                            { value: 0, text: "Không áp dụng cho tôi" },
                            { value: 1, text: "Áp dụng ít khi" },
                            { value: 2, text: "Áp dụng một phần/thỉnh thoảng" },
                            { value: 3, text: "Áp dụng nhiều/phần lớn thời gian" }
                        ]
                    }
                ]
            }
        };
    }
    
    startAssessment() {
        const assessment = this.assessmentData[this.currentAssessmentType];
        
        if (!assessment) {
            this.showError('Không tìm thấy bộ câu hỏi đánh giá.');
            return;
        }
        
        // Update UI with assessment info
        if (this.assessmentTitle) {
            this.assessmentTitle.textContent = assessment.title;
        }
        
        if (this.assessmentSubtitle) {
            this.assessmentSubtitle.textContent = assessment.description;
        }
        
        // Start with first question
        this.displayCurrentQuestion();
    }
    
    displayCurrentQuestion() {
        const assessment = this.assessmentData[this.currentAssessmentType];
        const questions = assessment.questions;
        
        if (!questions || this.currentQuestionIndex >= questions.length) {
            this.completeAssessment();
            return;
        }
        
        const question = questions[this.currentQuestionIndex];
        
        // Update question display
        this.updateQuestionDisplay(question);
        this.updateProgress();
        this.displayAnswerOptions(question);
        this.updateNavigationButtons();
        
        // Show question card
        this.showQuestionCard();
    }
    
    updateQuestionDisplay(question) {
        if (this.questionNumber) {
            this.questionNumber.textContent = `${this.currentQuestionIndex + 1}`;
        }
        
        if (this.questionCategory) {
            this.questionCategory.textContent = this.getCategoryDisplayName(question.category);
        }
        
        if (this.questionText) {
            this.questionText.textContent = question.text;
        }
        
        if (this.questionDescription && question.description) {
            this.questionDescription.textContent = question.description;
            this.questionDescription.style.display = 'block';
        } else if (this.questionDescription) {
            this.questionDescription.style.display = 'none';
        }
    }
    
    getCategoryDisplayName(category) {
        const categoryNames = {
            'mood': 'Tâm trạng',
            'interest': 'Sở thích',
            'anxiety': 'Lo âu',
            'sleep': 'Giấc ngủ',
            'energy': 'Năng lượng',
            'appetite': 'Ăn uống',
            'self_worth': 'Tự đánh giá',
            'concentration': 'Tập trung',
            'psychomotor': 'Vận động',
            'suicide_risk': 'Nguy cơ',
            'worry_control': 'Kiểm soát lo lắng',
            'excessive_worry': 'Lo lắng quá mức',
            'relaxation': 'Thư giãn',
            'restlessness': 'Bồn chồn',
            'irritability': 'Cáu kỉnh',
            'fear': 'Sợ hãi',
            'tension': 'Căng thẳng',
            'overreaction': 'Phản ứng thái quá',
            'agitation': 'Kích động',
            'impatience': 'Thiếu kiên nhẫn'
        };
        
        return categoryNames[category] || category;
    }
    
    updateProgress() {
        const assessment = this.assessmentData[this.currentAssessmentType];
        const totalQuestions = assessment.questions.length;
        const currentProgress = ((this.currentQuestionIndex + 1) / totalQuestions) * 100;
        
        if (this.progressBar) {
            this.progressBar.style.width = `${currentProgress}%`;
        }
        
        if (this.progressText) {
            this.progressText.textContent = `${this.currentQuestionIndex + 1}/${totalQuestions}`;
        }
    }
    
    displayAnswerOptions(question) {
        if (!this.answerOptions) return;
        
        this.answerOptions.innerHTML = '';
        
        question.options.forEach((option, index) => {
            const optionElement = this.createAnswerOption(option, index, question);
            this.answerOptions.appendChild(optionElement);
        });
    }
    
    createAnswerOption(option, index, question) {
        const optionElement = document.createElement('div');
        optionElement.className = 'answer-option';
        optionElement.dataset.value = option.value;
        optionElement.dataset.questionId = question.id;
        
        // Check if this option is already selected
        const currentAnswer = this.answers[question.id];
        if (currentAnswer !== undefined && currentAnswer == option.value) {
            optionElement.classList.add('selected');
        }
        
        optionElement.innerHTML = `
            <div class="option-content">
                <div class="option-number">${index + 1}</div>
                <div class="option-text">${option.text}</div>
                <div class="option-value">${option.value}</div>
            </div>
        `;
        
        optionElement.addEventListener('click', () => {
            this.selectOption(question.id, option.value, optionElement);
        });
        
        return optionElement;
    }
    
    selectOption(questionId, value, element) {
        // Remove previous selection
        const allOptions = this.answerOptions.querySelectorAll('.answer-option');
        allOptions.forEach(opt => opt.classList.remove('selected'));
        
        // Select current option
        element.classList.add('selected');
        
        // Save answer
        this.answers[questionId] = value;
        this.saveAnswers();
        
        // Update navigation
        this.updateNavigationButtons();
        
        // Check for high-risk answers
        this.checkHighRiskAnswer(questionId, value);
    }
    
    checkHighRiskAnswer(questionId, value) {
        const assessment = this.assessmentData[this.currentAssessmentType];
        const question = assessment.questions.find(q => q.id === questionId);
        
        if (question && question.warning === 'high_risk' && value > 0) {
            this.showHighRiskWarning();
        }
    }
    
    showHighRiskWarning() {
        // Create warning modal or notification
        const warningHtml = `
            <div class="risk-warning-overlay">
                <div class="risk-warning-modal">
                    <h3>⚠️ Cảnh báo quan trọng</h3>
                    <p>Chúng tôi quan tâm đến sự an toàn của bạn. Nếu bạn đang có ý nghĩ tự làm hại bản thân, vui lòng liên hệ ngay:</p>
                    <div class="emergency-contacts">
                        <p><strong>Đường dây nóng:</strong> 1800-0011</p>
                        <p><strong>Cấp cứu:</strong> 113</p>
                    </div>
                    <button onclick="this.closest('.risk-warning-overlay').remove()" class="close-warning-btn">Tôi hiểu</button>
                </div>
            </div>
        `;
        
        // Add to page
        const warningElement = document.createElement('div');
        warningElement.innerHTML = warningHtml;
        document.body.appendChild(warningElement);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            const overlay = document.querySelector('.risk-warning-overlay');
            if (overlay) {
                overlay.remove();
            }
        }, 10000);
    }
    
    updateNavigationButtons() {
        const assessment = this.assessmentData[this.currentAssessmentType];
        const currentQuestion = assessment.questions[this.currentQuestionIndex];
        const hasAnswer = this.answers[currentQuestion.id] !== undefined;
        
        // Previous button
        if (this.prevButton) {
            this.prevButton.disabled = this.currentQuestionIndex === 0;
        }
        
        // Next button
        if (this.nextButton) {
            this.nextButton.disabled = !hasAnswer;
            
            if (this.currentQuestionIndex === assessment.questions.length - 1) {
                this.nextButton.textContent = 'Hoàn thành đánh giá';
                this.nextButton.classList.add('completion-button');
            } else {
                this.nextButton.textContent = 'Câu hỏi tiếp theo';
                this.nextButton.classList.remove('completion-button');
            }
        }
    }
    
    handlePreviousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.displayCurrentQuestion();
        }
    }
    
    handleNextQuestion() {
        const assessment = this.assessmentData[this.currentAssessmentType];
        const currentQuestion = assessment.questions[this.currentQuestionIndex];
        
        if (this.answers[currentQuestion.id] === undefined) {
            this.showError('Vui lòng chọn một câu trả lời trước khi tiếp tục.');
            return;
        }
        
        if (this.currentQuestionIndex < assessment.questions.length - 1) {
            this.currentQuestionIndex++;
            this.displayCurrentQuestion();
        } else {
            this.completeAssessment();
        }
    }
    
    async completeAssessment() {
        try {
            this.showLoading();
            
            // Calculate scores
            const results = this.calculateResults();
            
            // Save results to localStorage
            this.saveResults(results);
            
            // Show completion
            setTimeout(() => {
                this.showCompletion(results);
            }, 1000);
            
        } catch (error) {
            console.error('Assessment completion error:', error);
            this.showError('Có lỗi xảy ra khi tính toán kết quả. Vui lòng thử lại.');
        }
    }
    
    calculateResults() {
        const assessment = this.assessmentData[this.currentAssessmentType];
        const answers = this.answers;
        
        // Calculate total score
        let totalScore = 0;
        let maxScore = 0;
        const categoryScores = {};
        
        assessment.questions.forEach(question => {
            const answer = answers[question.id];
            if (answer !== undefined) {
                totalScore += answer;
                
                // Track category scores
                if (!categoryScores[question.category]) {
                    categoryScores[question.category] = { score: 0, count: 0 };
                }
                categoryScores[question.category].score += answer;
                categoryScores[question.category].count++;
            }
            
            // Calculate max possible score
            const maxOptionValue = Math.max(...question.options.map(opt => opt.value));
            maxScore += maxOptionValue;
        });
        
        // Determine severity level
        const severity = this.determineSeverity(totalScore, maxScore);
        
        // Generate recommendations
        const recommendations = this.generateRecommendations(totalScore, severity, categoryScores);
        
        const results = {
            assessment_type: this.currentAssessmentType,
            assessment_title: assessment.title,
            total_score: totalScore,
            max_score: maxScore,
            percentage: Math.round((totalScore / maxScore) * 100),
            severity: severity,
            category_scores: categoryScores,
            answers: answers,
            recommendations: recommendations,
            completed_at: new Date().toISOString(),
            session_id: this.sessionId
        };
        
        return results;
    }
    
    determineSeverity(score, maxScore) {
        const percentage = (score / maxScore) * 100;
        
        // Different scales for different assessments
        if (this.currentAssessmentType === 'phq9') {
            if (score <= 4) return { level: 'minimal', label: 'Tối thiểu', color: '#22c55e' };
            if (score <= 9) return { level: 'mild', label: 'Nhẹ', color: '#eab308' };
            if (score <= 14) return { level: 'moderate', label: 'Trung bình', color: '#f97316' };
            if (score <= 19) return { level: 'moderately_severe', label: 'Trung bình nặng', color: '#ef4444' };
            return { level: 'severe', label: 'Nặng', color: '#dc2626' };
        } else if (this.currentAssessmentType === 'gad7') {
            if (score <= 4) return { level: 'minimal', label: 'Tối thiểu', color: '#22c55e' };
            if (score <= 9) return { level: 'mild', label: 'Nhẹ', color: '#eab308' };
            if (score <= 14) return { level: 'moderate', label: 'Trung bình', color: '#f97316' };
            return { level: 'severe', label: 'Nặng', color: '#ef4444' };
        } else {
            // Generic severity levels
            if (percentage <= 25) return { level: 'minimal', label: 'Tối thiểu', color: '#22c55e' };
            if (percentage <= 50) return { level: 'mild', label: 'Nhẹ', color: '#eab308' };
            if (percentage <= 75) return { level: 'moderate', label: 'Trung bình', color: '#f97316' };
            return { level: 'severe', label: 'Nặng', color: '#ef4444' };
        }
    }
    
    generateRecommendations(score, severity, categoryScores) {
        const recommendations = [];
        
        // General recommendations based on severity
        if (severity.level === 'minimal') {
            recommendations.push({
                type: 'general',
                title: 'Tình trạng tốt',
                content: 'Kết quả cho thấy bạn đang có tình trạng sức khỏe tâm thần tốt. Hãy duy trì lối sống lành mạnh.'
            });
        } else if (severity.level === 'mild') {
            recommendations.push({
                type: 'lifestyle',
                title: 'Chăm sóc bản thân',
                content: 'Hãy duy trì thói quen tập thể dục, ngủ đủ giấc và ăn uống lành mạnh. Cân nhắc thực hành mindfulness.'
            });
        } else if (severity.level === 'moderate') {
            recommendations.push({
                type: 'professional',
                title: 'Tìm kiếm hỗ trợ',
                content: 'Nên cân nhắc tham khảo ý kiến từ chuyên gia tâm lý hoặc bác sĩ để được hỗ trợ phù hợp.'
            });
        } else {
            recommendations.push({
                type: 'urgent',
                title: 'Cần hỗ trợ chuyên nghiệp',
                content: 'Kết quả cho thấy bạn cần được hỗ trợ chuyên nghiệp. Hãy liên hệ với bác sĩ hoặc chuyên gia tâm lý ngay.'
            });
        }
        
        // Category-specific recommendations
        Object.entries(categoryScores).forEach(([category, data]) => {
            const avgScore = data.score / data.count;
            if (avgScore >= 2) {
                const categoryRec = this.getCategoryRecommendation(category);
                if (categoryRec) {
                    recommendations.push(categoryRec);
                }
            }
        });
        
        return recommendations;
    }
    
    getCategoryRecommendation(category) {
        const categoryRecommendations = {
            'sleep': {
                type: 'lifestyle',
                title: 'Cải thiện giấc ngủ',
                content: 'Thiết lập thói quen ngủ đều đặn, tránh caffeine trước khi ngủ, tạo môi trường ngủ thoải mái.'
            },
            'energy': {
                type: 'lifestyle',
                title: 'Tăng cường năng lượng',
                content: 'Tập thể dục nhẹ nhàng, ăn uống cân bằng, đảm bảo nghỉ ngơi đầy đủ.'
            },
            'anxiety': {
                type: 'technique',
                title: 'Quản lý lo âu',
                content: 'Thực hành kỹ thuật thở sâu, meditation, hoặc yoga để giảm căng thẳng.'
            },
            'concentration': {
                type: 'technique',
                title: 'Cải thiện tập trung',
                content: 'Chia nhỏ công việc, loại bỏ yếu tố gây xao nhãng, thực hành mindfulness.'
            }
        };
        
        return categoryRecommendations[category] || null;
    }
    
    saveResults(results) {
        try {
            // Save to localStorage
            localStorage.setItem('assessmentResults', JSON.stringify(results));
            localStorage.setItem(`assessment_${this.currentAssessmentType}_results`, JSON.stringify(results));
            
            // Clear answers after completion
            localStorage.removeItem(`assessment_${this.currentAssessmentType}_answers`);
            
        } catch (error) {
            console.warn('Could not save results:', error);
        }
    }
    
    showLoading() {
        this.hideQuestionCard();
        
        if (this.loadingState) {
            this.loadingState.style.display = 'flex';
            this.loadingState.innerHTML = `
                <div class="loading-content">
                    <div class="loading-spinner"></div>
                    <h3>Đang tính toán kết quả...</h3>
                    <p>Vui lòng chờ trong giây lát</p>
                </div>
            `;
        }
    }
    
    showCompletion(results) {
        this.hideLoading();
        
        if (this.completionScreen) {
            this.completionScreen.style.display = 'flex';
            this.completionScreen.innerHTML = `
                <div class="completion-content">
                    <div class="completion-header">
                        <div class="completion-icon">✅</div>
                        <h2>Hoàn thành đánh giá!</h2>
                        <p>Cảm ơn bạn đã hoàn thành bộ câu hỏi ${results.assessment_title}</p>
                    </div>
                    
                    <div class="results-preview">
                        <div class="score-display">
                            <div class="score-circle" style="background: conic-gradient(${results.severity.color} ${results.percentage}%, #e5e7eb ${results.percentage}%)">
                                <span class="score-text">${results.total_score}/${results.max_score}</span>
                            </div>
                            <div class="severity-label" style="color: ${results.severity.color}">
                                ${results.severity.label}
                            </div>
                        </div>
                    </div>
                    
                    <div class="completion-actions">
                        <button onclick="window.location.href='/results'" class="primary-button">
                            Xem kết quả chi tiết
                        </button>
                        <button onclick="window.location.href='/'" class="secondary-button">
                            Về trang chủ
                        </button>
                    </div>
                </div>
            `;
        }
    }
    
    showQuestionCard() {
        if (this.questionCard) {
            this.questionCard.style.display = 'block';
        }
        this.hideLoading();
        this.hideCompletion();
    }
    
    hideQuestionCard() {
        if (this.questionCard) {
            this.questionCard.style.display = 'none';
        }
    }
    
    hideLoading() {
        if (this.loadingState) {
            this.loadingState.style.display = 'none';
        }
    }
    
    hideCompletion() {
        if (this.completionScreen) {
            this.completionScreen.style.display = 'none';
        }
    }
    
    showError(message) {
        // Create error notification
        const errorHtml = `
            <div class="error-notification">
                <div class="error-content">
                    <span class="error-icon">⚠️</span>
                    <span class="error-message">${message}</span>
                </div>
            </div>
        `;
        
        // Remove existing error notifications
        const existingErrors = document.querySelectorAll('.error-notification');
        existingErrors.forEach(error => error.remove());
        
        // Add new error
        const errorElement = document.createElement('div');
        errorElement.innerHTML = errorHtml;
        document.body.appendChild(errorElement);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const notification = document.querySelector('.error-notification');
            if (notification) {
                notification.remove();
            }
        }, 5000);
    }
    
    // Public methods
    resetAssessment() {
        this.currentQuestionIndex = 0;
        this.answers = {};
        
        // Clear localStorage
        localStorage.removeItem(`assessment_${this.currentAssessmentType}_answers`);
        
        // Reset UI
        this.displayCurrentQuestion();
    }
    
    getProgress() {
        const assessment = this.assessmentData[this.currentAssessmentType];
        return {
            current: this.currentQuestionIndex + 1,
            total: assessment.questions.length,
            percentage: ((this.currentQuestionIndex + 1) / assessment.questions.length) * 100,
            answers: Object.keys(this.answers).length
        };
    }
}

// Initialize assessment interface when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.assessmentInterface = new AssessmentInterface();
    
    // Add global functions
    window.resetAssessment = function() {
        if (window.assessmentInterface) {
            window.assessmentInterface.resetAssessment();
        }
    };
    
    window.getAssessmentProgress = function() {
        if (window.assessmentInterface) {
            return window.assessmentInterface.getProgress();
        }
        return null;
    };
    
    console.log('Assessment interface initialized successfully');
});