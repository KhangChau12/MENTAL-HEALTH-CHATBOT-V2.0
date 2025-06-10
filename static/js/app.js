/**
 * Mental Health Chatbot - Main Application JavaScript
 * Handles core functionality, navigation, and global interactions
 */

class MentalHealthApp {
    constructor() {
        this.isLoading = false;
        this.currentLanguage = 'vi';
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.loadUserPreferences();
        console.log('Mental Health Chatbot initialized');
    }

    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Mobile menu toggle
        const mobileMenuToggle = document.querySelector('[data-mobile-menu-toggle]');
        const mobileNav = document.querySelector('[data-mobile-nav]');
        
        if (mobileMenuToggle && mobileNav) {
            mobileMenuToggle.addEventListener('click', () => {
                mobileNav.classList.toggle('active');
                mobileMenuToggle.classList.toggle('active');
            });
        }

        // Language selector
        const languageToggle = document.querySelector('[data-language-toggle]');
        const languageOptions = document.querySelectorAll('[data-language]');

        if (languageToggle) {
            languageOptions.forEach(option => {
                option.addEventListener('click', (e) => {
                    const language = e.target.dataset.language;
                    this.changeLanguage(language);
                });
            });
        }

        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });

        // Error handling for uncaught errors
        window.addEventListener('error', (e) => {
            this.handleGlobalError(e);
        });

        // Handle API errors
        window.addEventListener('unhandledrejection', (e) => {
            this.handleApiError(e);
        });
    }

    /**
     * Initialize application components
     */
    initializeComponents() {
        this.initToastSystem();
        this.initLoadingSystem();
        this.initAnimations();
    }

    /**
     * Load user preferences from localStorage
     */
    loadUserPreferences() {
        // Language preference
        const savedLanguage = localStorage.getItem('preferred_language');
        if (savedLanguage && savedLanguage !== this.currentLanguage) {
            this.changeLanguage(savedLanguage);
        }

        // Assessment mode preference
        const savedMode = localStorage.getItem('assessment_mode');
        if (savedMode) {
            this.highlightPreferredMode(savedMode);
        }
    }

    /**
     * Change application language
     */
    changeLanguage(language) {
        if (language === this.currentLanguage) return;

        this.currentLanguage = language;
        localStorage.setItem('preferred_language', language);

        // Update language indicator
        const currentLanguageEl = document.querySelector('.current-language');
        if (currentLanguageEl) {
            currentLanguageEl.textContent = language.toUpperCase();
        }

        // Update active language option
        document.querySelectorAll('[data-language]').forEach(option => {
            option.classList.toggle('active', option.dataset.language === language);
        });

        this.showToast('success', `Language changed to ${language === 'vi' ? 'Vietnamese' : 'English'}`);
        
        // In a full implementation, this would trigger translation updates
        // For now, we'll just store the preference
    }

    /**
     * Highlight preferred assessment mode
     */
    highlightPreferredMode(mode) {
        const modeCards = document.querySelectorAll('.mode-card');
        modeCards.forEach(card => {
            if (card.dataset.mode === mode) {
                card.classList.add('active');
            }
        });
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(e) {
        // Escape key - close modals, dropdowns, etc.
        if (e.key === 'Escape') {
            this.closeAllOverlays();
        }

        // Ctrl/Cmd + K - Quick action (if implemented)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            // Could implement quick search/action here
        }

        // Alt + T - Toggle theme
        if (e.altKey && e.key === 't') {
            e.preventDefault();
            window.themeManager?.toggleTheme();
        }

        // Alt + L - Toggle language
        if (e.altKey && e.key === 'l') {
            e.preventDefault();
            const newLang = this.currentLanguage === 'vi' ? 'en' : 'vi';
            this.changeLanguage(newLang);
        }
    }

    /**
     * Handle page visibility changes
     */
    handleVisibilityChange() {
        if (document.hidden) {
            // Page is hidden - pause any animations or timers
            this.pauseAnimations();
        } else {
            // Page is visible - resume animations
            this.resumeAnimations();
        }
    }

    /**
     * Close all overlays and dropdowns
     */
    closeAllOverlays() {
        // Close mobile menu
        const mobileNav = document.querySelector('[data-mobile-nav]');
        const mobileMenuToggle = document.querySelector('[data-mobile-menu-toggle]');
        if (mobileNav && mobileNav.classList.contains('active')) {
            mobileNav.classList.remove('active');
            mobileMenuToggle?.classList.remove('active');
        }

        // Close language dropdown
        const languageDropdowns = document.querySelectorAll('.language-dropdown');
        languageDropdowns.forEach(dropdown => {
            dropdown.style.opacity = '0';
            dropdown.style.visibility = 'hidden';
        });

        // Close any modals
        const modals = document.querySelectorAll('.modal.active');
        modals.forEach(modal => {
            modal.classList.remove('active');
        });
    }

    /**
     * Initialize toast notification system
     */
    initToastSystem() {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('[data-toast-container]');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            toastContainer.setAttribute('data-toast-container', '');
            document.body.appendChild(toastContainer);
        }
    }

    /**
     * Show toast notification
     */
    showToast(type, message, duration = 5000) {
        const toastContainer = document.querySelector('[data-toast-container]');
        if (!toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = this.getToastIcon(type);
        
        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-message">${message}</div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        `;

        toastContainer.appendChild(toast);

        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    /**
     * Get appropriate icon for toast type
     */
    getToastIcon(type) {
        const icons = {
            success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22,4 12,14.01 9,11.01"></polyline>
                      </svg>`,
            error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <line x1="15" y1="9" x2="9" y2="15"></line>
                      <line x1="9" y1="9" x2="15" y2="15"></line>
                    </svg>`,
            warning: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                      </svg>`,
            info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                     <circle cx="12" cy="12" r="10"></circle>
                     <line x1="12" y1="16" x2="12" y2="12"></line>
                     <line x1="12" y1="8" x2="12.01" y2="8"></line>
                   </svg>`
        };
        return icons[type] || icons.info;
    }

    /**
     * Initialize loading system
     */
    initLoadingSystem() {
        // Create loading overlay if it doesn't exist
        let loadingOverlay = document.querySelector('[data-loading-overlay]');
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'loading-overlay';
            loadingOverlay.setAttribute('data-loading-overlay', '');
            loadingOverlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <p class="loading-text">Đang xử lý...</p>
                </div>
            `;
            document.body.appendChild(loadingOverlay);
        }
    }

    /**
     * Show loading overlay
     */
    showLoading(message = 'Đang xử lý...') {
        this.isLoading = true;
        const loadingOverlay = document.querySelector('[data-loading-overlay]');
        const loadingText = loadingOverlay?.querySelector('.loading-text');
        
        if (loadingText) {
            loadingText.textContent = message;
        }
        
        if (loadingOverlay) {
            loadingOverlay.classList.add('active');
        }
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        this.isLoading = false;
        const loadingOverlay = document.querySelector('[data-loading-overlay]');
        if (loadingOverlay) {
            loadingOverlay.classList.remove('active');
        }
    }

    /**
     * Initialize scroll animations
     */
    initAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const delay = entry.target.dataset.delay || 0;
                    setTimeout(() => {
                        entry.target.classList.add('animate-in');
                    }, parseInt(delay));
                }
            });
        }, observerOptions);

        // Observe elements with animation classes
        const animatedElements = document.querySelectorAll('.feature-card, .mode-card, .stat-item');
        animatedElements.forEach((el, index) => {
            el.dataset.delay = index * 100;
            observer.observe(el);
        });
    }

    /**
     * Pause animations when page is hidden
     */
    pauseAnimations() {
        const animatedElements = document.querySelectorAll('[class*="animate"]');
        animatedElements.forEach(el => {
            el.style.animationPlayState = 'paused';
        });
    }

    /**
     * Resume animations when page is visible
     */
    resumeAnimations() {
        const animatedElements = document.querySelectorAll('[class*="animate"]');
        animatedElements.forEach(el => {
            el.style.animationPlayState = 'running';
        });
    }

    /**
     * Handle global JavaScript errors
     */
    handleGlobalError(event) {
        console.error('Global error:', event.error);
        
        // Don't show error toast in production for security
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            this.showToast('error', 'Đã xảy ra lỗi trong ứng dụng');
        }
    }

    /**
     * Handle API/Promise errors
     */
    handleApiError(event) {
        console.error('API error:', event.reason);
        
        // Hide loading if it's showing
        this.hideLoading();
        
        // Show user-friendly error message
        this.showToast('error', 'Không thể kết nối đến server. Vui lòng thử lại.');
    }

    /**
     * Make API request with error handling
     */
    async apiRequest(url, options = {}) {
        try {
            this.showLoading();
            
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.hideLoading();
            
            return data;
        } catch (error) {
            this.hideLoading();
            throw error;
        }
    }

    /**
     * Navigate to assessment mode
     */
    startAssessment(mode) {
        // Store selected mode
        localStorage.setItem('assessment_mode', mode);
        localStorage.setItem('assessment_start_time', new Date().toISOString());
        
        // Show loading
        this.showLoading('Đang khởi tạo đánh giá...');
        
        // Redirect after short delay for UX
        setTimeout(() => {
            if (mode === 'ai') {
                window.location.href = '/chat';
            } else {
                window.location.href = '/assessment';
            }
        }, 1000);
    }

    /**
     * Get session information
     */
    getSessionInfo() {
        return {
            sessionId: this.generateSessionId(),
            language: this.currentLanguage,
            startTime: new Date().toISOString(),
            userAgent: navigator.userAgent,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            }
        };
    }

    /**
     * Generate unique session ID
     */
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Save session data to localStorage
     */
    saveSessionData(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.error('Failed to save session data:', error);
        }
    }

    /**
     * Load session data from localStorage
     */
    loadSessionData(key) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Failed to load session data:', error);
            return null;
        }
    }

    /**
     * Clear session data
     */
    clearSessionData() {
        const keysToKeep = ['theme', 'preferred_language'];
        const keysToRemove = [];
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (!keysToKeep.includes(key)) {
                keysToRemove.push(key);
            }
        }
        
        keysToRemove.forEach(key => localStorage.removeItem(key));
    }

    /**
     * Check browser compatibility
     */
    checkBrowserCompatibility() {
        const requiredFeatures = [
            'fetch',
            'localStorage',
            'addEventListener',
            'classList'
        ];

        const unsupportedFeatures = requiredFeatures.filter(feature => {
            return !(feature in window) && !(feature in Element.prototype);
        });

        if (unsupportedFeatures.length > 0) {
            this.showToast('warning', 'Trình duyệt của bạn có thể không hỗ trợ đầy đủ các tính năng.');
        }
    }
}

// Global functions for template usage
window.startAssessment = function(mode) {
    window.app.startAssessment(mode);
};

window.showToast = function(type, message, duration) {
    window.app.showToast(type, message, duration);
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MentalHealthApp();
    window.app.checkBrowserCompatibility();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MentalHealthApp;
}