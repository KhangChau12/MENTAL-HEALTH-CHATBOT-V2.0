/**
 * Chat.js - AI Chat Mode Implementation
 * Clean version without syntax errors
 */

class ChatInterface {
    constructor() {
        // DOM Elements
        this.chatContainer = document.getElementById('chat-container');
        this.messagesContainer = document.getElementById('chat-messages');
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
        
        // Debug mode
        this.debugMode = true;
        
        // State
        this.conversation = {
            history: [],
            state: this.initializeState(),
            currentPhase: 'chat',
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
        this.log('Initializing ChatInterface...');
        this.log('Messages container:', this.messagesContainer);
        this.log('User input:', this.userInput);
        this.log('Send button:', this.sendButton);
        
        // Check if required elements exist
        if (!this.messagesContainer) {
            console.error('Messages container not found! Looking for element with id="chat-messages"');
            return;
        }
        
        if (!this.userInput) {
            console.error('User input not found! Looking for element with id="user-input"');
            return;
        }
        
        if (!this.sendButton) {
            console.error('Send button not found! Looking for element with id="send-button"');
            return;
        }
        
        this.setupEventListeners();
        this.updateUI();
        
        // Auto-focus input
        if (this.userInput) {
            this.userInput.focus();
        }
        
        // Set welcome message time
        this.setWelcomeTime();
        
        this.log('ChatInterface initialized successfully');
    }
    
    log() {
        if (this.debugMode) {
            console.log.apply(console, ['[ChatInterface]'].concat(Array.prototype.slice.call(arguments)));
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
            var r = Math.random() * 16 | 0;
            var v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    setupEventListeners() {
        var self = this;
        self.log('Setting up event listeners...');
        
        // Chat form submission
        if (self.chatForm) {
            self.chatForm.addEventListener('submit', function(e) {
                e.preventDefault();
                self.log('Form submitted');
                self.handleSendMessage();
            });
        } else {
            self.log('Warning: Chat form not found');
        }
        
        // Send button click
        if (self.sendButton) {
            self.sendButton.addEventListener('click', function(e) {
                e.preventDefault();
                self.log('Send button clicked');
                self.handleSendMessage();
            });
        } else {
            self.log('Warning: Send button not found');
        }
        
        // Input handling
        if (self.userInput) {
            self.userInput.addEventListener('input', function() {
                self.updateSendButton();
                self.autoResizeInput();
            });
            
            self.userInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    self.log('Enter key pressed');
                    self.handleSendMessage();
                }
            });
        } else {
            self.log('Warning: User input not found');
        }
        
        // Restart chat button
        var restartButton = document.getElementById('restart-chat');
        if (restartButton) {
            restartButton.addEventListener('click', function() {
                self.log('Restart button clicked');
                self.resetChat();
            });
        }
        
        // Poll navigation
        if (self.pollPrevButton) {
            self.pollPrevButton.addEventListener('click', function() {
                self.handlePollPrevious();
            });
        }
        
        if (self.pollNextButton) {
            self.pollNextButton.addEventListener('click', function() {
                self.handlePollNext();
            });
        }
        
        self.log('Event listeners set up successfully');
    }
    
    setWelcomeTime() {
        var welcomeTimeElement = document.getElementById('welcome-time');
        if (welcomeTimeElement) {
            welcomeTimeElement.textContent = this.formatTime(new Date());
        }
    }
    
    handleSendMessage() {
        var self = this;
        
        if (!self.userInput || !self.messagesContainer) {
            self.log('Error: Required DOM elements not found');
            alert('Có lỗi xảy ra với giao diện. Vui lòng tải lại trang.');
            return;
        }
        
        var message = self.userInput.value.trim();
        
        if (!message) {
            self.log('No message to send');
            return;
        }
        
        if (self.conversation.isLoading) {
            self.log('Already loading, ignoring send request');
            return;
        }
        
        self.log('Sending message:', message);
        
        // Disable input and show loading state
        self.conversation.isLoading = true;
        self.updateSendButton();
        
        // Clear input
        self.userInput.value = '';
        self.autoResizeInput();
        
        // Add user message to UI and history
        var userMessage = {
            role: 'user',
            content: message,
            timestamp: new Date()
        };
        
        self.conversation.history.push(userMessage);
        self.addMessageToUI(userMessage);
        
        // Update state
        self.conversation.state.message_count = (self.conversation.state.message_count || 0) + 1;
        
        // Show typing indicator
        self.showTypingIndicator();
        
        // Send message to API
        self.sendMessageToAPI(message).then(function(response) {
            if (response.success) {
                self.handleAPIResponse(response.data);
            } else {
                self.handleAPIError(response.error);
            }
        }).catch(function(error) {
            self.log('Error sending message:', error);
            self.handleAPIError('Đã xảy ra lỗi khi gửi tin nhắn. Vui lòng thử lại.');
        }).finally(function() {
            self.hideTypingIndicator();
            self.conversation.isLoading = false;
            self.updateSendButton();
        });
    }
    
    sendMessageToAPI(message) {
        var self = this;
        
        return new Promise(function(resolve, reject) {
            self.log('Sending API request...');
            
            // First, try to check if API is available
            fetch('/health').then(function(healthCheck) {
                if (!healthCheck.ok) {
                    self.log('Server health check failed, using mock response');
                    resolve(self.getMockResponse(message));
                    return;
                }
                
                // Try real API
                fetch('/api/chat/send_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        history: self.conversation.history.slice(0, -1),
                        state: self.conversation.state,
                        use_ai: true
                    })
                }).then(function(response) {
                    self.log('API response status:', response.status);
                    
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                    }
                    
                    return response.json();
                }).then(function(data) {
                    self.log('API response data:', data);
                    
                    if (data.error) {
                        resolve({ success: false, error: data.message || data.error });
                    } else {
                        resolve({ success: true, data: data });
                    }
                }).catch(function(error) {
                    self.log('API request failed, using mock response:', error);
                    resolve(self.getMockResponse(message));
                });
            }).catch(function(e) {
                self.log('Server not reachable, using mock response');
                resolve(self.getMockResponse(message));
            });
        });
    }
    
    getMockResponse(message) {
        var responses = [
            "Cảm ơn bạn đã chia sẻ. Tôi hiểu bạn đang trải qua những cảm xúc khó khăn. Có thể bạn kể thêm về những gì đang làm bạn cảm thấy lo lắng?",
            "Tôi đang lắng nghe. Những triệu chứng này xuất hiện từ khi nào? Có điều gì đặc biệt xảy ra gần đây không?",
            "Cảm ơn bạn đã tin tưởng chia sẻ với tôi. Dựa trên những gì bạn đã nói, tôi nghĩ chúng ta nên thực hiện một bài đánh giá chi tiết hơn để hiểu rõ tình trạng của bạn.",
            "Tôi sẽ đưa bạn đến phần đánh giá chuyên sâu. Điều này sẽ giúp chúng ta có cái nhìn tổng quan về tình trạng sức khỏe tâm thần của bạn."
        ];
        
        var messageCount = this.conversation.state.message_count || 0;
        var responseText;
        
        if (messageCount >= 3) {
            responseText = responses[3];
            return {
                success: true,
                data: {
                    message: responseText,
                    state: {
                        session_id: this.conversation.state.session_id,
                        message_count: messageCount + 1,
                        current_phase: 'chat',
                        language: 'vi',
                        started_at: this.conversation.state.started_at,
                        last_activity: new Date().toISOString()
                    },
                    metadata: {
                        should_show_poll: true,
                        type: 'assessment_transition'
                    },
                    assessment: {
                        type: 'phq9',
                        questions: [
                            {
                                text: "Trong 2 tuần qua, bạn có thường xuyên cảm thấy buồn chán, chán nản, hoặc tuyệt vọng không?",
                                options: [
                                    { text: "Không bao giờ", value: 0 },
                                    { text: "Vài ngày", value: 1 },
                                    { text: "Hơn một nửa số ngày", value: 2 },
                                    { text: "Gần như mỗi ngày", value: 3 }
                                ]
                            },
                            {
                                text: "Trong 2 tuần qua, bạn có thường xuyên cảm thấy ít hứng thú hoặc vui vẻ khi làm việc không?",
                                options: [
                                    { text: "Không bao giờ", value: 0 },
                                    { text: "Vài ngày", value: 1 },
                                    { text: "Hơn một nửa số ngày", value: 2 },
                                    { text: "Gần như mỗi ngày", value: 3 }
                                ]
                            },
                            {
                                text: "Trong 2 tuần qua, bạn có gặp khó khăn trong việc ngủ hoặc ngủ quá nhiều không?",
                                options: [
                                    { text: "Không bao giờ", value: 0 },
                                    { text: "Vài ngày", value: 1 },
                                    { text: "Hơn một nửa số ngày", value: 2 },
                                    { text: "Gần như mỗi ngày", value: 3 }
                                ]
                            }
                        ]
                    }
                }
            };
        } else {
            responseText = responses[messageCount] || responses[0];
            return {
                success: true,
                data: {
                    message: responseText,
                    state: {
                        session_id: this.conversation.state.session_id,
                        message_count: messageCount + 1,
                        current_phase: 'chat',
                        language: 'vi',
                        started_at: this.conversation.state.started_at,
                        last_activity: new Date().toISOString()
                    },
                    metadata: {
                        type: 'chat_response'
                    }
                }
            };
        }
    }
    
    handleAPIResponse(data) {
        var self = this;
        self.log('Handling API response:', data);
        
        // Update conversation state
        if (data.state) {
            self.conversation.state = Object.assign(self.conversation.state, data.state);
        }
        
        // Add bot response to UI
        if (data.message) {
            var botMessage = {
                role: 'bot',
                content: data.message,
                timestamp: new Date()
            };
            
            self.conversation.history.push(botMessage);
            self.addMessageToUI(botMessage);
        }
        
        // Check if we should transition to poll mode
        if (data.metadata && data.metadata.should_show_poll && data.assessment) {
            setTimeout(function() {
                self.transitionToPoll(data.assessment);
            }, 1000);
        }
        
        self.updateUI();
    }
    
    handleAPIError(error) {
        var self = this;
        self.log('API Error:', error);
        
        var errorMessage = {
            role: 'bot',
            content: error || 'Xin lỗi, tôi gặp chút khó khăn. Bạn có thể thử lại không?',
            timestamp: new Date(),
            isError: true
        };
        
        self.conversation.history.push(errorMessage);
        self.addMessageToUI(errorMessage);
    }
    
    addMessageToUI(message) {
        var self = this;
        
        if (!self.messagesContainer) {
            self.log('Error: Messages container not found');
            return;
        }
        
        self.log('Adding message to UI:', message);
        
        var messageElement = document.createElement('div');
        messageElement.className = 'message ' + message.role;
        
        if (message.isError) {
            messageElement.classList.add('error');
        }
        
        var avatarEmoji = message.role === 'user' ? '👤' : '🤖';
        var escapedContent = self.escapeHtml(message.content);
        var formattedTime = self.formatTime(message.timestamp);
        
        messageElement.innerHTML = 
            '<div class="message-avatar">' + avatarEmoji + '</div>' +
            '<div class="message-content">' +
                '<p>' + escapedContent + '</p>' +
                '<div class="message-time">' + formattedTime + '</div>' +
            '</div>';
        
        self.messagesContainer.appendChild(messageElement);
        self.scrollToBottom();
        
        // Add animation
        setTimeout(function() {
            messageElement.classList.add('show');
        }, 10);
        
        self.log('Message added to UI successfully');
    }
    
    transitionToPoll(assessmentData) {
        var self = this;
        self.log('Transitioning to poll mode with data:', assessmentData);
        
        self.conversation.currentPhase = 'poll';
        self.assessment.data = assessmentData;
        self.assessment.currentQuestionIndex = 0;
        self.assessment.answers = {};
        self.assessment.totalQuestions = assessmentData.questions ? assessmentData.questions.length : 0;
        
        // Update mode indicator
        if (self.chatModeIndicator) {
            self.chatModeIndicator.textContent = 'Chế độ Đánh giá';
            self.chatModeIndicator.classList.add('assessment-mode');
        }
        
        // Show poll container and hide chat input
        self.showPollInterface();
        self.displayCurrentQuestion();
    }
    
    showPollInterface() {
        if (this.pollContainer) {
            this.pollContainer.classList.add('show');
        }
        
        // Hide chat input
        var chatInputContainer = document.querySelector('.chat-input-container');
        if (chatInputContainer) {
            chatInputContainer.style.display = 'none';
        }
    }
    
    hidePollInterface() {
        if (this.pollContainer) {
            this.pollContainer.classList.remove('show');
        }
        
        // Show chat input
        var chatInputContainer = document.querySelector('.chat-input-container');
        if (chatInputContainer) {
            chatInputContainer.style.display = 'block';
        }
    }
    
    displayCurrentQuestion() {
        var self = this;
        
        if (!self.assessment.data || !self.assessment.data.questions) {
            return;
        }
        
        var question = self.assessment.data.questions[self.assessment.currentQuestionIndex];
        
        if (!question) {
            self.completeAssessment();
            return;
        }
        
        // Update question text
        if (self.pollQuestion) {
            self.pollQuestion.textContent = question.text || question.question;
        }
        
        // Update progress
        self.updatePollProgress();
        
        // Display options
        self.displayQuestionOptions(question);
        
        // Update navigation buttons
        self.updatePollNavigation();
    }
    
    displayQuestionOptions(question) {
        var self = this;
        
        if (!self.pollOptions || !question.options) return;
        
        self.pollOptions.innerHTML = '';
        
        question.options.forEach(function(option, index) {
            var optionElement = document.createElement('div');
            optionElement.className = 'poll-option';
            optionElement.dataset.value = option.value || index;
            
            optionElement.innerHTML = '<span>' + (option.text || option) + '</span>';
            
            optionElement.addEventListener('click', function() {
                self.selectPollOption(optionElement, option.value || index);
            });
            
            self.pollOptions.appendChild(optionElement);
        });
    }
    
    selectPollOption(element, value) {
        var self = this;
        
        // Remove previous selection
        var options = self.pollOptions.querySelectorAll('.poll-option');
        for (var i = 0; i < options.length; i++) {
            options[i].classList.remove('selected');
        }
        
        // Select current option
        element.classList.add('selected');
        
        // Store answer
        var questionId = self.assessment.currentQuestionIndex;
        self.assessment.answers[questionId] = value;
        
        // Enable next button
        self.updatePollNavigation();
    }
    
    updatePollProgress() {
        var self = this;
        
        if (!self.pollProgressBar || !self.pollProgress) return;
        
        var progress = ((self.assessment.currentQuestionIndex + 1) / self.assessment.totalQuestions) * 100;
        self.pollProgressBar.style.width = progress + '%';
        self.pollProgress.textContent = (self.assessment.currentQuestionIndex + 1) + '/' + self.assessment.totalQuestions;
    }
    
    updatePollNavigation() {
        var self = this;
        
        if (self.pollPrevButton) {
            self.pollPrevButton.disabled = self.assessment.currentQuestionIndex === 0;
        }
        
        if (self.pollNextButton) {
            var hasAnswer = self.assessment.currentQuestionIndex in self.assessment.answers;
            var isLastQuestion = self.assessment.currentQuestionIndex === self.assessment.totalQuestions - 1;
            
            self.pollNextButton.disabled = !hasAnswer;
            self.pollNextButton.textContent = isLastQuestion ? 'Hoàn thành' : 'Tiếp tục →';
        }
    }
    
    handlePollPrevious() {
        if (this.assessment.currentQuestionIndex > 0) {
            this.assessment.currentQuestionIndex--;
            this.displayCurrentQuestion();
        }
    }
    
    handlePollNext() {
        var self = this;
        var hasAnswer = self.assessment.currentQuestionIndex in self.assessment.answers;
        
        if (!hasAnswer) return;
        
        if (self.assessment.currentQuestionIndex < self.assessment.totalQuestions - 1) {
            self.assessment.currentQuestionIndex++;
            self.displayCurrentQuestion();
        } else {
            self.completeAssessment();
        }
    }
    
    completeAssessment() {
        var self = this;
        self.log('Completing assessment');
        
        self.showAssessmentLoading();
        
        fetch('/api/assessment/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                answers: self.assessment.answers,
                assessment_type: self.assessment.data.type,
                state: self.conversation.state
            })
        }).then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Assessment completion failed');
            }
        }).then(function(data) {
            // Redirect to results page
            window.location.href = '/results?session_id=' + data.session_id;
        }).catch(function(error) {
            self.log('Error completing assessment:', error);
            self.handleAssessmentError('Không thể hoàn thành đánh giá. Vui lòng thử lại.');
        });
    }
    
    showAssessmentLoading() {
        if (this.pollContainer) {
            this.pollContainer.innerHTML = 
                '<div class="assessment-loading">' +
                    '<div class="loading-spinner"></div>' +
                    '<p>Đang xử lý kết quả đánh giá...</p>' +
                '</div>';
        }
    }
    
    handleAssessmentError(error) {
        if (this.pollContainer) {
            this.pollContainer.innerHTML = 
                '<div class="assessment-error">' +
                    '<p class="error-message">' + error + '</p>' +
                    '<button onclick="location.reload()" class="retry-button">Thử lại</button>' +
                '</div>';
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
            var hasText = this.userInput.value.trim().length > 0;
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
        var self = this;
        if (self.messagesContainer) {
            setTimeout(function() {
                self.messagesContainer.scrollTop = self.messagesContainer.scrollHeight;
            }, 100);
        }
    }
    
    formatTime(date) {
        if (!date) return '';
        
        var now = new Date();
        var messageDate = new Date(date);
        
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
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    resetChat() {
        var self = this;
        self.log('Resetting chat');
        
        self.conversation = {
            history: [],
            state: self.initializeState(),
            currentPhase: 'chat',
            isLoading: false
        };
        
        self.assessment = {
            data: null,
            currentQuestionIndex: 0,
            answers: {},
            totalQuestions: 0
        };
        
        // Clear UI - keep welcome message
        if (self.messagesContainer) {
            var welcomeMessage = self.messagesContainer.querySelector('.message.bot');
            self.messagesContainer.innerHTML = '';
            if (welcomeMessage) {
                self.messagesContainer.appendChild(welcomeMessage);
            }
        }
        
        self.hidePollInterface();
        self.setWelcomeTime();
        self.updateUI();
        
        if (self.userInput) {
            self.userInput.value = '';
            self.userInput.focus();
        }
    }
    
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
    console.log('DOM loaded, initializing chat interface');
    
    // Add a small delay to ensure all styles are loaded
    setTimeout(function() {
        window.chatInterface = new ChatInterface();
        
        // Add global reset function
        window.resetChat = function() {
            if (window.chatInterface) {
                window.chatInterface.resetChat();
            }
        };
        
        // Add debug function
        window.debugChat = function() {
            if (window.chatInterface) {
                console.log('Chat Debug Info:');
                console.log('- Messages Container:', window.chatInterface.messagesContainer);
                console.log('- User Input:', window.chatInterface.userInput);
                console.log('- Send Button:', window.chatInterface.sendButton);
                console.log('- Conversation:', window.chatInterface.conversation);
                console.log('- Assessment:', window.chatInterface.assessment);
            }
        };
        
        // Handle page visibility for better UX
        document.addEventListener('visibilitychange', function() {
            if (!document.hidden && window.chatInterface && window.chatInterface.userInput) {
                window.chatInterface.userInput.focus();
            }
        });
        
        console.log('Chat interface initialized successfully');
        console.log('Use debugChat() in console for debugging info');
    }, 100);
});