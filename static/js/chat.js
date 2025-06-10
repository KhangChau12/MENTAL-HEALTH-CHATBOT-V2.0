/**
 * Chat.js - AI Chat Mode Implementation
 * Handles chat interface, message flow, and transition to assessment
 */

class ChatInterface {
    constructor() {
        // DOM Elements
        this.chatContainer = document.getElementById('chat-container');
        this.messagesContainer = document.getElementById('messages-container');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-button');
        this.chatForm = document.getElementById('chat-form');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.pollContainer = document.getElementById('poll-container');
        this.chatModeIndicator = document.getElementById('chat-mode-indicator');
        
        // Poll elements
        this.pollQuestion = document.getElementById('poll-question');
        this.pollOptions = document.getElementById('poll-options');
        this.pollProgressBar = document.getElementById('poll-progress-bar');
        this.pollProgress = document.getElementById('poll-progress');
        this.pollPrevButton = document.getElementById('poll-previous');
        this.pollNextButton = document.getElementById('poll-next');
        
        // State
        this.conversation = {
            history: [],
            state: this.initializeState(),
            currentPhase: 'chat', // 'chat' or 'poll'
            isLoading: false
        };
        
        // Assessment state
        this.assessment = {
            data: null,
            currentQuestionIndex: 0,
            answers: {},
            totalQuestions: 0
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.showWelcomeMessage();
        this.updateUI();
        
        // Auto-focus input
        if (this.userInput) {
            this.userInput.focus();
        }
    }
    
    initializeState() {
        return {
            session_id: this.generateSessionId(),
            current_phase: 'chat',
            language: 'vi',
            message_count: 0,
            scores: {},
            started_at: new Date().toISOString()
        };
    }
    
    generateSessionId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    setupEventListeners() {
        // Chat form submission
        if (this.chatForm) {
            this.chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSendMessage();
            });
        }
        
        // Input handling
        if (this.userInput) {
            this.userInput.addEventListener('input', () => {
                this.updateSendButton();
                this.autoResizeInput();
            });
            
            this.userInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSendMessage();
                }
            });
        }
        
        // Poll navigation
        if (this.pollPrevButton) {
            this.pollPrevButton.addEventListener('click', () => {
                this.handlePollPrevious();
            });
        }
        
        if (this.pollNextButton) {
            this.pollNextButton.addEventListener('click', () => {
                this.handlePollNext();
            });
        }
    }
    
    showWelcomeMessage() {
        const welcomeMessage = {
            role: 'bot',
            content: 'Xin chào! Tôi là trợ lý sức khỏe tâm thần. Tôi sẽ giúp bạn đánh giá sơ bộ tình trạng sức khỏe tâm thần của mình. Hãy chia sẻ với tôi những gì đang khiến bạn lo lắng hoặc bất kỳ điều gì bạn muốn nói về tâm trạng của mình gần đây.',
            timestamp: new Date()
        };
        
        this.conversation.history.push(welcomeMessage);
        this.addMessageToUI(welcomeMessage);
        
        // Set welcome time
        const welcomeTimeElement = document.getElementById('welcome-time');
        if (welcomeTimeElement) {
            welcomeTimeElement.textContent = this.formatTime(new Date());
        }
    }
    
    async handleSendMessage() {
        const message = this.userInput.value.trim();
        
        if (!message || this.conversation.isLoading) {
            return;
        }
        
        // Add user message to UI and conversation
        const userMessage = {
            role: 'user',
            content: message,
            timestamp: new Date()
        };
        
        this.conversation.history.push(userMessage);
        this.addMessageToUI(userMessage);
        
        // Clear input and show loading
        this.userInput.value = '';
        this.updateSendButton();
        this.showTypingIndicator();
        this.conversation.isLoading = true;
        
        try {
            // Send message to backend
            const response = await this.sendMessageToAPI(message);
            
            if (response.success) {
                this.handleAPIResponse(response.data);
            } else {
                this.handleAPIError(response.error);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.handleAPIError('Kết nối không ổn định. Vui lòng thử lại.');
        } finally {
            this.hideTypingIndicator();
            this.conversation.isLoading = false;
        }
    }
    
    async sendMessageToAPI(message) {
        try {
            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    history: this.conversation.history.slice(0, -1), // Exclude the current user message
                    state: this.conversation.state,
                    use_ai: true
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                return { success: false, error: data.message || data.error };
            }
            
            return { success: true, data: data };
            
        } catch (error) {
            console.error('API request failed:', error);
            return { 
                success: false, 
                error: 'Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.' 
            };
        }
    }
    
    handleAPIResponse(data) {
        // Update conversation state
        if (data.state) {
            this.conversation.state = data.state;
        }
        
        if (data.history) {
            this.conversation.history = data.history;
        }
        
        // Add bot response to UI
        if (data.message) {
            const botMessage = {
                role: 'bot',
                content: data.message,
                timestamp: new Date()
            };
            
            // Only add if not already in history
            const lastMessage = this.conversation.history[this.conversation.history.length - 1];
            if (!lastMessage || lastMessage.content !== data.message) {
                this.conversation.history.push(botMessage);
            }
            
            this.addMessageToUI(botMessage);
        }
        
        // Check if we should transition to poll mode
        if (data.metadata && data.metadata.should_show_poll && data.assessment) {
            this.transitionToPoll(data.assessment);
        }
        
        this.updateUI();
    }
    
    handleAPIError(error) {
        const errorMessage = {
            role: 'bot',
            content: error || 'Xin lỗi, tôi gặp chút khó khăn. Bạn có thể thử lại không?',
            timestamp: new Date(),
            isError: true
        };
        
        this.conversation.history.push(errorMessage);
        this.addMessageToUI(errorMessage);
    }
    
    addMessageToUI(message) {
        if (!this.messagesContainer) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.role}`;
        
        if (message.isError) {
            messageElement.classList.add('error');
        }
        
        messageElement.innerHTML = `
            <div class="message-avatar">
                ${message.role === 'user' ? '👤' : '🤖'}
            </div>
            <div class="message-content">
                <p>${this.escapeHtml(message.content)}</p>
                <div class="message-time">${this.formatTime(message.timestamp)}</div>
            </div>
        `;
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
        
        // Add animation
        setTimeout(() => {
            messageElement.classList.add('show');
        }, 10);
    }
    
    transitionToPoll(assessmentData) {
        this.conversation.currentPhase = 'poll';
        this.assessment.data = assessmentData;
        this.assessment.currentQuestionIndex = 0;
        this.assessment.answers = {};
        this.assessment.totalQuestions = assessmentData.questions ? assessmentData.questions.length : 0;
        
        // Update mode indicator
        if (this.chatModeIndicator) {
            this.chatModeIndicator.textContent = 'Chế độ Đánh giá';
            this.chatModeIndicator.classList.add('assessment-mode');
        }
        
        // Show poll container and hide chat input
        this.showPollInterface();
        this.displayCurrentQuestion();
    }
    
    showPollInterface() {
        if (this.pollContainer) {
            this.pollContainer.classList.add('show');
        }
        
        // Hide chat input
        const chatInputContainer = document.querySelector('.chat-input-container');
        if (chatInputContainer) {
            chatInputContainer.style.display = 'none';
        }
    }
    
    hidePollInterface() {
        if (this.pollContainer) {
            this.pollContainer.classList.remove('show');
        }
        
        // Show chat input
        const chatInputContainer = document.querySelector('.chat-input-container');
        if (chatInputContainer) {
            chatInputContainer.style.display = 'block';
        }
    }
    
    displayCurrentQuestion() {
        if (!this.assessment.data || !this.assessment.data.questions) {
            return;
        }
        
        const question = this.assessment.data.questions[this.assessment.currentQuestionIndex];
        
        if (!question) {
            this.completeAssessment();
            return;
        }
        
        // Update question text
        if (this.pollQuestion) {
            this.pollQuestion.textContent = question.text;
        }
        
        // Update progress
        this.updatePollProgress();
        
        // Display options
        this.displayQuestionOptions(question);
        
        // Update navigation buttons
        this.updatePollNavigation();
    }
    
    displayQuestionOptions(question) {
        if (!this.pollOptions) return;
        
        this.pollOptions.innerHTML = '';
        
        if (!question.options) return;
        
        question.options.forEach((option, index) => {
            const optionElement = document.createElement('div');
            optionElement.className = 'poll-option';
            optionElement.dataset.value = option.value || index;
            
            const currentAnswer = this.assessment.answers[question.id];
            if (currentAnswer == (option.value || index)) {
                optionElement.classList.add('selected');
            }
            
            optionElement.innerHTML = `
                <span class="option-text">${option.text}</span>
                <span class="option-value">${option.value || index}</span>
            `;
            
            optionElement.addEventListener('click', () => {
                this.selectPollOption(question.id, option.value || index, optionElement);
            });
            
            this.pollOptions.appendChild(optionElement);
        });
    }
    
    selectPollOption(questionId, value, element) {
        // Remove previous selections
        const allOptions = this.pollOptions.querySelectorAll('.poll-option');
        allOptions.forEach(opt => opt.classList.remove('selected'));
        
        // Select current option
        element.classList.add('selected');
        
        // Save answer
        this.assessment.answers[questionId] = value;
        
        // Update navigation
        this.updatePollNavigation();
    }
    
    updatePollProgress() {
        const current = this.assessment.currentQuestionIndex + 1;
        const total = this.assessment.totalQuestions;
        const percentage = (current / total) * 100;
        
        if (this.pollProgressBar) {
            this.pollProgressBar.style.width = `${percentage}%`;
        }
        
        if (this.pollProgress) {
            this.pollProgress.textContent = `${current}/${total}`;
        }
    }
    
    updatePollNavigation() {
        const currentQuestion = this.assessment.data.questions[this.assessment.currentQuestionIndex];
        const hasAnswer = currentQuestion && this.assessment.answers[currentQuestion.id] !== undefined;
        
        // Previous button
        if (this.pollPrevButton) {
            this.pollPrevButton.disabled = this.assessment.currentQuestionIndex === 0;
        }
        
        // Next button
        if (this.pollNextButton) {
            this.pollNextButton.disabled = !hasAnswer;
            
            // Update button text for last question
            if (this.assessment.currentQuestionIndex === this.assessment.totalQuestions - 1) {
                this.pollNextButton.textContent = 'Hoàn thành';
            } else {
                this.pollNextButton.textContent = 'Tiếp tục →';
            }
        }
    }
    
    handlePollPrevious() {
        if (this.assessment.currentQuestionIndex > 0) {
            this.assessment.currentQuestionIndex--;
            this.displayCurrentQuestion();
        }
    }
    
    handlePollNext() {
        const currentQuestion = this.assessment.data.questions[this.assessment.currentQuestionIndex];
        const hasAnswer = currentQuestion && this.assessment.answers[currentQuestion.id] !== undefined;
        
        if (!hasAnswer) {
            return;
        }
        
        if (this.assessment.currentQuestionIndex < this.assessment.totalQuestions - 1) {
            this.assessment.currentQuestionIndex++;
            this.displayCurrentQuestion();
        } else {
            this.completeAssessment();
        }
    }
    
    async completeAssessment() {
        try {
            // Show loading state
            this.showAssessmentLoading();
            
            // Submit assessment results
            const response = await this.submitAssessment();
            
            if (response.success) {
                // Redirect to results page
                window.location.href = '/results';
            } else {
                this.handleAssessmentError(response.error);
            }
        } catch (error) {
            console.error('Assessment completion error:', error);
            this.handleAssessmentError('Có lỗi xảy ra khi hoàn thành đánh giá.');
        }
    }
    
    async submitAssessment() {
        try {
            const response = await fetch('/api/assessment/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.conversation.state.session_id,
                    assessment_type: this.conversation.state.assessment_type,
                    answers: this.assessment.answers,
                    chat_history: this.conversation.history,
                    state: this.conversation.state
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                return { success: false, error: data.message || data.error };
            }
            
            // Store results for the results page
            if (data.results) {
                localStorage.setItem('assessmentResults', JSON.stringify(data.results));
            }
            
            return { success: true, data: data };
            
        } catch (error) {
            return { success: false, error: 'Không thể gửi kết quả đánh giá.' };
        }
    }
    
    showAssessmentLoading() {
        if (this.pollContainer) {
            this.pollContainer.innerHTML = `
                <div class="assessment-loading">
                    <div class="loading-spinner"></div>
                    <p>Đang xử lý kết quả đánh giá...</p>
                </div>
            `;
        }
    }
    
    handleAssessmentError(error) {
        if (this.pollContainer) {
            this.pollContainer.innerHTML = `
                <div class="assessment-error">
                    <p class="error-message">${error}</p>
                    <button onclick="location.reload()" class="retry-button">Thử lại</button>
                </div>
            `;
        }
    }
    
    showTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.classList.add('show');
            this.scrollToBottom();
        }
    }
    
    hideTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.classList.remove('show');
        }
    }
    
    updateSendButton() {
        if (this.sendButton && this.userInput) {
            const hasText = this.userInput.value.trim().length > 0;
            this.sendButton.disabled = !hasText || this.conversation.isLoading;
        }
    }
    
    autoResizeInput() {
        if (this.userInput) {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = Math.min(this.userInput.scrollHeight, 120) + 'px';
        }
    }
    
    updateUI() {
        this.updateSendButton();
        
        // Update mode indicator
        if (this.chatModeIndicator) {
            if (this.conversation.currentPhase === 'chat') {
                this.chatModeIndicator.textContent = 'Chế độ AI';
                this.chatModeIndicator.classList.remove('assessment-mode');
            }
        }
    }
    
    scrollToBottom() {
        if (this.messagesContainer) {
            setTimeout(() => {
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            }, 100);
        }
    }
    
    formatTime(date) {
        if (!date) return '';
        
        const now = new Date();
        const messageDate = new Date(date);
        
        if (now.toDateString() === messageDate.toDateString()) {
            // Same day - show time only
            return messageDate.toLocaleTimeString('vi-VN', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        } else {
            // Different day - show date and time
            return messageDate.toLocaleString('vi-VN', { 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit', 
                minute: '2-digit' 
            });
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Public methods
    resetChat() {
        this.conversation = {
            history: [],
            state: this.initializeState(),
            currentPhase: 'chat',
            isLoading: false
        };
        
        this.assessment = {
            data: null,
            currentQuestionIndex: 0,
            answers: {},
            totalQuestions: 0
        };
        
        // Clear UI
        if (this.messagesContainer) {
            this.messagesContainer.innerHTML = '';
        }
        
        this.hidePollInterface();
        this.showWelcomeMessage();
        this.updateUI();
        
        if (this.userInput) {
            this.userInput.focus();
        }
    }
    
    // Get current conversation data
    getConversationData() {
        return {
            history: this.conversation.history,
            state: this.conversation.state,
            assessment: this.assessment
        };
    }
}

// Initialize chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chatInterface = new ChatInterface();
    
    // Add global reset function
    window.resetChat = function() {
        if (window.chatInterface) {
            window.chatInterface.resetChat();
        }
    };
    
    // Handle page visibility for better UX
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden && window.chatInterface && window.chatInterface.userInput) {
            window.chatInterface.userInput.focus();
        }
    });
    
    console.log('Chat interface initialized successfully');
});