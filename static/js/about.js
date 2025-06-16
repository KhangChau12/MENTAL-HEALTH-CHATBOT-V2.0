/**
 * About Page JavaScript
 * Enhanced animations and interactions
 */

class AboutPage {
    constructor() {
        this.initScrollAnimations();
        this.initInteractions();
        this.initParallax();
        console.log('About page initialized');
    }
    
    initScrollAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);
        
        // Observe feature cards
        document.querySelectorAll('.feature-card').forEach(card => {
            observer.observe(card);
        });
        
        // Observe step items
        document.querySelectorAll('.step-item').forEach(step => {
            observer.observe(step);
        });
        
        // Observe sections
        document.querySelectorAll('.mission-section, .features-section, .how-it-works-section').forEach(section => {
            observer.observe(section);
        });
    }
    
    initInteractions() {
        // Feature card hover effects
        document.querySelectorAll('.feature-card').forEach(card => {
            card.addEventListener('mouseenter', this.handleCardHover);
            card.addEventListener('mouseleave', this.handleCardLeave);
        });
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', this.handleSmoothScroll);
        });
        
        // CTA button interactions
        document.querySelectorAll('.cta-button').forEach(button => {
            button.addEventListener('click', this.handleCTAClick);
        });
    }
    
    initParallax() {
        // Simple parallax effect for hero section
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const heroSection = document.querySelector('.hero-section');
            
            if (heroSection) {
                const speed = scrolled * 0.5;
                heroSection.style.transform = `translateY(${speed}px)`;
            }
        });
    }
    
    handleCardHover(event) {
        const card = event.currentTarget;
        const icon = card.querySelector('.feature-icon');
        
        if (icon) {
            icon.style.transform = 'scale(1.1) rotate(5deg)';
            icon.style.transition = 'transform 0.3s ease';
        }
    }
    
    handleCardLeave(event) {
        const card = event.currentTarget;
        const icon = card.querySelector('.feature-icon');
        
        if (icon) {
            icon.style.transform = 'scale(1) rotate(0deg)';
        }
    }
    
    handleSmoothScroll(event) {
        event.preventDefault();
        const targetId = event.currentTarget.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
            const offsetTop = targetElement.getBoundingClientRect().top + window.pageYOffset - 80;
            
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    }
    
    handleCTAClick(event) {
        const button = event.currentTarget;
        
        // Add click animation
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = 'scale(1)';
        }, 150);
        
        // Track analytics if needed
        console.log('CTA clicked:', button.href);
    }
    
    // Utility methods
    isElementInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    
    // Counter animation for statistics (if added)
    animateCounter(element, target, duration = 2000) {
        let start = 0;
        const increment = target / (duration / 16);
        
        const timer = setInterval(() => {
            start += increment;
            element.textContent = Math.floor(start);
            
            if (start >= target) {
                clearInterval(timer);
                element.textContent = target;
            }
        }, 16);
    }
    
    // Add floating animation to visual elements
    addFloatingAnimation() {
        const floatingElements = document.querySelectorAll('.visual-icon, .step-number');
        
        floatingElements.forEach((element, index) => {
            element.style.animation = `float 3s ease-in-out infinite`;
            element.style.animationDelay = `${index * 0.5}s`;
        });
    }
    
    // Initialize typing effect for hero subtitle
    initTypingEffect() {
        const subtitle = document.querySelector('.hero-subtitle');
        if (!subtitle) return;
        
        const text = subtitle.textContent;
        subtitle.textContent = '';
        subtitle.style.borderRight = '2px solid rgba(255,255,255,0.7)';
        
        let index = 0;
        const typingInterval = setInterval(() => {
            if (index < text.length) {
                subtitle.textContent += text.charAt(index);
                index++;
            } else {
                clearInterval(typingInterval);
                setTimeout(() => {
                    subtitle.style.borderRight = 'none';
                }, 1000);
            }
        }, 50);
    }
}

// Enhanced CSS animations
const aboutPageStyles = `
    .animate-in {
        animation: slideInUp 0.8s ease forwards;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .feature-card {
        transition: all 0.3s ease;
        opacity: 0;
        transform: translateY(30px);
    }
    
    .feature-card.animate-in {
        opacity: 1;
        transform: translateY(0);
    }
    
    .step-item {
        opacity: 0;
        transform: scale(0.8);
        transition: all 0.5s ease;
    }
    
    .step-item.animate-in {
        opacity: 1;
        transform: scale(1);
    }
    
    .hero-section {
        transition: transform 0.1s ease-out;
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    .floating {
        animation: float 3s ease-in-out infinite;
    }
    
    .cta-button {
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .cta-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .cta-button:hover::before {
        left: 100%;
    }
    
    .disclaimer-card {
        border-left: 4px solid var(--color-warning);
        transition: all 0.3s ease;
    }
    
    .disclaimer-card:hover {
        transform: translateX(5px);
        box-shadow: var(--shadow-lg);
    }
    
    @media (prefers-reduced-motion: no-preference) {
        .feature-card:nth-child(1) { animation-delay: 0.1s; }
        .feature-card:nth-child(2) { animation-delay: 0.2s; }
        .feature-card:nth-child(3) { animation-delay: 0.3s; }
        .feature-card:nth-child(4) { animation-delay: 0.4s; }
        .feature-card:nth-child(5) { animation-delay: 0.5s; }
        .feature-card:nth-child(6) { animation-delay: 0.6s; }
    }
    
    @media (prefers-reduced-motion: reduce) {
        .animate-in,
        .feature-card,
        .step-item {
            animation: none;
            opacity: 1;
            transform: none;
        }
        
        .hero-section {
            transform: none !important;
        }
    }
`;

// Initialize about page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Inject custom styles
    const styleSheet = document.createElement('style');
    styleSheet.textContent = aboutPageStyles;
    document.head.appendChild(styleSheet);
    
    // Initialize about page functionality
    window.aboutPage = new AboutPage();
    
    // Add floating animations after a short delay
    setTimeout(() => {
        window.aboutPage.addFloatingAnimation();
    }, 1000);
    
    // Initialize typing effect if on hero section
    if (document.querySelector('.hero-section')) {
        setTimeout(() => {
            window.aboutPage.initTypingEffect();
        }, 500);
    }
});

// Handle page visibility for performance
document.addEventListener('visibilitychange', function() {
    const floatingElements = document.querySelectorAll('.floating');
    
    if (document.hidden) {
        // Pause animations when page is hidden
        floatingElements.forEach(el => {
            el.style.animationPlayState = 'paused';
        });
    } else {
        // Resume animations when page is visible
        floatingElements.forEach(el => {
            el.style.animationPlayState = 'running';
        });
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AboutPage;
}