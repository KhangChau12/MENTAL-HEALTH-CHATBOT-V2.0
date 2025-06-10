/**
 * Admin.js - Admin dashboard functionality
 * Handles statistics, system monitoring, and data export
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize admin dashboard
    initializeDashboard();
    loadStatistics();
    setupRealTimeUpdates();
    
    // Refresh data every 30 seconds
    setInterval(loadStatistics, 30000);
});

function initializeDashboard() {
    console.log('Admin Dashboard initialized');
    
    // Check admin authentication
    checkAdminAuth();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load initial data
    loadSystemHealth();
    loadRecentSessions();
}

function checkAdminAuth() {
    // Simple admin check - in production, this should be server-side
    const adminToken = localStorage.getItem('adminToken');
    if (!adminToken) {
        // In a real app, redirect to login
        console.log('Admin authentication required');
    }
}

function setupEventListeners() {
    // Chart interactions
    const chartBars = document.querySelectorAll('.chart-bar');
    chartBars.forEach(bar => {
        bar.addEventListener('mouseenter', function() {
            const value = this.querySelector('.chart-value').textContent;
            const label = this.querySelector('.chart-label').textContent;
            showTooltip(`${label}: ${value} đánh giá`, this);
        });
        
        bar.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
    
    // Session table interactions
    setupSessionTableEvents();
}

function loadStatistics() {
    // Simulate API call to get statistics
    fetch('/api/admin/statistics')
        .then(response => response.json())
        .then(data => {
            updateStatistics(data);
        })
        .catch(error => {
            console.error('Error loading statistics:', error);
            // Use mock data for development
            updateStatistics(getMockStatistics());
        });
}

function getMockStatistics() {
    return {
        totalSessions: 1248,
        completedAssessments: 987,
        highRiskCases: 23,
        abandonedSessions: 156,
        monthlyChange: {
            totalSessions: 12,
            completedAssessments: 8,
            highRiskCases: -5,
            abandonedSessions: -3
        },
        assessmentBreakdown: {
            phq9: 180,
            gad7: 135,
            dass21: 240,
            riskAssessment: 75
        },
        systemHealth: {
            togetherAI: 'healthy',
            database: 'healthy',
            exportService: 'warning',
            emailService: 'healthy'
        }
    };
}

function updateStatistics(data) {
    // Update main statistics
    updateElement('total-sessions', data.totalSessions);
    updateElement('completed-assessments', data.completedAssessments);
    updateElement('high-risk-cases', data.highRiskCases);
    updateElement('abandoned-sessions', data.abandonedSessions);
    
    // Update assessment chart
    updateAssessmentChart(data.assessmentBreakdown);
    
    // Update system health
    updateSystemHealth(data.systemHealth);
    
    // Animate counters
    animateCounters();
}

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = formatNumber(value);
    }
}

function formatNumber(num) {
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
}

function updateAssessmentChart(data) {
    const chartBars = document.querySelectorAll('.chart-bar');
    const maxValue = Math.max(...Object.values(data));
    
    chartBars.forEach(bar => {
        const label = bar.querySelector('.chart-label').textContent.toLowerCase();
        const value = getChartValueByLabel(label, data);
        const percentage = (value / maxValue) * 100;
        
        // Animate height change
        bar.style.height = `${Math.max(percentage, 10)}%`;
        bar.querySelector('.chart-value').textContent = value;
    });
}

function getChartValueByLabel(label, data) {
    const mapping = {
        'phq-9': data.phq9,
        'gad-7': data.gad7,
        'dass-21': data.dass21,
        'rủi ro': data.riskAssessment
    };
    return mapping[label] || 0;
}

function updateSystemHealth(healthData) {
    const healthItems = document.querySelectorAll('.health-item');
    
    healthItems.forEach(item => {
        const serviceName = item.querySelector('span').textContent.toLowerCase();
        const statusIndicator = item.querySelector('.status-indicator');
        const statusText = item.querySelector('.health-status');
        
        const status = getHealthStatusByService(serviceName, healthData);
        
        // Update indicator color
        statusIndicator.className = `status-indicator status-${status.level}`;
        
        // Update status text
        statusText.innerHTML = `
            <div class="status-indicator status-${status.level}"></div>
            ${status.text}
        `;
    });
}

function getHealthStatusByService(serviceName, healthData) {
    const statusMap = {
        'api together ai': {
            level: healthData.togetherAI,
            text: healthData.togetherAI === 'healthy' ? 'Hoạt động tốt' : 'Có vấn đề'
        },
        'database': {
            level: healthData.database,
            text: healthData.database === 'healthy' ? 'Hoạt động tốt' : 'Có vấn đề'
        },
        'export service': {
            level: healthData.exportService,
            text: healthData.exportService === 'healthy' ? 'Hoạt động tốt' : 
                  healthData.exportService === 'warning' ? 'Chậm' : 'Có vấn đề'
        },
        'email service': {
            level: healthData.emailService,
            text: healthData.emailService === 'healthy' ? 'Hoạt động tốt' : 'Có vấn đề'
        }
    };
    
    return statusMap[serviceName] || { level: 'error', text: 'Không xác định' };
}

function animateCounters() {
    const counters = document.querySelectorAll('.stat-value');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent.replace(/[^\d]/g, ''));
        const duration = 1000;
        const increment = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = formatNumber(Math.floor(current));
        }, 16);
    });
}

function loadSystemHealth() {
    fetch('/api/admin/health')
        .then(response => response.json())
        .then(data => {
            updateSystemHealth(data);
        })
        .catch(error => {
            console.error('Error loading system health:', error);
        });
}

function loadRecentSessions() {
    fetch('/api/admin/sessions/recent')
        .then(response => response.json())
        .then(data => {
            updateSessionsTable(data);
        })
        .catch(error => {
            console.error('Error loading recent sessions:', error);
            // Use mock data
            updateSessionsTable(getMockSessions());
        });
}

function getMockSessions() {
    return [
        {
            id: 'S001248',
            timestamp: '10/06/2025 14:30',
            type: 'AI Chat',
            score: '25/63',
            risk: 'Thấp',
            status: 'completed'
        },
        {
            id: 'S001247',
            timestamp: '10/06/2025 13:45',
            type: 'Logic Poll',
            score: '-',
            risk: '-',
            status: 'in-progress'
        },
        {
            id: 'S001246',
            timestamp: '10/06/2025 12:15',
            type: 'AI Chat',
            score: '42/63',
            risk: 'Cao',
            status: 'completed'
        },
        {
            id: 'S001245',
            timestamp: '10/06/2025 11:30',
            type: 'Logic Poll',
            score: '-',
            risk: '-',
            status: 'abandoned'
        },
        {
            id: 'S001244',
            timestamp: '10/06/2025 10:00',
            type: 'AI Chat',
            score: '18/63',
            risk: 'Thấp',
            status: 'completed'
        }
    ];
}

function updateSessionsTable(sessions) {
    const tbody = document.getElementById('sessions-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = sessions.map(session => `
        <tr>
            <td>#${session.id}</td>
            <td>${session.timestamp}</td>
            <td>${session.type}</td>
            <td>${session.score}</td>
            <td>${session.risk}</td>
            <td><span class="session-status status-${session.status.replace('-', '_')}">${getStatusText(session.status)}</span></td>
            <td>
                <button class="admin-button ${session.risk === 'Cao' ? 'danger' : ''}" onclick="viewSession('${session.id}')">
                    Xem
                </button>
            </td>
        </tr>
    `).join('');
}

function getStatusText(status) {
    const statusMap = {
        'completed': 'Hoàn thành',
        'in-progress': 'Đang tiến hành',
        'abandoned': 'Bỏ dở'
    };
    return statusMap[status] || status;
}

function setupSessionTableEvents() {
    // Add sorting functionality
    const headers = document.querySelectorAll('.sessions-table th');
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            sortTable(this);
        });
    });
}

function sortTable(header) {
    // Simple table sorting implementation
    const table = header.closest('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    
    const isAscending = header.classList.contains('sort-asc');
    
    // Remove existing sort classes
    header.parentNode.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Add new sort class
    header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        if (isAscending) {
            return bValue.localeCompare(aValue, undefined, { numeric: true });
        } else {
            return aValue.localeCompare(bValue, undefined, { numeric: true });
        }
    });
    
    // Reorder rows
    rows.forEach(row => tbody.appendChild(row));
}

function setupRealTimeUpdates() {
    // WebSocket connection for real-time updates (if available)
    if (typeof WebSocket !== 'undefined') {
        try {
            const ws = new WebSocket(`ws://${window.location.host}/admin/ws`);
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleRealTimeUpdate(data);
            };
            
            ws.onerror = function(error) {
                console.log('WebSocket connection failed, using polling instead');
            };
        } catch (error) {
            console.log('WebSocket not available, using polling');
        }
    }
}

function handleRealTimeUpdate(data) {
    switch (data.type) {
        case 'new_session':
            incrementStat('total-sessions');
            showNotification('Phiên mới bắt đầu', 'info');
            break;
        case 'assessment_completed':
            incrementStat('completed-assessments');
            showNotification('Đánh giá được hoàn thành', 'success');
            break;
        case 'high_risk_detected':
            incrementStat('high-risk-cases');
            showNotification('Phát hiện trường hợp rủi ro cao', 'warning');
            break;
        case 'session_abandoned':
            incrementStat('abandoned-sessions');
            break;
    }
}

function incrementStat(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const currentValue = parseInt(element.textContent.replace(/[^\d]/g, ''));
        element.textContent = formatNumber(currentValue + 1);
    }
}

// Admin action functions
function clearCache() {
    if (confirm('Bạn có chắc chắn muốn xóa cache hệ thống?')) {
        fetch('/api/admin/cache/clear', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                showNotification('Cache đã được xóa thành công', 'success');
            })
            .catch(error => {
                showNotification('Lỗi khi xóa cache', 'error');
            });
    }
}

function testApiConnection() {
    showNotification('Đang kiểm tra kết nối API...', 'info');
    
    fetch('/api/admin/test/together-ai')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Kết nối API thành công', 'success');
            } else {
                showNotification('Kết nối API thất bại', 'error');
            }
        })
        .catch(error => {
            showNotification('Lỗi khi kiểm tra API', 'error');
        });
}

function sendTestEmail() {
    const email = prompt('Nhập email để gửi test:');
    if (email) {
        fetch('/api/admin/test/email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email })
        })
        .then(response => response.json())
        .then(data => {
            showNotification('Email test đã được gửi', 'success');
        })
        .catch(error => {
            showNotification('Lỗi khi gửi email', 'error');
        });
    }
}

function backupData() {
    if (confirm('Bạn có chắc chắn muốn tạo backup dữ liệu?')) {
        showNotification('Đang tạo backup...', 'info');
        
        fetch('/api/admin/backup', { method: 'POST' })
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `backup-${new Date().toISOString().split('T')[0]}.zip`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                
                showNotification('Backup đã được tạo và tải xuống', 'success');
            })
            .catch(error => {
                showNotification('Lỗi khi tạo backup', 'error');
            });
    }
}

function exportData(type) {
    showNotification('Đang chuẩn bị xuất dữ liệu...', 'info');
    
    fetch(`/api/admin/export/${type}`, { method: 'POST' })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `${type}-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            
            showNotification('Dữ liệu đã được xuất thành công', 'success');
        })
        .catch(error => {
            showNotification('Lỗi khi xuất dữ liệu', 'error');
        });
}

function viewSession(sessionId) {
    // Open session details in modal or new tab
    window.open(`/admin/session/${sessionId}`, '_blank');
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: var(--color-${type === 'error' ? 'error' : type === 'warning' ? 'warning' : type === 'success' ? 'success' : 'primary'});
        color: white;
        border-radius: 0.5rem;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function showTooltip(text, element) {
    const tooltip = document.createElement('div');
    tooltip.className = 'admin-tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: var(--color-text);
        color: var(--color-surface);
        padding: 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        z-index: 1001;
        pointer-events: none;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.admin-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Export functions for global access
window.adminController = {
    clearCache,
    testApiConnection,
    sendTestEmail,
    backupData,
    exportData,
    viewSession,
    refreshStats: loadStatistics
};