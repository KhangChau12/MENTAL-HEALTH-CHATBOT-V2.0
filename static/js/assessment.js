/**
 * Assessment.js - Logic assessment interface
 * Handles structured questionnaire flow for Mental Health Assessment
 */

document.addEventListener('DOMContentLoaded', function() {
    // UI Elements
    const questionCard = document.getElementById('question-card');
    const loadingState = document.getElementById('loading-state');
    const completionScreen = document.getElementById('completion-screen');
    const questionNumber = document.getElementById('question-number');
    const questionCategory = document.getElementById('question-category');
    const questionText = document.getElementById('question-text');
    const questionDescription = document.getElementById('question-description');
    const answerOptions = document.getElementById('answer-options');
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const assessmentTitle = document.getElementById('assessment-title');
    const assessmentSubtitle = document.getElementById('assessment-subtitle');
    
    // State variables
    let currentQuestionIndex = 0;
    let currentAssessmentType = 'initial_screening';
    let answers = {};
    let assessmentData = {};
    let isLoading = false;
    
    // Initialize assessment
    init();
    
    function init() {
        loadAssessmentData();
        setupEventListeners();
        startAssessment();
    }
    
    function setupEventListeners() {
        prevButton.addEventListener('click', handlePreviousQuestion);
        nextButton.addEventListener('click', handleNextQuestion);
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft' && !prevButton.disabled) {
                handlePreviousQuestion();
            } else if (e.key === 'ArrowRight' && !nextButton.disabled) {
                handleNextQuestion();
            } else if (e.key >= '1' && e.key <= '9') {
                const optionIndex = parseInt(e.key) - 1;
                const options = document.querySelectorAll('.answer-option');
                if (options[optionIndex]) {
                    selectOption(optionIndex);
                }
            }
        });
    }
    
    function loadAssessmentData() {
        // Load assessment configuration
        assessmentData = {
            initial_screening: {
                title: "Sàng lọc ban đầu",
                description: "Xác định các vấn đề chính về sức khỏe tâm thần",
                questions: [
                    {
                        id: "mood_weeks",
                        text: "Trong 2 tuần qua, bạn có cảm thấy buồn bã, chán nản hoặc tuyệt vọng không?",
                        options: [
                            { value: 0, text: "Không, không hề" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "interest_loss",
                        text: "Trong 2 tuần qua, bạn có cảm thấy ít hứng thú hoặc vui vẻ khi làm việc không?",
                        options: [
                            { value: 0, text: "Không, không hề" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "anxiety_frequency",
                        text: "Bạn có thường xuyên cảm thấy lo lắng, bồn chồn hoặc căng thẳng không?",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Thỉnh thoảng" },
                            { value: 2, text: "Thường xuyên" },
                            { value: 3, text: "Hầu như lúc nào cũng vậy" }
                        ]
                    },
                    {
                        id: "sleep_problems",
                        text: "Gần đây bạn có gặp khó khăn về giấc ngủ không?",
                        options: [
                            { value: 0, text: "Ngủ bình thường" },
                            { value: 1, text: "Thỉnh thoảng khó ngủ" },
                            { value: 2, text: "Thường xuyên khó ngủ" },
                            { value: 3, text: "Mất ngủ nghiêm trọng" }
                        ]
                    },
                    {
                        id: "stress_level",
                        text: "Mức độ căng thẳng trong cuộc sống hiện tại của bạn như thế nào?",
                        options: [
                            { value: 0, text: "Rất thấp" },
                            { value: 1, text: "Thấp" },
                            { value: 2, text: "Vừa phải" },
                            { value: 3, text: "Cao" },
                            { value: 4, text: "Rất cao" }
                        ]
                    }
                ]
            },
            phq9: {
                title: "Đánh giá trầm cảm (PHQ-9)",
                description: "Bộ câu hỏi tiêu chuẩn đánh giá mức độ trầm cảm",
                questions: [
                    {
                        id: "phq9_1",
                        text: "Ít hứng thú hoặc không vui vẻ khi làm việc",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "phq9_2",
                        text: "Cảm thấy buồn bã, chán nản hoặc tuyệt vọng",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "phq9_3",
                        text: "Khó ngủ hoặc ngủ nhiều",
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
                title: "Đánh giá lo âu (GAD-7)",
                description: "Bộ câu hỏi tiêu chuẩn đánh giá mức độ lo âu",
                questions: [
                    {
                        id: "gad7_1",
                        text: "Cảm thấy bồn chồn, lo lắng hoặc căng thẳng",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "gad7_2",
                        text: "Không thể ngừng lo lắng hoặc kiểm soát lo lắng",
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    },
                    {
                        id: "gad7_3",
                        text: "Lo lắng quá nhiều về những việc khác nhau",
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
                        options: [
                            { value: 0, text: "Không bao giờ" },
                            { value: 1, text: "Vài ngày" },
                            { value: 2, text: "Hơn một nửa số ngày" },
                            { value: 3, text: "Gần như mỗi ngày" }
                        ]
                    }
                ]
            }
        };
    }
    
    function startAssessment() {
        currentAssessmentType = 'initial_screening';
        currentQuestionIndex = 0;
        answers = {};
        
        updateAssessmentHeader();
        displayCurrentQuestion();
    }
    
    function updateAssessmentHeader() {
        const assessment = assessmentData[currentAssessmentType];
        if (assessment) {
            assessmentTitle.textContent = assessment.title;
            assessmentSubtitle.textContent = assessment.description;
        }
    }
    
    function displayCurrentQuestion() {
        const assessment = assessmentData[currentAssessmentType];
        const question = assessment.questions[currentQuestionIndex];
        
        if (!question) {
            handleAssessmentComplete();
            return;
        }
        
        // Update question info
        questionNumber.textContent = `Câu hỏi ${currentQuestionIndex + 1}`;
        questionCategory.textContent = assessment.title;
        questionText.textContent = question.text;
        
        // Update progress
        const totalQuestions = assessment.questions.length;
        const progress = ((currentQuestionIndex + 1) / totalQuestions) * 100;
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${currentQuestionIndex + 1}/${totalQuestions}`;
        
        // Generate answer options
        renderAnswerOptions(question);
        
        // Update navigation buttons
        updateNavigationButtons();
        
        // Load saved answer if exists
        loadSavedAnswer(question.id);
    }
    
    function renderAnswerOptions(question) {
        answerOptions.innerHTML = '';
        
        question.options.forEach((option, index) => {
            const optionElement = document.createElement('div');
            optionElement.className = 'answer-option';
            optionElement.setAttribute('data-value', option.value);
            optionElement.setAttribute('data-index', index);
            
            optionElement.innerHTML = `
                <div class="answer-radio"></div>
                <div class="answer-content">
                    <div class="answer-text">${option.text}</div>
                    <div class="answer-value">Điểm: ${option.value}</div>
                </div>
            `;
            
            optionElement.addEventListener('click', () => selectOption(index));
            answerOptions.appendChild(optionElement);
        });
    }
    
    function selectOption(index) {
        // Remove previous selection
        document.querySelectorAll('.answer-option').forEach(option => {
            option.classList.remove('selected');
        });
        
        // Select new option
        const selectedOption = document.querySelector(`[data-index="${index}"]`);
        if (selectedOption) {
            selectedOption.classList.add('selected');
            
            // Save answer
            const assessment = assessmentData[currentAssessmentType];
            const question = assessment.questions[currentQuestionIndex];
            const value = parseInt(selectedOption.getAttribute('data-value'));
            
            answers[question.id] = {
                value: value,
                text: question.options[index].text,
                questionText: question.text
            };
            
            // Update next button
            nextButton.disabled = false;
            
            // Save to localStorage
            saveProgress();
        }
    }
    
    function loadSavedAnswer(questionId) {
        if (answers[questionId]) {
            const savedValue = answers[questionId].value;
            const option = document.querySelector(`[data-value="${savedValue}"]`);
            if (option) {
                const index = parseInt(option.getAttribute('data-index'));
                selectOption(index);
            }
        }
    }
    
    function updateNavigationButtons() {
        prevButton.disabled = currentQuestionIndex === 0;
        nextButton.disabled = true; // Will be enabled when option is selected
        
        const assessment = assessmentData[currentAssessmentType];
        const isLastQuestion = currentQuestionIndex === assessment.questions.length - 1;
        
        nextButton.textContent = isLastQuestion ? 'Hoàn thành' : 'Tiếp tục';
    }
    
    function handlePreviousQuestion() {
        if (currentQuestionIndex > 0) {
            currentQuestionIndex--;
            displayCurrentQuestion();
        }
    }
    
    function handleNextQuestion() {
        const assessment = assessmentData[currentAssessmentType];
        const isLastQuestion = currentQuestionIndex === assessment.questions.length - 1;
        
        if (isLastQuestion) {
            handleAssessmentComplete();
        } else {
            currentQuestionIndex++;
            displayCurrentQuestion();
        }
    }
    
    function handleAssessmentComplete() {
        // Calculate scores
        const scores = calculateScores();
        
        // Save results
        saveResults(scores);
        
        // Show completion screen
        showCompletionScreen();
        
        // Send results to server
        submitResults(scores);
    }
    
    function calculateScores() {
        const scores = {};
        
        // Calculate score for current assessment
        let totalScore = 0;
        const assessment = assessmentData[currentAssessmentType];
        
        assessment.questions.forEach(question => {
            if (answers[question.id]) {
                totalScore += answers[question.id].value;
            }
        });
        
        scores[currentAssessmentType] = {
            score: totalScore,
            maxScore: assessment.questions.reduce((max, q) => max + Math.max(...q.options.map(o => o.value)), 0),
            severity: getSeverityLevel(currentAssessmentType, totalScore),
            answers: { ...answers }
        };
        
        return scores;
    }
    
    function getSeverityLevel(assessmentType, score) {
        const severityMappings = {
            initial_screening: [
                { min: 0, max: 4, level: 'minimal', label: 'Tối thiểu' },
                { min: 5, max: 9, level: 'mild', label: 'Nhẹ' },
                { min: 10, max: 14, level: 'moderate', label: 'Vừa phải' },
                { min: 15, max: 19, level: 'severe', label: 'Nặng' }
            ],
            phq9: [
                { min: 0, max: 4, level: 'minimal', label: 'Tối thiểu' },
                { min: 5, max: 9, level: 'mild', label: 'Nhẹ' },
                { min: 10, max: 14, level: 'moderate', label: 'Vừa phải' },
                { min: 15, max: 19, level: 'moderately_severe', label: 'Khá nặng' },
                { min: 20, max: 27, level: 'severe', label: 'Nặng' }
            ],
            gad7: [
                { min: 0, max: 4, level: 'minimal', label: 'Tối thiểu' },
                { min: 5, max: 9, level: 'mild', label: 'Nhẹ' },
                { min: 10, max: 14, level: 'moderate', label: 'Vừa phải' },
                { min: 15, max: 21, level: 'severe', label: 'Nặng' }
            ]
        };
        
        const mapping = severityMappings[assessmentType] || severityMappings.initial_screening;
        for (const range of mapping) {
            if (score >= range.min && score <= range.max) {
                return range;
            }
        }
        
        return mapping[mapping.length - 1]; // Return highest severity if score exceeds ranges
    }
    
    function saveResults(scores) {
        const results = {
            timestamp: new Date().toISOString(),
            assessmentType: currentAssessmentType,
            scores: scores,
            sessionId: generateSessionId()
        };
        
        localStorage.setItem('assessmentResults', JSON.stringify(results));
        localStorage.setItem('lastAssessmentType', currentAssessmentType);
    }
    
    function saveProgress() {
        const progress = {
            currentAssessmentType,
            currentQuestionIndex,
            answers,
            timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('assessmentProgress', JSON.stringify(progress));
    }
    
    function loadProgress() {
        const saved = localStorage.getItem('assessmentProgress');
        if (saved) {
            try {
                const progress = JSON.parse(saved);
                currentAssessmentType = progress.currentAssessmentType;
                currentQuestionIndex = progress.currentQuestionIndex;
                answers = progress.answers || {};
                return true;
            } catch (error) {
                console.error('Failed to load progress:', error);
            }
        }
        return false;
    }
    
    function generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    function showCompletionScreen() {
        questionCard.style.display = 'none';
        loadingState.style.display = 'none';
        completionScreen.style.display = 'block';
    }
    
    function submitResults(scores) {
        // Submit to API
        fetch('/api/assessment/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                assessmentType: currentAssessmentType,
                scores: scores,
                sessionId: generateSessionId(),
                timestamp: new Date().toISOString()
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Results submitted successfully:', data);
        })
        .catch(error => {
            console.error('Error submitting results:', error);
        });
    }
    
    function showLoading(message = 'Đang tải...') {
        questionCard.style.display = 'none';
        completionScreen.style.display = 'none';
        loadingState.style.display = 'block';
        
        const loadingText = loadingState.querySelector('.loading-text');
        if (loadingText) {
            loadingText.textContent = message;
        }
    }
    
    function hideLoading() {
        loadingState.style.display = 'none';
        questionCard.style.display = 'block';
    }
    
    // Check for saved progress on load
    if (loadProgress()) {
        updateAssessmentHeader();
        displayCurrentQuestion();
    }
    
    // Auto-save progress periodically
    setInterval(saveProgress, 30000); // Save every 30 seconds
    
    // Handle page visibility change
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            saveProgress();
        }
    });
    
    // Handle beforeunload to save progress
    window.addEventListener('beforeunload', function() {
        saveProgress();
    });
    
    // Utility functions
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: var(--color-${type === 'error' ? 'error' : 'success'});
            color: white;
            border-radius: 0.5rem;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
    
    // Export functions for external use
    window.assessmentController = {
        startAssessment: startAssessment,
        selectOption: selectOption,
        nextQuestion: handleNextQuestion,
        previousQuestion: handlePreviousQuestion,
        getCurrentProgress: () => ({
            assessmentType: currentAssessmentType,
            questionIndex: currentQuestionIndex,
            totalQuestions: assessmentData[currentAssessmentType]?.questions.length || 0,
            answers: answers
        })
    };
});