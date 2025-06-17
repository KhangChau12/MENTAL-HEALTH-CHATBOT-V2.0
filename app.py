"""
Mental Health Chatbot - Main Flask Application
COMPLETE REWRITE - Fixed all import conflicts and route issues
"""

import os
import sys
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import traceback

# Fix Unicode encoding for Windows
if os.name == 'nt':  # Windows
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass  # Use default locale

# Set stdout/stderr encoding for Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import configuration - FIXED to handle missing config gracefully
try:
    from config import FLASK_DEBUG, SECRET_KEY, FLASK_ENV, validate_config
except ImportError:
    # Fallback configuration if config.py is missing
    FLASK_DEBUG = True
    SECRET_KEY = 'dev-secret-key-change-in-production'
    FLASK_ENV = 'development'
    
    def validate_config():
        return ["Config file missing - using fallback configuration"]

# Import services with error handling
from src.services.ai_context_analyzer import initialize_ai_analyzer
from src.services.together_client import get_together_client

def create_app():
    """Create and configure Flask application"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = FLASK_DEBUG
    app.config['ENV'] = FLASK_ENV
    
    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
    
    # Setup logging
    setup_logging(app)
    
    # Validate configuration
    try:
        config_issues = validate_config()
        if config_issues:
            app.logger.warning("Config issues:")
            for issue in config_issues:
                app.logger.warning(f"  - {issue}")
    except Exception as e:
        app.logger.error(f"Config validation failed: {e}")
    
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
    """Configure application logging with proper Unicode support"""
    # Create logs directory
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Setup file handler with UTF-8 encoding
    log_file = os.path.join('logs', 'chatbot.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # Set log level
    if app.config['DEBUG']:
        file_handler.setLevel(logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)
    else:
        file_handler.setLevel(logging.INFO)
        app.logger.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    
    # Use simple English messages to avoid Unicode issues
    app.logger.info('Mental Health Chatbot starting up')
    
    # Set console handler encoding if needed
    try:
        # For Windows console compatibility
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        console_handler.setLevel(logging.WARNING)
        app.logger.addHandler(console_handler)
    except Exception as e:
        print(f"Console handler setup failed: {e}")
        pass

def initialize_services(app):
    """Initialize external services"""
    with app.app_context():
        # Test Together AI client
        try:
            client = get_together_client()
            if client:
                app.logger.info("Together AI client ready")
            else:
                app.logger.warning("Together AI client not available")
        except Exception as e:
            app.logger.error(f"Together AI client error: {e}")
        
        # Initialize AI analyzer
        try:
            if initialize_ai_analyzer():
                app.logger.info("AI Context Analyzer ready")
            else:
                app.logger.warning("AI Context Analyzer failed - using fallback mode")
        except Exception as e:
            app.logger.error(f"AI Context Analyzer error: {e}")

def register_blueprints(app):
    """Register API blueprints - FIXED with proper error handling"""
    
    # Always register chat blueprint (main functionality)
    try:
        from src.api.chat import chat_bp
        app.register_blueprint(chat_bp, url_prefix='/api/chat')
        app.logger.info("Registered chat blueprint")
        
        # Initialize chat services after registering blueprint
        try:
            from src.api.chat import register_init_services
            register_init_services(app)
        except Exception as e:
            app.logger.error(f"Failed to initialize chat services: {e}")
            
    except ImportError as e:
        app.logger.error(f"Failed to import chat blueprint: {e}")
    except Exception as e:
        app.logger.error(f"Failed to register chat blueprint: {e}")
    
    # FIXED: Register assessment blueprint with proper error handling
    try:
        from src.api.assessment import assessment_bp
        if assessment_bp:
            app.register_blueprint(assessment_bp, url_prefix='/api/assessment')
            app.logger.info("Registered assessment blueprint")
        else:
            app.logger.warning("Assessment blueprint not available")
    except ImportError as e:
        app.logger.warning(f"Assessment blueprint not available - import error: {e}")
    except Exception as e:
        app.logger.error(f"Failed to register assessment blueprint: {e}")
    
    # Register export blueprint if available
    try:
        from src.api.export import export_bp
        if export_bp:
            app.register_blueprint(export_bp, url_prefix='/api/export')
            app.logger.info("Registered export blueprint")
        else:
            app.logger.warning("Export blueprint not available")
    except ImportError as e:
        app.logger.warning(f"Export blueprint not available - import error: {e}")
    except Exception as e:
        app.logger.error(f"Failed to register export blueprint: {e}")

def register_routes(app):
    """Register main application routes - FIXED to avoid conflicts"""
    
    @app.route('/')
    def index():
        """Home page - assessment mode selection"""
        try:
            return render_template('home.html')
        except Exception as e:
            app.logger.error(f"Error rendering home page: {e}")
            return render_template_safe('error.html', 
                                      error_message='Không thể tải trang chủ'), 500
    
    @app.route('/chat')
    def chat():
        """Chat interface page - AI mode"""
        try:
            # Initialize session if needed
            if 'session_id' not in session:
                session['session_id'] = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                session['created_at'] = datetime.now().isoformat()
            
            return render_template('chat.html', session_id=session['session_id'])
        except Exception as e:
            app.logger.error(f"Error rendering chat page: {e}")
            return render_template_safe('error.html', 
                                      error_message='Không thể tải trang trò chuyện'), 500
    
    # FIXED: Assessment page route - no conflicts with API blueprint
    @app.route('/assessment')
    def assessment_page():
        """Assessment page - Logic mode with structured questionnaires"""
        try:
            # Prepare assessment data for template (matches assessment.html expectations)
            assessment_types = {
                'phq9': {
                    'title': 'PHQ-9 - Đánh giá Trầm cảm',
                    'description': 'Bộ câu hỏi sàng lọc trầm cảm được sử dụng rộng rãi trong y tế, giúp đánh giá mức độ và triệu chứng trầm cảm.',
                    'question_count': 9,
                    'estimated_time': '3-5 phút',
                    'category': 'depression'
                },
                'gad7': {
                    'title': 'GAD-7 - Đánh giá Lo âu',
                    'description': 'Bộ câu hỏi đánh giá rối loạn lo âu tổng quát, được phát triển để sàng lọc và đánh giá mức độ lo âu.',
                    'question_count': 7,
                    'estimated_time': '2-4 phút',
                    'category': 'anxiety'
                },
                'dass21_stress': {
                    'title': 'DASS-21 - Đánh giá Căng thẳng',
                    'description': 'Phần đánh giá stress từ bộ DASS-21, giúp đo lường mức độ căng thẳng và áp lực tâm lý.',
                    'question_count': 7,
                    'estimated_time': '3-5 phút',
                    'category': 'stress'
                },
                'suicide_risk': {
                    'title': 'Đánh giá Nguy cơ Tự tử',
                    'description': 'Đánh giá nhanh nguy cơ tự tử và các yếu tố liên quan.',
                    'question_count': 5,
                    'estimated_time': '2-3 phút',
                    'category': 'risk'
                }
            }
            
            return render_template('assessment.html', 
                                 assessment_types=assessment_types,
                                 page_title='Đánh giá Sức khỏe Tâm thần')
        
        except Exception as e:
            app.logger.error(f"Error rendering assessment page: {e}")
            return render_template_safe('error.html', 
                                      error_message='Không thể tải trang đánh giá'), 500
    
    @app.route('/results')
    def results():
        """Results display page"""
        try:
            return render_template('results.html')
        except Exception as e:
            app.logger.error(f"Error rendering results page: {e}")
            return render_template_safe('error.html', 
                                      error_message='Không thể tải trang kết quả'), 500
    
    @app.route('/about')
    def about():
        """About page"""
        try:
            return render_template('about.html')
        except Exception as e:
            app.logger.error(f"Error rendering about page: {e}")
            return render_template_safe('error.html', 
                                      error_message='Không thể tải trang giới thiệu'), 500
    
    @app.route('/privacy')
    def privacy():
        """Privacy policy page"""
        try:
            return render_template('privacy.html')
        except Exception as e:
            app.logger.error(f"Error rendering privacy page: {e}")
            return render_template_safe('error.html', 
                                      error_message='Không thể tải trang chính sách'), 500
    
    # ADDED: Health check endpoint for monitoring
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'services': {
                    'web_server': 'running',
                    'templates': 'available',
                    'static_files': 'available'
                }
            }
            
            # Check if critical templates exist
            template_dir = os.path.join(app.template_folder or 'templates')
            critical_templates = ['base.html', 'home.html', 'chat.html', 'assessment.html']
            
            for template in critical_templates:
                template_path = os.path.join(template_dir, template)
                if not os.path.exists(template_path):
                    health_status['services'][f'template_{template}'] = 'missing'
                    health_status['status'] = 'degraded'
                else:
                    health_status['services'][f'template_{template}'] = 'available'
            
            status_code = 200 if health_status['status'] == 'healthy' else 503
            return jsonify(health_status), status_code
            
        except Exception as e:
            app.logger.error(f"Health check error: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

def render_template_safe(template_name, **kwargs):
    """Safe template rendering with fallback"""
    try:
        return render_template(template_name, **kwargs)
    except Exception as e:
        # Fallback to basic HTML if template fails
        error_message = kwargs.get('error_message', 'Đã xảy ra lỗi')
        return f"""
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Lỗi - Trợ lý Sức khỏe Tâm thần</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                .error {{ color: #dc3545; margin: 20px 0; }}
                .btn {{ 
                    display: inline-block; 
                    padding: 10px 20px; 
                    background: #007bff; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <h1>🤖 Trợ lý Sức khỏe Tâm thần</h1>
            <div class="error">
                <h2>Có lỗi xảy ra</h2>
                <p>{error_message}</p>
            </div>
            <a href="/" class="btn">Quay lại trang chủ</a>
        </body>
        </html>
        """

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found(error):
        try:
            return render_template('errors/404.html'), 404
        except:
            return render_template_safe('error.html', 
                                      error_message='Trang không tồn tại'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {error}')
        try:
            return render_template('errors/500.html'), 500
        except:
            return render_template_safe('error.html', 
                                      error_message='Lỗi máy chủ nội bộ'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {error}', exc_info=True)
        try:
            return render_template('errors/500.html'), 500
        except:
            return render_template_safe('error.html', 
                                      error_message='Đã xảy ra lỗi không mong muốn'), 500

# Global exception handler for better debugging
def log_exception(sender, exception, **extra):
    """Log exceptions globally"""
    sender.logger.error(f'Global exception handler: {exception}', exc_info=True)

# Create application instance
app = create_app()

# Connect exception handler
try:
    from flask.signals import got_request_exception
    got_request_exception.connect(log_exception, app)
except ImportError:
    pass  # Signals not available in older Flask versions

if __name__ == '__main__':
    print("🚀 Starting Mental Health Chatbot...")
    print(f"Debug mode: {app.config['DEBUG']}")
    print(f"Environment: {app.config['ENV']}")
    
    # Check if templates directory exists
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(template_dir):
        print(f"⚠️ Warning: Templates directory not found at {template_dir}")
        print("Creating basic templates directory...")
        os.makedirs(template_dir, exist_ok=True)
    else:
        print(f"✅ Templates directory found: {template_dir}")
        
        # Check critical templates
        critical_templates = ['base.html', 'home.html', 'chat.html', 'assessment.html']
        missing_templates = []
        
        for template in critical_templates:
            template_path = os.path.join(template_dir, template)
            if not os.path.exists(template_path):
                missing_templates.append(template)
            else:
                print(f"✅ Template found: {template}")
        
        if missing_templates:
            print(f"⚠️ Warning: Missing templates: {', '.join(missing_templates)}")
        else:
            print("✅ All critical templates found")
    
    # Check static directory
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_dir):
        print(f"⚠️ Warning: Static directory not found at {static_dir}")
        os.makedirs(static_dir, exist_ok=True)
        os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
        os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)
        os.makedirs(os.path.join(static_dir, 'images'), exist_ok=True)
    else:
        print(f"✅ Static directory found: {static_dir}")
    
    # Run the application
    try:
        app.run(
            host='0.0.0.0', 
            port=5000, 
            debug=app.config['DEBUG'],
            use_reloader=app.config['DEBUG']
        )
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)