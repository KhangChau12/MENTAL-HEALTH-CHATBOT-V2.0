"""
Mental Health Chatbot - Main Flask Application
Fixed to work with new AI-powered transition logic
"""

import os
import sys
import logging
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

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

# Import configuration - FIXED
from config import FLASK_DEBUG, SECRET_KEY, FLASK_ENV, validate_config

# Import API blueprints
from src.api.chat import chat_bp
try:
    from src.api.assessment import assessment_bp
except ImportError:
    assessment_bp = None
    
try:
    from src.api.export import export_bp  
except ImportError:
    export_bp = None

# Import services
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
    """Register API blueprints"""
    # Always register chat blueprint (main functionality)
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.logger.info("Registered chat blueprint")
    
    # Initialize chat services after registering blueprint
    try:
        from src.api.chat import register_init_services
        register_init_services(app)
    except Exception as e:
        app.logger.error(f"Failed to initialize chat services: {e}")
    
    # Register assessment blueprint if available
    if assessment_bp:
        app.register_blueprint(assessment_bp, url_prefix='/api/assessment')
        app.logger.info("Registered assessment blueprint")
    else:
        app.logger.warning("Assessment blueprint not available")
    
    # Register export blueprint if available
    if export_bp:
        app.register_blueprint(export_bp, url_prefix='/api/export')
        app.logger.info("Registered export blueprint")
    else:
        app.logger.warning("Export blueprint not available")

def register_routes(app):
    """Register main application routes"""
    
    @app.route('/')
    def index():
        """Home page - chatbot interface"""
        return render_template('home.html')
    
    @app.route('/chat')
    def chat():
        """Chat interface page"""
        # Initialize session if needed
        if 'session_id' not in session:
            session['session_id'] = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            session['created_at'] = datetime.now().isoformat()
        
        return render_template('chat.html', session_id=session['session_id'])
    
    @app.route('/assessment')
    def assessment():
        """Assessment page"""
        return render_template('assessment.html')
    
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
        return render_template('admin.html')
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            # Check basic functionality
            health_status = {
                'status': 'healthy',
                'service': 'mental-health-chatbot',
                'version': '2.0.0-ai-powered',
                'timestamp': datetime.now().isoformat(),
                'components': {
                    'flask': 'running',
                    'together_ai': 'unknown',
                    'ai_analyzer': 'unknown'
                }
            }
            
            # Check Together AI
            try:
                client = get_together_client()
                health_status['components']['together_ai'] = 'available' if client else 'unavailable'
            except:
                health_status['components']['together_ai'] = 'error'
            
            # Check AI analyzer
            try:
                from src.services.ai_context_analyzer import ai_context_analyzer
                health_status['components']['ai_analyzer'] = 'available' if ai_context_analyzer.initialized else 'unavailable'
            except:
                health_status['components']['ai_analyzer'] = 'error'
            
            return health_status
            
        except Exception as e:
            app.logger.error(f"Health check error: {e}")
            return {
                'status': 'unhealthy', 
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, 500

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f"404 error: {request.url}")
        try:
            return render_template('errors/404.html'), 404
        except:
            return {'error': 'Page not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {error}')
        try:
            return render_template('errors/500.html'), 500
        except:
            return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {error}', exc_info=True)
        try:
            return render_template('errors/500.html'), 500
        except:
            return {'error': 'An unexpected error occurred'}, 500

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
        
        # Create a basic index.html if it doesn't exist
        index_path = os.path.join(template_dir, 'index.html')
        if not os.path.exists(index_path):
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Mental Health Chatbot</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>🤖 Mental Health Chatbot</h1>
    <p>Chatbot hỗ trợ sức khỏe tâm thần với AI-powered transition logic</p>
    <div id="chat-container">
        <div id="messages"></div>
        <input type="text" id="user-input" placeholder="Nhập tin nhắn của bạn...">
        <button onclick="sendMessage()">Gửi</button>
    </div>
    
    <script>
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            if (!message) return;
            
            // Display user message
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML += `<div><strong>Bạn:</strong> ${message}</div>`;
            
            try {
                const response = await fetch('/api/chat/send_message', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: message,
                        history: [],
                        state: {},
                        use_ai: true
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    messagesDiv.innerHTML += `<div><strong>Bot:</strong> ${data.message}</div>`;
                } else {
                    messagesDiv.innerHTML += `<div><strong>Error:</strong> ${data.error}</div>`;
                }
            } catch (error) {
                messagesDiv.innerHTML += `<div><strong>Error:</strong> ${error.message}</div>`;
            }
            
            input.value = '';
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        // Allow Enter key to send message
        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
    
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        #chat-container { border: 1px solid #ddd; padding: 20px; margin-top: 20px; }
        #messages { height: 400px; overflow-y: scroll; border: 1px solid #eee; padding: 10px; margin-bottom: 10px; }
        #user-input { width: 70%; padding: 10px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</body>
</html>""")
    
    print("✅ Application setup complete!")
    
    # Start development server
    try:
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=app.config['DEBUG'],
            threaded=True
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()