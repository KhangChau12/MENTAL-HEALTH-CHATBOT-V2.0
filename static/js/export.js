/**
 * Export.js - Handle data export functionality
 * Supports PDF and JSON export of assessment results
 */

class ExportController {
    constructor() {
        this.currentResults = null;
        this.init();
    }
    
    init() {
        this.loadResults();
        this.setupEventListeners();
    }
    
    loadResults() {
        // Load results from localStorage
        const resultsData = localStorage.getItem('assessmentResults');
        if (resultsData) {
            try {
                this.currentResults = JSON.parse(resultsData);
            } catch (error) {
                console.error('Error parsing results data:', error);
            }
        }
    }
    
    setupEventListeners() {
        // Listen for export button clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-export-pdf]')) {
                this.exportPDF();
            } else if (e.target.matches('[data-export-json]')) {
                this.exportJSON();
            } else if (e.target.matches('[onclick*="exportResults"]')) {
                const format = e.target.getAttribute('onclick').match(/exportResults\('(\w+)'\)/)?.[1];
                if (format) {
                    this.exportResults(format);
                }
            }
        });
    }
    
    exportResults(format) {
        switch (format) {
            case 'pdf':
                this.exportPDF();
                break;
            case 'json':
                this.exportJSON();
                break;
            default:
                console.error('Unknown export format:', format);
        }
    }
    
    async exportPDF() {
        if (!this.currentResults) {
            this.showError('Không có dữ liệu kết quả để xuất');
            return;
        }
        
        try {
            this.showLoading('Đang tạo file PDF...');
            
            // Option 1: Use server-side PDF generation
            if (this.hasServerSupport()) {
                await this.exportPDFServer();
            } else {
                // Option 2: Use client-side PDF generation
                await this.exportPDFClient();
            }
            
            this.hideLoading();
            this.showSuccess('File PDF đã được tạo thành công');
            
        } catch (error) {
            this.hideLoading();
            this.showError('Lỗi khi tạo file PDF: ' + error.message);
        }
    }
    
    async exportPDFServer() {
        const response = await fetch('/api/export/pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(this.currentResults)
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const blob = await response.blob();
        this.downloadFile(blob, this.generatePDFFilename(), 'application/pdf');
    }
    
    async exportPDFClient() {
        // Client-side PDF generation using jsPDF (would need to be included)
        // This is a fallback when server-side generation is not available
        
        const pdfContent = this.generatePDFContent();
        const blob = new Blob([pdfContent], { type: 'application/pdf' });
        this.downloadFile(blob, this.generatePDFFilename(), 'application/pdf');
    }
    
    exportJSON() {
        if (!this.currentResults) {
            this.showError('Không có dữ liệu kết quả để xuất');
            return;
        }
        
        try {
            const jsonData = this.prepareJSONData();
            const jsonString = JSON.stringify(jsonData, null, 2);
            const blob = new Blob([jsonString], { type: 'application/json' });
            
            this.downloadFile(blob, this.generateJSONFilename(), 'application/json');
            this.showSuccess('File JSON đã được tạo thành công');
            
        } catch (error) {
            this.showError('Lỗi khi tạo file JSON: ' + error.message);
        }
    }
    
    prepareJSONData() {
        return {
            exportInfo: {
                timestamp: new Date().toISOString(),
                version: '2.0.0',
                format: 'Mental Health Assessment Results'
            },
            assessmentResults: this.currentResults,
            summary: this.generateResultsSummary(),
            recommendations: this.generateRecommendations()
        };
    }
    
    generateResultsSummary() {
        if (!this.currentResults?.scores) return null;
        
        const summary = {
            totalScore: 0,
            assessmentTypes: [],
            overallSeverity: 'unknown',
            riskLevel: 'unknown'
        };
        
        Object.entries(this.currentResults.scores).forEach(([type, data]) => {
            summary.totalScore += data.score || 0;
            summary.assessmentTypes.push({
                type: type,
                score: data.score,
                maxScore: data.maxScore,
                severity: data.severity?.label || 'unknown'
            });
        });
        
        // Determine overall severity
        summary.overallSeverity = this.determineOverallSeverity(summary.assessmentTypes);
        summary.riskLevel = this.determineRiskLevel(summary.totalScore);
        
        return summary;
    }
    
    determineOverallSeverity(assessmentTypes) {
        const severityLevels = ['minimal', 'mild', 'moderate', 'moderately_severe', 'severe'];
        let highestSeverity = 'minimal';
        
        assessmentTypes.forEach(assessment => {
            const currentLevel = assessment.severity?.toLowerCase() || 'minimal';
            if (severityLevels.indexOf(currentLevel) > severityLevels.indexOf(highestSeverity)) {
                highestSeverity = currentLevel;
            }
        });
        
        return highestSeverity;
    }
    
    determineRiskLevel(totalScore) {
        if (totalScore >= 40) return 'high';
        if (totalScore >= 25) return 'moderate';
        if (totalScore >= 10) return 'low';
        return 'minimal';
    }
    
    generateRecommendations() {
        const summary = this.generateResultsSummary();
        const recommendations = [];
        
        // Base recommendations
        recommendations.push({
            category: 'general',
            title: 'Tự chăm sóc',
            description: 'Thực hành các kỹ thuật thư giãn như thiền, yoga, hoặc hít thở sâu',
            priority: 'medium'
        });
        
        // Severity-based recommendations
        switch (summary.overallSeverity) {
            case 'severe':
            case 'moderately_severe':
                recommendations.push({
                    category: 'professional',
                    title: 'Tìm kiếm hỗ trợ chuyên nghiệp',
                    description: 'Nên liên hệ với chuyên gia sức khỏe tâm thần trong thời gian sớm nhất',
                    priority: 'high'
                });
                break;
                
            case 'moderate':
                recommendations.push({
                    category: 'support',
                    title: 'Tăng cường hỗ trợ xã hội',
                    description: 'Chia sẻ với bạn bè, gia đình hoặc tham gia nhóm hỗ trợ',
                    priority: 'medium'
                });
                break;
                
            case 'mild':
                recommendations.push({
                    category: 'lifestyle',
                    title: 'Cải thiện lối sống',
                    description: 'Tập thể dục đều đặn, ăn uống lành mạnh và ngủ đủ giấc',
                    priority: 'medium'
                });
                break;
        }
        
        // Risk-based recommendations
        if (summary.riskLevel === 'high') {
            recommendations.unshift({
                category: 'emergency',
                title: 'Liên hệ khẩn cấp',
                description: 'Nếu có ý nghĩ tự hại, hãy liên hệ đường dây nóng 1800-1060',
                priority: 'critical'
            });
        }
        
        return recommendations;
    }
    
    generatePDFContent() {
        // Simple text-based PDF content as fallback
        return `
BÁOCÁO KẾT QUẢ ĐÁNH GIÁ SỨC KHỎE TÂM THẦN

Ngày tạo: ${new Date().toLocaleDateString('vi-VN')}
Thời gian: ${new Date().toLocaleTimeString('vi-VN')}

${this.formatResultsForPDF()}

---
Lưu ý: Kết quả này chỉ mang tính chất tham khảo và không thay thế cho tư vấn y tế chuyên nghiệp.
        `.trim();
    }
    
    formatResultsForPDF() {
        if (!this.currentResults?.scores) return 'Không có dữ liệu kết quả';
        
        let content = 'KẾT QUẢ ĐÁNH GIÁ:\n\n';
        
        Object.entries(this.currentResults.scores).forEach(([type, data]) => {
            const typeName = this.getAssessmentTypeName(type);
            content += `${typeName}:\n`;
            content += `  Điểm số: ${data.score}/${data.maxScore}\n`;
            content += `  Mức độ: ${data.severity?.label || 'Không xác định'}\n\n`;
        });
        
        return content;
    }
    
    getAssessmentTypeName(type) {
        const typeNames = {
            'initial_screening': 'Sàng lọc ban đầu',
            'phq9': 'Đánh giá trầm cảm (PHQ-9)',
            'gad7': 'Đánh giá lo âu (GAD-7)',
            'dass21': 'Đánh giá căng thẳng (DASS-21)',
            'suicide_risk': 'Đánh giá rủi ro tự tử'
        };
        return typeNames[type] || type;
    }
    
    downloadFile(blob, filename, mimeType) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        a.type = mimeType;
        
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 100);
    }
    
    generatePDFFilename() {
        const timestamp = new Date().toISOString().split('T')[0];
        return `ket-qua-danh-gia-suc-khoe-tam-than-${timestamp}.pdf`;
    }
    
    generateJSONFilename() {
        const timestamp = new Date().toISOString().split('T')[0];
        return `assessment-results-${timestamp}.json`;
    }
    
    hasServerSupport() {
        // Check if server-side PDF generation is available
        return true; // Assume available by default
    }
    
    showLoading(message) {
        this.hideNotifications();
        const loading = document.createElement('div');
        loading.id = 'export-loading';
        loading.className = 'export-notification export-loading';
        loading.innerHTML = `
            <div class="loading-spinner"></div>
            <span>${message}</span>
        `;
        loading.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: var(--color-primary);
            color: white;
            border-radius: 0.5rem;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            animation: slideIn 0.3s ease;
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            .loading-spinner {
                width: 16px;
                height: 16px;
                border: 2px solid rgba(255,255,255,0.3);
                border-top: 2px solid white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
        `;
        document.head.appendChild(style);
        document.body.appendChild(loading);
    }
    
    hideLoading() {
        const loading = document.getElementById('export-loading');
        if (loading) {
            loading.remove();
        }
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type) {
        this.hideNotifications();
        
        const notification = document.createElement('div');
        notification.className = 'export-notification';
        notification.textContent = message;
        
        const colors = {
            success: { bg: 'var(--color-success)', text: 'white' },
            error: { bg: 'var(--color-error)', text: 'white' },
            info: { bg: 'var(--color-primary)', text: 'white' }
        };
        
        const color = colors[type] || colors.info;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${color.bg};
            color: ${color.text};
            border-radius: 0.5rem;
            z-index: 1000;
            animation: slideIn 0.3s ease;
            max-width: 300px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    hideNotifications() {
        const notifications = document.querySelectorAll('.export-notification');
        notifications.forEach(notification => notification.remove());
    }
    
    // Public API methods
    setResults(results) {
        this.currentResults = results;
    }
    
    getResults() {
        return this.currentResults;
    }
    
    async exportWithOptions(format, options = {}) {
        // Advanced export with custom options
        if (format === 'pdf') {
            await this.exportPDF();
        } else if (format === 'json') {
            this.exportJSON();
        } else {
            throw new Error(`Unsupported export format: ${format}`);
        }
    }
}

// Initialize export controller when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.exportController = new ExportController();
});

// Global export functions for backward compatibility
window.exportResults = function(format) {
    if (window.exportController) {
        window.exportController.exportResults(format);
    } else {
        console.error('Export controller not initialized');
    }
};

window.exportPDF = function() {
    if (window.exportController) {
        window.exportController.exportPDF();
    }
};

window.exportJSON = function() {
    if (window.exportController) {
        window.exportController.exportJSON();
    }
};

// Export the class for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExportController;
}