/**
 * Assessment.js - Enhanced Assessment Interface with Beautiful Animations
 * Handles assessment selection, question display, and result processing
 */

class AssessmentInterface {
    constructor() {
        // DOM Elements
        this.assessmentSelection = document.getElementById('assessment-selection');
        this.assessmentInterface = document.getElementById('assessment-interface');
        this.resultsSection = document.getElementById('results-section');
        
        // Progress elements
        this.currentAssessmentTitle = document.getElementById('current-assessment-title');
        this.progressBar = document.getElementById('progress-bar');
        this.progressText = document.getElementById('progress-text');
        
        // Question elements
        this.questionContainer = document.getElementById('question-container');
        this.questionText = document.getElementById('question-text');
        this.answerOptions = document.getElementById('answer-options');
        this.questionCard = this.questionContainer?.querySelector('.question-card');
        
        // Navigation elements
        this.prevButton = document.getElementById('prev-question');
        this.nextButton = document.getElementById('next-question');
        
        // Results elements
        this.totalScore = document.getElementById('total-score');
        this.scoreLevel = document.getElementById('score-level');
        this.scoreDescription = document.getElementById('score-description');
        
        // State
        this.currentAssessment = null;
        this.currentQuestionIndex = 0;
        this.answers = {};
        this.sessionId = this.generateSessionId();
        this.isTransitioning = false;
        
        // Debug mode
        this.debugMode = true;
        
        this.init();
    }
    
    init() {
        this.log('Initializing Enhanced Assessment Interface...');
        this.setupEventListeners();
        this.addEnhancedStyles();
        this.log('Assessment Interface initialized successfully');
    }
    
    addEnhancedStyles() {
        // Add dynamic styles for smooth animations
        const style = document.createElement('style');
        style.textContent = `
            .question-changing {
                pointer-events: none;
            }
            
            .option-selecting {
                animation: optionSelect 0.3s ease-out;
            }
            
            @keyframes optionSelect {
                0% { transform: scale(1); }
                50% { transform: scale(0.95); }
                100% { transform: scale(1); }
            }
            
            .progress-updating .progress-bar {
                transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .score-counting {
                animation: scoreCount 1.5s ease-out;
            }
            
            @keyframes scoreCount {
                0% { transform: scale(0.8); opacity: 0; }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    setupEventListeners() {
        // Assessment selection buttons
        const assessmentButtons = document.querySelectorAll('.select-assessment-btn');
        assessmentButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const assessmentType = button.getAttribute('data-assessment');
                this.log(`Assessment button clicked: ${assessmentType}`);
                
                // Add button animation
                button.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    button.style.transform = '';
                    this.startAssessment(assessmentType);
                }, 150);
            });
        });
        
        // Navigation buttons
        if (this.prevButton) {
            this.prevButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.previousQuestion();
            });
        }
        
        if (this.nextButton) {
            this.nextButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.nextQuestion();
            });
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (this.currentAssessment && !this.isTransitioning) {
                if (e.key === 'ArrowLeft' && !this.prevButton?.disabled) {
                    e.preventDefault();
                    this.previousQuestion();
                } else if (e.key === 'ArrowRight' && !this.nextButton?.disabled) {
                    e.preventDefault();
                    this.nextQuestion();
                } else if (e.key >= '1' && e.key <= '4') {
                    e.preventDefault();
                    const answerValue = parseInt(e.key) - 1;
                    this.selectAnswer(answerValue);
                } else if (e.key === 'Enter' && !this.nextButton?.disabled) {
                    e.preventDefault();
                    this.nextQuestion();
                }
            }
        });
    }
    
    async startAssessment(assessmentType) {
        this.log(`Starting assessment: ${assessmentType}`);
        
        try {
            // Show loading with beautiful animation
            this.showEnhancedLoading('🧠 Đang khởi tạo đánh giá...', 'Vui lòng chờ trong giây lát');
            
            // Call API to start assessment
            const response = await fetch('/api/assessment/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    assessment_type: assessmentType,
                    session_id: this.sessionId,
                    language: 'vi',
                    mode: 'poll'
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.currentAssessment = data;
                this.currentQuestionIndex = 0;
                this.answers = {};
                
                this.log('Assessment data received:', data);
                
                // Hide loading and transition to assessment
                await this.hideLoading();
                await this.transitionToAssessment();
            } else {
                throw new Error(data.message || 'Failed to start assessment');
            }
            
        } catch (error) {
            this.log('Error starting assessment:', error);
            await this.hideLoading();
            this.showEnhancedError('❌ Không thể bắt đầu đánh giá', 'Vui lòng kiểm tra kết nối mạng và thử lại.');
        }
    }
    
    async transitionToAssessment() {
        // Smooth transition from selection to assessment
        if (this.assessmentSelection) {
            this.assessmentSelection.style.transition = 'all 0.6s ease-out';
            this.assessmentSelection.style.transform = 'translateY(-50px)';
            this.assessmentSelection.style.opacity = '0';
            
            await this.delay(300);
            this.assessmentSelection.style.display = 'none';
        }
        
        // Show assessment interface with animation
        if (this.assessmentInterface) {
            this.assessmentInterface.style.display = 'block';
            this.assessmentInterface.style.opacity = '0';
            this.assessmentInterface.style.transform = 'translateY(50px)';
            
            // Update title with typewriter effect
            if (this.currentAssessmentTitle && this.currentAssessment.questionnaire) {
                await this.typewriterEffect(this.currentAssessmentTitle, this.currentAssessment.questionnaire.title);
            }
            
            // Animate interface appearance
            this.assessmentInterface.style.transition = 'all 0.6s ease-out';
            this.assessmentInterface.style.opacity = '1';
            this.assessmentInterface.style.transform = 'translateY(0)';
            
            await this.delay(600);
            this.displayCurrentQuestion();
        }
    }
    
    async typewriterEffect(element, text, speed = 50) {
        element.textContent = '';
        for (let i = 0; i < text.length; i++) {
            element.textContent += text.charAt(i);
            await this.delay(speed);
        }
    }
    
    async displayCurrentQuestion() {
        if (!this.currentAssessment || !this.currentAssessment.questionnaire) {
            this.log('No assessment data available');
            return;
        }
        
        const questions = this.currentAssessment.questionnaire.questions;
        const currentQuestion = questions[this.currentQuestionIndex];
        
        if (!currentQuestion) {
            this.log('No current question found');
            return;
        }
        
        this.log(`Displaying question ${this.currentQuestionIndex + 1}/${questions.length}`);
        
        // Start transition
        this.isTransitioning = true;
        
        // Add transition class to question card
        if (this.questionCard) {
            this.questionCard.classList.add('question-changing');
        }
        
        // Fade out current content
        if (this.questionText) {
            this.questionText.style.transition = 'all 0.3s ease-out';
            this.questionText.style.opacity = '0';
            this.questionText.style.transform = 'translateX(-30px)';
        }
        
        if (this.answerOptions) {
            this.answerOptions.style.transition = 'all 0.3s ease-out';
            this.answerOptions.style.opacity = '0';
            this.answerOptions.style.transform = 'translateX(-30px)';
        }
        
        await this.delay(300);
        
        // Update question text with animation
        if (this.questionText) {
            this.questionText.textContent = currentQuestion.text;
            this.questionText.style.opacity = '1';
            this.questionText.style.transform = 'translateX(0)';
        }
        
        // Update progress with animation
        this.updateProgressAnimated();
        
        await this.delay(200);
        
        // Display answer options with staggered animation
        await this.displayAnswerOptionsAnimated(currentQuestion);
        
        // Update navigation
        this.updateNavigation();
        
        // Remove transition class
        if (this.questionCard) {
            this.questionCard.classList.remove('question-changing');
        }
        
        this.isTransitioning = false;
    }
    
    async displayAnswerOptionsAnimated(question) {
        if (!this.answerOptions) return;
        
        this.answerOptions.innerHTML = '';
        this.answerOptions.style.opacity = '1';
        this.answerOptions.style.transform = 'translateX(0)';
        
        const currentAnswer = this.answers[question.id];
        
        for (let index = 0; index < question.options.length; index++) {
            const option = question.options[index];
            const optionElement = document.createElement('div');
            optionElement.className = 'answer-option';
            optionElement.setAttribute('data-value', option.value);
            
            // Check if this option is already selected
            if (currentAnswer !== undefined && currentAnswer === option.value) {
                optionElement.classList.add('selected');
            }
            
            optionElement.innerHTML = `
                <div class="option-content">
                    <div class="option-number">${option.value}</div>
                    <div class="option-text">${option.text}</div>
                </div>
            `;
            
            // Add click handler with animation
            optionElement.addEventListener('click', () => {
                if (!this.isTransitioning) {
                    this.selectAnswerAnimated(option.value, question.id, optionElement);
                }
            });
            
            // Add hover effects
            optionElement.addEventListener('mouseenter', () => {
                if (!optionElement.classList.contains('selected')) {
                    optionElement.style.transform = 'translateY(-2px) scale(1.01)';
                }
            });
            
            optionElement.addEventListener('mouseleave', () => {
                if (!optionElement.classList.contains('selected')) {
                    optionElement.style.transform = '';
                }
            });
            
            // Initial animation state
            optionElement.style.opacity = '0';
            optionElement.style.transform = 'translateY(30px)';
            
            this.answerOptions.appendChild(optionElement);
            
            // Animate in with delay
            await this.delay(100);
            optionElement.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            optionElement.style.opacity = '1';
            optionElement.style.transform = 'translateY(0)';
        }
    }
    
    async selectAnswerAnimated(value, questionId = null, optionElement = null) {
        if (!this.currentAssessment) return;
        
        const questions = this.currentAssessment.questionnaire.questions;
        const currentQuestion = questions[this.currentQuestionIndex];
        const qId = questionId || currentQuestion.id;
        
        // Store answer
        this.answers[qId] = value;
        
        this.log(`Answer selected: ${qId} = ${value}`);
        
        // Animate selection
        if (optionElement) {
            optionElement.classList.add('option-selecting');
            await this.delay(300);
        }
        
        // Update UI with smooth animations
        const options = this.answerOptions.querySelectorAll('.answer-option');
        
        for (const option of options) {
            option.classList.remove('selected');
            const optionValue = parseInt(option.getAttribute('data-value'));
            
            if (optionValue === value) {
                option.classList.add('selected');
                
                // Success animation
                const numberElement = option.querySelector('.option-number');
                if (numberElement) {
                    numberElement.style.animation = 'successPop 0.6s ease-out';
                }
                
                // Add checkmark animation
                this.addSuccessIndicator(option);
            } else {
                // Subtle fade for unselected options
                option.style.opacity = '0.7';
                setTimeout(() => {
                    if (!option.classList.contains('selected')) {
                        option.style.opacity = '1';
                    }
                }, 500);
            }
        }
        
        // Enable next button with animation
        this.updateNavigation();
        
        // Show positive feedback
        this.showQuickFeedback('✅ Đã ghi nhận câu trả lời');
        
        // Auto-advance option (disabled by default for better UX)
        // setTimeout(() => {
        //     if (this.currentQuestionIndex < questions.length - 1) {
        //         this.nextQuestion();
        //     }
        // }, 1000);
    }
    
    addSuccessIndicator(optionElement) {
        const existingIndicator = optionElement.querySelector('.success-indicator');
        if (existingIndicator) return;
        
        const indicator = document.createElement('div');
        indicator.className = 'success-indicator';
        indicator.innerHTML = '✓';
        
        const optionContent = optionElement.querySelector('.option-content');
        if (optionContent) {
            optionContent.appendChild(indicator);
        }
    }
    
    updateProgressAnimated() {
        if (!this.currentAssessment) return;
        
        const questions = this.currentAssessment.questionnaire.questions;
        const progress = ((this.currentQuestionIndex + 1) / questions.length) * 100;
        
        // Add progress updating class
        const progressContainer = this.progressBar?.closest('.progress-container');
        if (progressContainer) {
            progressContainer.classList.add('progress-updating');
        }
        
        // Animate progress bar
        if (this.progressBar) {
            this.progressBar.style.width = `${progress}%`;
        }
        
        // Animate progress text with counting effect
        if (this.progressText) {
            const currentText = this.progressText.textContent;
            const newText = `${this.currentQuestionIndex + 1}/${questions.length}`;
            
            if (currentText !== newText) {
                this.progressText.style.animation = 'scoreCount 0.6s ease-out';
                this.progressText.textContent = newText;
                
                setTimeout(() => {
                    this.progressText.style.animation = '';
                }, 600);
            }
        }
        
        // Remove progress updating class
        setTimeout(() => {
            if (progressContainer) {
                progressContainer.classList.remove('progress-updating');
            }
        }, 800);
    }
    
    updateNavigation() {
        if (!this.currentAssessment) return;
        
        const questions = this.currentAssessment.questionnaire.questions;
        const currentQuestion = questions[this.currentQuestionIndex];
        const hasAnswer = this.answers[currentQuestion.id] !== undefined;
        
        // Previous button with animation
        if (this.prevButton) {
            const wasDisabled = this.prevButton.disabled;
            this.prevButton.disabled = this.currentQuestionIndex === 0;
            
            if (wasDisabled !== this.prevButton.disabled) {
                this.prevButton.style.transition = 'all 0.3s ease';
            }
        }
        
        // Next button with animation
        if (this.nextButton) {
            const wasDisabled = this.nextButton.disabled;
            
            if (this.currentQuestionIndex === questions.length - 1) {
                this.nextButton.innerHTML = `
                    Hoàn thành
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="20,6 12,18 4,12"/>
                    </svg>
                `;
                this.nextButton.disabled = !hasAnswer;
            } else {
                this.nextButton.innerHTML = `
                    Câu tiếp
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="9,18 15,12 9,6"/>
                    </svg>
                `;
                this.nextButton.disabled = !hasAnswer;
            }
            
            if (wasDisabled !== this.nextButton.disabled) {
                this.nextButton.style.transition = 'all 0.3s ease';
                if (!this.nextButton.disabled) {
                    this.nextButton.style.animation = 'successPop 0.6s ease-out';
                    setTimeout(() => {
                        this.nextButton.style.animation = '';
                    }, 600);
                }
            }
        }
    }
    
    async previousQuestion() {
        if (this.currentQuestionIndex > 0 && !this.isTransitioning) {
            this.currentQuestionIndex--;
            await this.displayCurrentQuestion();
            this.showQuickFeedback('← Quay lại câu trước');
        }
    }
    
    async nextQuestion() {
        if (!this.currentAssessment || this.isTransitioning) return;
        
        const questions = this.currentAssessment.questionnaire.questions;
        
        if (this.currentQuestionIndex < questions.length - 1) {
            this.currentQuestionIndex++;
            await this.displayCurrentQuestion();
            this.showQuickFeedback('→ Chuyển sang câu tiếp');
        } else {
            // Assessment complete
            await this.completeAssessment();
        }
    }
    
    async completeAssessment() {
        this.log('Completing assessment...');
        
        try {
            // Show completion loading
            this.showEnhancedLoading('🎯 Đang xử lý kết quả...', 'Chúng tôi đang phân tích câu trả lời của bạn');
            
            // Submit assessment
            const response = await fetch('/api/assessment/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    assessment_type: this.currentAssessment.assessment_type,
                    session_id: this.sessionId,
                    answers: this.answers,
                    completed_at: new Date().toISOString()
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const results = await response.json();
            
            if (results.success) {
                await this.hideLoading();
                await this.displayResultsAnimated(results);
            } else {
                throw new Error(results.message || 'Failed to process results');
            }
            
        } catch (error) {
            this.log('Error completing assessment:', error);
            await this.hideLoading();
            this.showEnhancedError('❌ Không thể xử lý kết quả', 'Vui lòng thử lại hoặc liên hệ hỗ trợ.');
        }
    }
    
    async displayResultsAnimated(results) {
        this.log('Displaying results with animations:', results);
        
        // Hide assessment interface with animation
        if (this.assessmentInterface) {
            this.assessmentInterface.style.transition = 'all 0.6s ease-out';
            this.assessmentInterface.style.transform = 'translateY(-50px)';
            this.assessmentInterface.style.opacity = '0';
            
            await this.delay(300);
            this.assessmentInterface.style.display = 'none';
        }
        
        // Show results section with animation
        if (this.resultsSection) {
            this.resultsSection.style.display = 'block';
            this.resultsSection.style.opacity = '0';
            this.resultsSection.style.transform = 'translateY(50px)';
            
            await this.delay(200);
            
            this.resultsSection.style.transition = 'all 0.8s ease-out';
            this.resultsSection.style.opacity = '1';
            this.resultsSection.style.transform = 'translateY(0)';
            
            await this.delay(500);
            
            // Animate score with counting effect
            if (this.totalScore) {
                await this.animateCounter(this.totalScore, 0, results.results.total_score, 1500);
            }
            
            // Update severity level with animation
            if (this.scoreLevel) {
                await this.delay(300);
                this.scoreLevel.textContent = this.getSeverityLabel(results.results.severity);
                this.scoreLevel.className = `level-indicator ${results.results.severity}`;
                this.scoreLevel.style.animation = 'slideInLeft 0.6s ease-out';
            }
            
            // Update description with typewriter effect
            if (this.scoreDescription) {
                await this.delay(500);
                await this.typewriterEffect(this.scoreDescription, results.results.severity_description, 30);
            }
            
            // Display recommendations with staggered animation
            await this.delay(300);
            this.displayRecommendationsAnimated(results.recommendations);
            
            // Scroll to top of results
            this.resultsSection.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
    
    async animateCounter(element, startValue, endValue, duration) {
        const startTime = performance.now();
        const range = endValue - startValue;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = Math.round(startValue + (range * easeOutQuart));
            
            element.textContent = currentValue;
            element.classList.add('score-counting');
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.classList.remove('score-counting');
            }
        };
        
        requestAnimationFrame(animate);
        return new Promise(resolve => setTimeout(resolve, duration));
    }
    
    async displayRecommendationsAnimated(recommendations) {
        const recommendationsContainer = document.getElementById('recommendations-list');
        if (!recommendationsContainer || !recommendations) return;
        
        recommendationsContainer.innerHTML = '';
        
        for (let i = 0; i < recommendations.length; i++) {
            const rec = recommendations[i];
            const recElement = document.createElement('div');
            recElement.className = `recommendation-item ${rec.priority}`;
            
            recElement.innerHTML = `
                <div class="recommendation-header">
                    <h4 class="recommendation-title">${rec.title}</h4>
                    <span class="recommendation-priority ${rec.priority}">${this.getPriorityLabel(rec.priority)}</span>
                </div>
                <p class="recommendation-description">${rec.description}</p>
                <ul class="recommendation-actions">
                    ${rec.actions.map(action => `<li>${action}</li>`).join('')}
                </ul>
            `;
            
            // Initial animation state
            recElement.style.opacity = '0';
            recElement.style.transform = 'translateY(30px)';
            
            recommendationsContainer.appendChild(recElement);
            
            // Animate in with staggered delay
            await this.delay(200);
            recElement.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            recElement.style.opacity = '1';
            recElement.style.transform = 'translateY(0)';
        }
    }
    
    showEnhancedLoading(title, message = '') {
        // Create enhanced loading overlay
        let loadingOverlay = document.getElementById('loading-overlay');
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'loading-overlay';
            loadingOverlay.className = 'loading-overlay';
            document.body.appendChild(loadingOverlay);
        }
        
        loadingOverlay.innerHTML = `
            <div class="loading-content" style="
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                padding: 3rem;
                border-radius: 2rem;
                text-align: center;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.2);
                max-width: 400px;
                margin: 0 auto;
                animation: fadeInScale 0.6s ease-out;
            ">
                <div class="loading-spinner" style="
                    width: 60px;
                    height: 60px;
                    border: 4px solid rgba(16, 185, 129, 0.1);
                    border-left: 4px solid #10b981;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 2rem;
                "></div>
                <h3 style="
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: #1f2937;
                    margin: 0 0 1rem 0;
                ">${title}</h3>
                <p style="
                    color: #6b7280;
                    margin: 0;
                    line-height: 1.6;
                ">${message}</p>
            </div>
        `;
        
        loadingOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            backdrop-filter: blur(5px);
        `;
        
        loadingOverlay.style.display = 'flex';
    }
    
    async hideLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.transition = 'all 0.4s ease-out';
            loadingOverlay.style.opacity = '0';
            loadingOverlay.style.transform = 'scale(0.9)';
            
            await this.delay(400);
            loadingOverlay.style.display = 'none';
        }
    }
    
    showEnhancedError(title, message) {
        this.hideLoading();
        
        // Create enhanced error notification
        const errorNotification = document.createElement('div');
        errorNotification.className = 'error-notification';
        errorNotification.style.cssText = `
            position: fixed;
            top: 2rem;
            right: 2rem;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border: 2px solid #ef4444;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(239, 68, 68, 0.3);
            z-index: 10000;
            max-width: 400px;
            animation: slideInRight 0.6s ease-out;
        `;
        
        errorNotification.innerHTML = `
            <div style="display: flex; align-items: flex-start; gap: 1rem;">
                <div style="
                    width: 48px;
                    height: 48px;
                    background: linear-gradient(135deg, #ef4444, #dc2626);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 1.5rem;
                    flex-shrink: 0;
                ">❌</div>
                <div style="flex: 1;">
                    <h4 style="
                        margin: 0 0 0.5rem 0;
                        color: #1f2937;
                        font-weight: 700;
                        font-size: 1.125rem;
                    ">${title}</h4>
                    <p style="
                        margin: 0;
                        color: #6b7280;
                        line-height: 1.5;
                    ">${message}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    font-size: 1.5rem;
                    color: #ef4444;
                    cursor: pointer;
                    padding: 0;
                    width: 32px;
                    height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    transition: background 0.2s ease;
                " onmouseover="this.style.background='rgba(239,68,68,0.1)'" 
                   onmouseout="this.style.background='none'">×</button>
            </div>
        `;
        
        document.body.appendChild(errorNotification);
        
        // Auto-remove after 8 seconds
        setTimeout(() => {
            if (errorNotification.parentElement) {
                errorNotification.style.animation = 'slideOutRight 0.4s ease-in';
                setTimeout(() => errorNotification.remove(), 400);
            }
        }, 8000);
    }
    
    showQuickFeedback(message, type = 'success') {
        const feedback = document.createElement('div');
        feedback.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: ${type === 'success' ? 'rgba(16, 185, 129, 0.95)' : 'rgba(59, 130, 246, 0.95)'};
            color: white;
            padding: 1rem 2rem;
            border-radius: 2rem;
            font-weight: 600;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            z-index: 10001;
            animation: quickFeedback 1.5s ease-out;
            backdrop-filter: blur(10px);
        `;
        
        feedback.textContent = message;
        document.body.appendChild(feedback);
        
        setTimeout(() => feedback.remove(), 1500);
    }
    
    getSeverityLabel(severity) {
        const labels = {
            'minimal': 'Tối thiểu',
            'mild': 'Nhẹ',
            'moderate': 'Vừa phải',
            'moderately_severe': 'Khá nặng',
            'severe': 'Nặng',
            'extremely_severe': 'Rất nặng',
            'normal': 'Bình thường',
            'low': 'Thấp',
            'high': 'Cao'
        };
        return labels[severity] || severity;
    }
    
    getPriorityLabel(priority) {
        const labels = {
            'low': 'Thấp',
            'medium': 'Trung bình',
            'high': 'Cao',
            'urgent': 'Khẩn cấp'
        };
        return labels[priority] || priority;
    }
    
    generateSessionId() {
        return 'assessment_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    log(...args) {
        if (this.debugMode) {
            console.log('[Assessment Enhanced]', ...args);
        }
    }
    
    // Public methods for external use
    async restartAssessment() {
        this.currentAssessment = null;
        this.currentQuestionIndex = 0;
        this.answers = {};
        this.sessionId = this.generateSessionId();
        this.isTransitioning = false;
        
        // Animate transition back to selection
        if (this.resultsSection) {
            this.resultsSection.style.transition = 'all 0.6s ease-out';
            this.resultsSection.style.opacity = '0';
            this.resultsSection.style.transform = 'translateY(50px)';
            
            await this.delay(300);
            this.resultsSection.style.display = 'none';
        }
        
        if (this.assessmentInterface) {
            this.assessmentInterface.style.display = 'none';
        }
        
        if (this.assessmentSelection) {
            this.assessmentSelection.style.display = 'block';
            this.assessmentSelection.style.opacity = '0';
            this.assessmentSelection.style.transform = 'translateY(30px)';
            
            await this.delay(200);
            this.assessmentSelection.style.transition = 'all 0.6s ease-out';
            this.assessmentSelection.style.opacity = '1';
            this.assessmentSelection.style.transform = 'translateY(0)';
        }
        
        this.showQuickFeedback('🔄 Đã khởi tạo lại đánh giá');
    }
    
    exportResults() {
        if (!this.currentAssessment) {
            this.showEnhancedError('❌ Không có kết quả', 'Vui lòng hoàn thành đánh giá trước khi xuất kết quả.');
            return;
        }
        
        // Implementation for export functionality
        this.log('Export functionality not yet implemented');
        this.showQuickFeedback('🚧 Đang phát triển...', 'info');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Enhanced Assessment Interface...');
    
    // Add additional CSS animations
    const additionalCSS = `
        <style>
        @keyframes fadeInScale {
            0% { opacity: 0; transform: scale(0.8); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        @keyframes slideInRight {
            0% { opacity: 0; transform: translateX(100%); }
            100% { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes slideOutRight {
            0% { opacity: 1; transform: translateX(0); }
            100% { opacity: 0; transform: translateX(100%); }
        }
        
        @keyframes quickFeedback {
            0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
            20% { opacity: 1; transform: translate(-50%, -50%) scale(1.05); }
            80% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            100% { opacity: 0; transform: translate(-50%, -50%) scale(0.95); }
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .assessment-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }
        
        .select-assessment-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
        }
        
        .select-assessment-btn:active {
            transform: translateY(0) scale(0.98);
        }
        </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', additionalCSS);
    
    // Initialize the enhanced assessment interface
    window.assessmentInterface = new AssessmentInterface();
});