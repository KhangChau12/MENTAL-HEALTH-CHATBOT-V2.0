/**
 * Mental Health Chatbot - Theme Manager
 * Handles dark/light theme switching with system preference detection
 */

class ThemeManager {
    constructor() {
        this.currentTheme = 'light';
        this.systemPrefersDark = false;
        this.init();
    }

    /**
     * Initialize theme manager
     */
    init() {
        this.detectSystemPreference();
        this.loadSavedTheme();
        this.setupEventListeners();
        this.applyTheme(this.currentTheme);
        console.log('Theme manager initialized');
    }

    /**
     * Detect system theme preference
     */
    detectSystemPreference() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            this.systemPrefersDark = mediaQuery.matches;
            
            // Listen for system theme changes
            mediaQuery.addEventListener('change', (e) => {
                this.systemPrefersDark = e.matches;
                
                // If user hasn't set a manual preference, follow system
                const savedTheme = localStorage.getItem('theme');
                if (!savedTheme) {
                    this.setTheme(this.systemPrefersDark ? 'dark' : 'light');
                }
            });
        }
    }

    /**
     * Load saved theme from localStorage
     */
    loadSavedTheme() {
        const savedTheme = localStorage.getItem('theme');
        
        if (savedTheme && ['light', 'dark'].includes(savedTheme)) {
            this.currentTheme = savedTheme;
        } else {
            // No saved preference, use system preference
            this.currentTheme = this.systemPrefersDark ? 'dark' : 'light';
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Theme toggle button
        const themeToggle = document.querySelector('[data-theme-toggle]');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Handle system theme changes when page gains focus
        window.addEventListener('focus', () => {
            // Check if system preference changed while page was hidden
            const currentSystemPreference = window.matchMedia && 
                window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            if (currentSystemPreference !== this.systemPrefersDark) {
                this.systemPrefersDark = currentSystemPreference;
                
                // Update theme if no manual preference is set
                const savedTheme = localStorage.getItem('theme');
                if (!savedTheme) {
                    this.setTheme(this.systemPrefersDark ? 'dark' : 'light');
                }
            }
        });
    }

    /**
     * Apply theme to document
     */
    applyTheme(theme) {
        // Remove existing theme classes
        document.documentElement.classList.remove('dark-theme', 'light-theme');
        
        // Set theme attribute
        document.documentElement.setAttribute('data-theme', theme);
        
        // Add theme class for additional styling if needed
        document.documentElement.classList.add(`${theme}-theme`);
        
        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor(theme);
        
        // Trigger custom event for other components
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: { theme, previousTheme: this.currentTheme }
        }));
        
        this.currentTheme = theme;
    }

    /**
     * Update meta theme-color for mobile browsers
     */
    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.setAttribute('name', 'theme-color');
            document.head.appendChild(metaThemeColor);
        }
        
        const colors = {
            light: '#14B8A6', // Teal
            dark: '#1E293B'    // Dark slate
        };
        
        metaThemeColor.setAttribute('content', colors[theme] || colors.light);
    }

    /**
     * Set specific theme
     */
    setTheme(theme) {
        if (!['light', 'dark'].includes(theme)) {
            console.warn(`Invalid theme: ${theme}`);
            return;
        }

        this.applyTheme(theme);
        localStorage.setItem('theme', theme);
        
        // Show feedback to user
        if (window.app && window.app.showToast) {
            const themeNames = {
                light: 'sáng',
                dark: 'tối'
            };
            window.app.showToast('info', `Đã chuyển sang giao diện ${themeNames[theme]}`, 2000);
        }
    }

    /**
     * Toggle between light and dark themes
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Check if current theme is dark
     */
    isDarkTheme() {
        return this.currentTheme === 'dark';
    }

    /**
     * Reset to system preference
     */
    resetToSystemPreference() {
        localStorage.removeItem('theme');
        const systemTheme = this.systemPrefersDark ? 'dark' : 'light';
        this.setTheme(systemTheme);
        
        if (window.app && window.app.showToast) {
            window.app.showToast('info', 'Đã đặt lại theo thiết lập hệ thống', 2000);
        }
    }

    /**
     * Get theme statistics for analytics
     */
    getThemeStats() {
        return {
            currentTheme: this.currentTheme,
            systemPrefersDark: this.systemPrefersDark,
            hasManualPreference: localStorage.getItem('theme') !== null,
            browserSupportsColorScheme: window.matchMedia !== undefined
        };
    }

    /**
     * Auto theme scheduling (experimental)
     * Automatically switch themes based on time of day
     */
    enableAutoScheduling(enabled = true) {
        if (enabled) {
            this.scheduleAutoTheme();
            // Check every hour
            this.autoThemeInterval = setInterval(() => {
                this.scheduleAutoTheme();
            }, 3600000);
        } else {
            if (this.autoThemeInterval) {
                clearInterval(this.autoThemeInterval);
            }
        }
        
        localStorage.setItem('auto_theme_enabled', enabled.toString());
    }

    /**
     * Schedule theme based on time of day
     */
    scheduleAutoTheme() {
        const hour = new Date().getHours();
        
        // Dark theme from 8 PM to 6 AM
        const shouldBeDark = hour >= 20 || hour < 6;
        const targetTheme = shouldBeDark ? 'dark' : 'light';
        
        if (this.currentTheme !== targetTheme) {
            this.setTheme(targetTheme);
            
            if (window.app && window.app.showToast) {
                const timeBasedMessage = shouldBeDark ? 
                    'Đã chuyển sang giao diện tối cho buổi tối' : 
                    'Đã chuyển sang giao diện sáng cho ban ngày';
                window.app.showToast('info', timeBasedMessage, 3000);
            }
        }
    }

    /**
     * Sync theme across browser tabs
     */
    enableCrossTabSync() {
        window.addEventListener('storage', (e) => {
            if (e.key === 'theme' && e.newValue) {
                const newTheme = e.newValue;
                if (newTheme !== this.currentTheme) {
                    this.applyTheme(newTheme);
                }
            }
        });
    }

    /**
     * Theme transition with animation
     */
    animatedThemeTransition(theme) {
        // Add transition class
        document.documentElement.classList.add('theme-transitioning');
        
        // Apply new theme
        this.applyTheme(theme);
        
        // Remove transition class after animation
        setTimeout(() => {
            document.documentElement.classList.remove('theme-transitioning');
        }, 300);
        
        localStorage.setItem('theme', theme);
    }

    /**
     * Get appropriate colors for current theme
     */
    getThemeColors() {
        const colors = {
            light: {
                primary: '#14B8A6',
                background: '#F8FAFC',
                surface: '#FFFFFF',
                text: '#0F172A',
                textSecondary: '#64748B'
            },
            dark: {
                primary: '#5EEAD4',
                background: '#0F172A',
                surface: '#1E293B',
                text: '#F8FAFC',
                textSecondary: '#94A3B8'
            }
        };
        
        return colors[this.currentTheme] || colors.light;
    }

    /**
     * Update CSS custom properties for dynamic theming
     */
    updateCustomProperties() {
        const colors = this.getThemeColors();
        const root = document.documentElement;
        
        Object.entries(colors).forEach(([property, value]) => {
            root.style.setProperty(`--theme-${property}`, value);
        });
    }

    /**
     * Handle theme-specific media queries
     */
    handleThemeMediaQueries() {
        // Handle print styles
        const printMedia = window.matchMedia('print');
        printMedia.addEventListener('change', (e) => {
            if (e.matches) {
                // Force light theme for printing
                this.tempTheme = this.currentTheme;
                this.applyTheme('light');
            } else if (this.tempTheme) {
                // Restore original theme after printing
                this.applyTheme(this.tempTheme);
                delete this.tempTheme;
            }
        });
    }
}

// CSS for smooth theme transitions
const themeTransitionCSS = `
.theme-transitioning,
.theme-transitioning *,
.theme-transitioning *:before,
.theme-transitioning *:after {
    transition: all 300ms ease-in-out !important;
    transition-delay: 0 !important;
}
`;

// Add transition styles to document
const style = document.createElement('style');
style.textContent = themeTransitionCSS;
document.head.appendChild(style);

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
    window.themeManager.enableCrossTabSync();
    window.themeManager.handleThemeMediaQueries();
    
    // Load auto theme preference
    const autoThemeEnabled = localStorage.getItem('auto_theme_enabled') === 'true';
    if (autoThemeEnabled) {
        window.themeManager.enableAutoScheduling(true);
    }
});

// Global functions for easy access
window.toggleTheme = function() {
    window.themeManager?.toggleTheme();
};

window.setTheme = function(theme) {
    window.themeManager?.setTheme(theme);
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}