/**
 * Results.js - Results display and export functionality
 * Handles visualization of assessment results and export options
 */

class ResultsInterface {
    constructor() {
        // DOM Elements
        this.resultsContainer = document.getElementById('results-container');
        this.loadingState = document.getElementById('loading-state');
        this.errorState = document.getElementById('error-state');
        this.exportButtons = document.querySelectorAll('.export-button');
        this.shareButton = document.getElementById('share-button');
        this.newAssessmentButton = document.getElementById('new-assessment-button');
        this.printButton = document.getElementById('print-button');
        
        // Results data
        this.results = null;
        this.charts = {};
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadResults();
    }
    
    setupEventListeners() {
        // Export buttons
        this.exportButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const format = e.target.dataset.format;
                this.handleExport(format);
            });
        });
        
        // Share button
        if (this.shareButton) {
            this.shareButton.addEventListener('click', () => this.handleShare());
        }
        
        // New assessment button
        if (this.newAssessmentButton) {
            this.newAssessmentButton.addEventListener('click', () => {
                this.handleNewAssessment();
            });
        }
        
        // Print button
        if (this.printButton) {
            this.printButton.addEventListener('click', () => this.handlePrint());
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'p':
                        e.preventDefault();
                        this.handlePrint();
                        break;
                    case 's':
                        e.preventDefault();
                        this.handleExport('json');
                        break;
                }
            }
        });
    }
    
    loadResults() {
        this.showLoading();
        
        try {
            // Try to load from localStorage first
            const storedResults = localStorage.getItem('assessmentResults');
            
            if (storedResults) {
                this.results = JSON.parse(storedResults);
                this.displayResults();
                return;
            }
            
            // If no stored results, try to fetch from URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const sessionId = urlParams.get('session');
            
            if (sessionId) {
                this.fetchResultsFromAPI(sessionId);
            } else {
                this.showError('Không tìm thấy kết quả đánh giá. Vui lòng thực hiện đánh giá trước.');
            }
            
        } catch (error) {
            console.error('Error loading results:', error);
            this.showError('Có lỗi khi tải kết quả. Vui lòng thử lại.');
        }
    }
    
    async fetchResultsFromAPI(sessionId) {
        try {
            const response = await fetch(`/api/assessment/results/${sessionId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.results) {
                this.results = data.results;
                this.displayResults();
            } else {
                this.showError(data.message || 'Không thể tải kết quả.');
            }
            
        } catch (error) {
            console.error('API fetch error:', error);
            this.showError('Không thể kết nối đến server. Vui lòng thử lại.');
        }
    }
    
    displayResults() {
        this.hideLoading();
        this.hideError();
        
        if (!this.results) {
            this.showError('Không có dữ liệu kết quả để hiển thị.');
            return;
        }
        
        // Update page title
        document.title = `Kết quả ${this.results.assessment_title} - Trợ lý Sức khỏe Tâm thần`;
        
        // Build results display
        this.buildResultsDisplay();
        
        // Initialize charts
        this.initializeCharts();
        
        // Show results container
        if (this.resultsContainer) {
            this.resultsContainer.style.display = 'block';
        }
    }
    
    buildResultsDisplay() {
        if (!this.resultsContainer) return;
        
        const resultsHTML = `
            <div class="results-content">
                ${this.buildHeaderSection()}
                ${this.buildScoreSection()}
                ${this.buildCategorySection()}
                ${this.buildRecommendationsSection()}
                ${this.buildActionsSection()}
            </div>
        `;
        
        this.resultsContainer.innerHTML = resultsHTML;
        
        // Re-attach event listeners for new elements
        this.reattachEventListeners();
    }
    
    buildHeaderSection() {
        const results = this.results;
        const completedDate = this.formatDate(results.completed_at);
        
        return `
            <div class="results-header">
                <div class="results-header-content">
                    <h1 class="results-title">Kết quả Đánh giá</h1>
                    <h2 class="assessment-title">${results.assessment_title || 'Đánh giá Sức khỏe Tâm thần'}</h2>
                    <div class="assessment-meta">
                        <span class="completion-date">Hoàn thành: ${completedDate}</span>
                        <span class="session-id">Mã phiên: ${results.session_id || 'N/A'}</span>
                    </div>
                </div>
                <div class="results-header-actions">
                    <button class="btn btn-secondary" onclick="window.print()">
                        📄 In kết quả
                    </button>
                    <button class="btn btn-primary" onclick="window.location.href='/'">
                        🏠 Về trang chủ
                    </button>
                </div>
            </div>
        `;
    }
    
    buildScoreSection() {
        const results = this.results;
        const severity = results.severity || {};
        const percentage = results.percentage || 0;
        
        return `
            <div class="score-section">
                <div class="score-card">
                    <div class="score-visual">
                        <div class="score-circle" style="--percentage: ${percentage}; --color: ${severity.color || '#6b7280'}">
                            <div class="score-content">
                                <div class="score-number">${results.total_score || 0}</div>
                                <div class="score-max">/ ${results.max_score || 0}</div>
                            </div>
                        </div>
                    </div>
                    <div class="score-details">
                        <h3 class="score-title">Điểm số tổng</h3>
                        <div class="score-percentage">${percentage}%</div>
                        <div class="severity-level" style="color: ${severity.color || '#6b7280'}">
                            ${severity.label || 'Không xác định'}
                        </div>
                        <div class="score-interpretation">
                            ${this.generateInterpretation()}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    buildCategorySection() {
        const categoryScores = this.results.category_scores || {};
        
        if (Object.keys(categoryScores).length === 0) {
            return '';
        }
        
        const categoryRows = Object.entries(categoryScores)
            .filter(([key]) => !key.startsWith('_'))
            .map(([category, data]) => {
                const score = typeof data === 'object' ? data.score : data;
                const count = typeof data === 'object' ? data.count : 1;
                const avgScore = count > 0 ? (score / count) : 0;
                const percentage = Math.min(avgScore * 25, 100); // Rough conversion
                
                return `
                    <div class="category-row">
                        <div class="category-info">
                            <span class="category-name">${this.getCategoryDisplayName(category)}</span>
                            <span class="category-score">${score.toFixed(1)}</span>
                        </div>
                        <div class="category-bar">
                            <div class="category-progress" style="width: ${percentage}%"></div>
                        </div>
                        <span class="category-percentage">${percentage.toFixed(0)}%</span>
                    </div>
                `;
            }).join('');
        
        return `
            <div class="category-section">
                <h3 class="section-title">Phân tích theo danh mục</h3>
                <div class="category-breakdown">
                    ${categoryRows}
                </div>
            </div>
        `;
    }
    
    buildRecommendationsSection() {
        const recommendations = this.results.recommendations || [];
        
        if (recommendations.length === 0) {
            return '';
        }
        
        const recommendationItems = recommendations.map((rec, index) => {
            const typeIcons = {
                'urgent': '🚨',
                'professional': '👨‍⚕️',
                'lifestyle': '💡',
                'technique': '🧘',
                'general': '📋'
            };
            
            const icon = typeIcons[rec.type] || '📋';
            
            return `
                <div class="recommendation-item ${rec.type}">
                    <div class="recommendation-header">
                        <span class="recommendation-icon">${icon}</span>
                        <h4 class="recommendation-title">${rec.title}</h4>
                    </div>
                    <p class="recommendation-content">${rec.content}</p>
                </div>
            `;
        }).join('');
        
        return `
            <div class="recommendations-section">
                <h3 class="section-title">Khuyến nghị và hướng dẫn</h3>
                <div class="recommendations-list">
                    ${recommendationItems}
                </div>
            </div>
        `;
    }
    
    buildActionsSection() {
        return `
            <div class="actions-section">
                <h3 class="section-title">Xuất kết quả</h3>
                <div class="export-options">
                    <button class="export-button" data-format="pdf">
                        📄 Xuất PDF
                    </button>
                    <button class="export-button" data-format="json">
                        💾 Xuất JSON
                    </button>
                </div>
                
                <div class="next-steps">
                    <h4>Bước tiếp theo</h4>
                    <div class="next-steps-grid">
                        <button class="step-button" onclick="window.location.href='/assessment'">
                            📝 Đánh giá khác
                        </button>
                        <button class="step-button" onclick="window.location.href='/chat'">
                            💬 Trò chuyện với AI
                        </button>
                        <button class="step-button" onclick="this.findProfessionalHelp()">
                            🏥 Tìm chuyên gia
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    reattachEventListeners() {
        // Re-attach export button listeners
        const exportButtons = document.querySelectorAll('.export-button');
        exportButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const format = e.target.dataset.format;
                this.handleExport(format);
            });
        });
    }
    
    generateInterpretation() {
        const results = this.results;
        const assessmentType = results.assessment_type;
        const severity = results.severity?.level || 'unknown';
        const score = results.total_score || 0;
        const maxScore = results.max_score || 1;
        
        const interpretations = {
            'phq9': {
                'minimal': 'Kết quả cho thấy ít dấu hiệu trầm cảm. Tình trạng sức khỏe tâm thần hiện tại khá tốt.',
                'mild': 'Có một số dấu hiệu trầm cảm nhẹ. Nên chú ý chăm sóc bản thân và theo dõi tâm trạng.',
                'moderate': 'Có các dấu hiệu trầm cảm ở mức trung bình. Khuyến nghị tham khảo ý kiến chuyên gia.',
                'moderately_severe': 'Có các dấu hiệu trầm cảm khá nghiêm trọng. Nên tìm kiếm sự hỗ trợ chuyên nghiệp.',
                'severe': 'Có các dấu hiệu trầm cảm nghiêm trọng. Cần hỗ trợ chuyên nghiệp ngay lập tức.'
            },
            'gad7': {
                'minimal': 'Mức độ lo âu trong giới hạn bình thường. Tình trạng hiện tại khá ổn định.',
                'mild': 'Có một số dấu hiệu lo âu nhẹ. Có thể áp dụng các kỹ thuật thư giãn.',
                'moderate': 'Mức độ lo âu ở mức trung bình. Nên học cách quản lý căng thẳng hiệu quả.',
                'severe': 'Mức độ lo âu nghiêm trọng. Khuyến nghị tìm kiếm sự hỗ trợ chuyên nghiệp.'
            }
        };
        
        const typeInterpretations = interpretations[assessmentType];
        if (typeInterpretations && typeInterpretations[severity]) {
            return typeInterpretations[severity];
        }
        
        // Generic interpretation
        const percentage = (score / maxScore) * 100;
        if (percentage <= 25) {
            return 'Kết quả cho thấy tình trạng tốt với ít dấu hiệu đáng lo ngại.';
        } else if (percentage <= 50) {
            return 'Có một số dấu hiệu cần chú ý và theo dõi.';
        } else if (percentage <= 75) {
            return 'Có các dấu hiệu đáng quan ngại, nên tìm kiếm hỗ trợ.';
        } else {
            return 'Tình trạng nghiêm trọng, cần hỗ trợ chuyên nghiệp ngay lập tức.';
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
            'worry_control': 'Kiểm soát lo lắng',
            'excessive_worry': 'Lo lắng quá mức',
            'relaxation': 'Thư giãn',
            'restlessness': 'Bồn chồn',
            'irritability': 'Cáu kỉnh',
            'fear': 'Sợ hãi',
            'tension': 'Căng thẳng',
            'stress': 'Căng thẳng'
        };
        
        return categoryNames[category] || category;
    }
    
    initializeCharts() {
        // Initialize score circle animation
        this.animateScoreCircle();
        
        // Initialize category progress bars
        this.animateCategoryBars();
    }
    
    animateScoreCircle() {
        const scoreCircle = document.querySelector('.score-circle');
        if (!scoreCircle) return;
        
        const percentage = this.results.percentage || 0;
        
        // Animate the circle
        setTimeout(() => {
            scoreCircle.style.setProperty('--percentage', percentage);
        }, 500);
    }
    
    animateCategoryBars() {
        const categoryBars = document.querySelectorAll('.category-progress');
        
        categoryBars.forEach((bar, index) => {
            setTimeout(() => {
                bar.style.transition = 'width 0.8s ease-in-out';
                bar.style.width = bar.style.width; // Trigger the animation
            }, 200 * (index + 1));
        });
    }
    
    async handleExport(format) {
        if (!this.results) {
            this.showNotification('Không có dữ liệu để xuất.', 'error');
            return;
        }
        
        try {
            this.showExportLoading(format);
            
            // Call export API
            const response = await fetch('/api/export/assessment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    assessment_data: this.results,
                    format: format,
                    include_chat_history: true
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.downloadFile(result);
                this.showNotification(`Xuất ${format.toUpperCase()} thành công!`, 'success');
            } else {
                throw new Error(result.message || 'Export failed');
            }
            
        } catch (error) {
            console.error('Export error:', error);
            this.showNotification('Có lỗi khi xuất file. Vui lòng thử lại.', 'error');
        } finally {
            this.hideExportLoading(format);
        }
    }
    
    downloadFile(exportResult) {
        const { data, filename, mime_type, format } = exportResult;
        
        let blob;
        if (format === 'pdf') {
            // Decode base64 for PDF
            const binaryString = atob(data);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            blob = new Blob([bytes], { type: mime_type });
        } else {
            // JSON or other text formats
            blob = new Blob([data], { type: mime_type });
        }
        
        // Create download link
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.style.display = 'none';
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // Cleanup
        setTimeout(() => URL.revokeObjectURL(url), 100);
    }
    
    handleShare() {
        if (navigator.share) {
            // Use native sharing if available
            navigator.share({
                title: 'Kết quả Đánh giá Sức khỏe Tâm thần',
                text: 'Tôi vừa hoàn thành đánh giá sức khỏe tâm thần trên ứng dụng.',
                url: window.location.href
            }).catch(console.error);
        } else {
            // Fallback: copy link to clipboard
            navigator.clipboard.writeText(window.location.href).then(() => {
                this.showNotification('Đã sao chép liên kết!', 'success');
            }).catch(() => {
                this.showNotification('Không thể sao chép liên kết.', 'error');
            });
        }
    }
    
    handleNewAssessment() {
        // Clear stored results
        localStorage.removeItem('assessmentResults');
        
        // Clear assessment-specific data
        const assessmentType = this.results?.assessment_type;
        if (assessmentType) {
            localStorage.removeItem(`assessment_${assessmentType}_answers`);
            localStorage.removeItem(`assessment_${assessmentType}_results`);
        }
        
        // Redirect to home
        window.location.href = '/';
    }
    
    handlePrint() {
        // Add print-friendly styles
        const printStyles = `
            <style media="print">
                .results-header-actions, .export-options, .next-steps { display: none !important; }
                .results-content { max-width: none !important; }
                .score-circle { break-inside: avoid; }
                .recommendation-item { break-inside: avoid; margin-bottom: 10px; }
                @page { margin: 1in; }
            </style>
        `;
        
        const head = document.head || document.getElementsByTagName('head')[0];
        const printStyleElement = document.createElement('style');
        printStyleElement.innerHTML = printStyles;
        head.appendChild(printStyleElement);
        
        // Print
        window.print();
        
        // Remove print styles after printing
        setTimeout(() => {
            head.removeChild(printStyleElement);
        }, 1000);
    }
    
    findProfessionalHelp() {
        const helpInfo = `
            <div class="help-info-modal">
                <div class="help-info-content">
                    <h3>Tìm chuyên gia hỗ trợ</h3>
                    <div class="help-contacts">
                        <div class="help-item">
                            <strong>Đường dây nóng sức khỏe tâm thần:</strong>
                            <span>1900-6048</span>
                        </div>
                        <div class="help-item">
                            <strong>Đường dây nóng phòng chống tự tử:</strong>
                            <span>1800-0011</span>
                        </div>
                        <div class="help-item">
                            <strong>Cấp cứu:</strong>
                            <span>113</span>
                        </div>
                        <div class="help-item">
                            <strong>Website hỗ trợ:</strong>
                            <span>https://mentalhealth.gov.vn</span>
                        </div>
                    </div>
                    <button onclick="this.closest('.help-info-modal').remove()" class="close-help-btn">
                        Đóng
                    </button>
                </div>
            </div>
        `;
        
        const modalElement = document.createElement('div');
        modalElement.innerHTML = helpInfo;
        document.body.appendChild(modalElement);
    }
    
    showExportLoading(format) {
        const button = document.querySelector(`[data-format="${format}"]`);
        if (button) {
            button.disabled = true;
            button.innerHTML = `⏳ Đang xuất ${format.toUpperCase()}...`;
        }
    }
    
    hideExportLoading(format) {
        const button = document.querySelector(`[data-format="${format}"]`);
        if (button) {
            button.disabled = false;
            const formatNames = { pdf: '📄 Xuất PDF', json: '💾 Xuất JSON' };
            button.innerHTML = formatNames[format] || `Xuất ${format.toUpperCase()}`;
        }
    }
    
    showLoading() {
        if (this.loadingState) {
            this.loadingState.style.display = 'flex';
        }
        this.hideError();
        this.hideResults();
    }
    
    hideLoading() {
        if (this.loadingState) {
            this.loadingState.style.display = 'none';
        }
    }
    
    showError(message) {
        if (this.errorState) {
            this.errorState.style.display = 'flex';
            const errorMessage = this.errorState.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.textContent = message;
            }
        }
        this.hideLoading();
        this.hideResults();
    }
    
    hideError() {
        if (this.errorState) {
            this.errorState.style.display = 'none';
        }
    }
    
    hideResults() {
        if (this.resultsContainer) {
            this.resultsContainer.style.display = 'none';
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
        
        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
    }
    
    formatDate(dateString) {
        if (!dateString) return 'Không có thông tin';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleString('vi-VN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            return dateString;
        }
    }
    
    // Public methods
    getResults() {
        return this.results;
    }
    
    refreshResults() {
        this.loadResults();
    }
    
    exportResults(format) {
        return this.handleExport(format);
    }
}

// Initialize results interface when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.resultsInterface = new ResultsInterface();
    
    // Add global functions
    window.exportResults = function(format) {
        if (window.resultsInterface) {
            return window.resultsInterface.exportResults(format);
        }
    };
    
    window.findProfessionalHelp = function() {
        if (window.resultsInterface) {
            return window.resultsInterface.findProfessionalHelp();
        }
    };
    
    // Handle browser back button
    window.addEventListener('popstate', function(event) {
        // If user navigates back, clear results and go to home
        if (window.location.pathname === '/results') {
            window.location.href = '/';
        }
    });
    
    console.log('Results interface initialized successfully');
});