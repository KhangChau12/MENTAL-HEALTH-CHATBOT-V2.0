"""
Mental Health Chatbot - Main Flask Application
Modern, clean architecture with proper error handling
"""

import os
import logging
from flask import Flask, render_template, request, redirect, url_for
from flask_session import Session

# Import configuration
from config import config

# Import API blueprints
from src.api.chat import chat_bp
from src.api.assessment import assessment_bp
from src.api.export import export_bp

# Import services
from src.services.together_ai import initialize_together_client

def create_app(config_name=None):
    """Application factory pattern"""
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Validate configuration
    config[config_name].validate_config()
    
    # Initialize extensions
    Session(app)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize services
    initialize_services(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register routes
    register_routes(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def setup_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/mental_health_chatbot.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Mental Health Chatbot startup')

def initialize_services(app):
    """Initialize external services"""
    with app.app_context():
        # Initialize Together AI client
        if not initialize_together_client():
            app.logger.error("Failed to initialize Together AI client")
        else:
            app.logger.info("Together AI client initialized successfully")

def register_blueprints(app):
    """Register API blueprints"""
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(assessment_bp, url_prefix='/api/assessment')
    app.register_blueprint(export_bp, url_prefix='/api/export')

def register_routes(app):
    """Register main application routes"""
    
    @app.route('/')
    def index():
        """Home page - mode selection"""
        return render_template('home.html')
    
    @app.route('/chat')
    def chat():
        """AI Chat Mode"""
        return render_template('chat.html', mode='ai')
    
    @app.route('/assessment')
    def assessment():
        """Logic Assessment Mode"""
        return render_template('assessment.html', mode='logic')
    
    @app.route('/results')
    def results():
        """Results display page"""
        return render_template('results.html')
    
    @app.route('/about')
    def about():
        """About page"""
        return render_template('about.html')
    
    @app.route('/privacy')
    def privacy():
        """Privacy policy page"""
        return render_template('privacy.html')
    
    @app.route('/admin')
    def admin():
        """Admin dashboard"""
        if not app.config.get('ADMIN_ENABLED', False):
            return redirect(url_for('index'))
        return render_template('admin.html')
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'mental-health-chatbot',
            'version': '2.0.0'
        }

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {error}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {error}')
        return render_template('errors/500.html'), 500

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )