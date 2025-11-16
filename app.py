from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import sys
from datetime import datetime
import logging
from config import config

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Initialize extensions
from database import db
db.init_app(app)
migrate = Migrate(app, db)
CORS(app, origins=app.config['CORS_ORIGINS'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models
from models import User, Lecture, Task, Notification

# Import routes
from routes.auth_working import auth_bp
from routes.lectures import lectures_bp
from routes.tasks import tasks_bp
from routes.notifications import notifications_bp
from routes.ai import ai_bp
from routes.processing import processing_bp
from routes.chat import chat_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(lectures_bp, url_prefix='/api/lectures')
app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
app.register_blueprint(ai_bp, url_prefix='/api/ai')
app.register_blueprint(processing_bp, url_prefix='/api/processing')
app.register_blueprint(chat_bp, url_prefix='/api/chat')

# Database initialization function
def init_database():
    """Initialize the database with all tables"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")
            return True
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        return False

@app.route('/')
def health_check():
    """Root endpoint for Render health checks"""
    return jsonify({
        'status': 'success',
        'message': 'Classroom Assistant API is running',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/health')
def api_health():
    """Detailed health check endpoint"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = 'connected'
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'port': os.getenv('PORT', '5000'),
        'environment': os.getenv('FLASK_ENV', 'development'),
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

# Initialize database on import (for Gunicorn)
try:
    with app.app_context():
        db.create_all()
        logger.info("Database tables initialized")
except Exception as e:
    logger.error(f"Database initialization error: {str(e)}")

# Start background processor (for Gunicorn)
try:
    from services.background_processor import background_processor
    background_processor.start()
    logger.info("Background processor started")
except Exception as e:
    logger.warning(f"Background processor not started: {str(e)}")

if __name__ == '__main__':
    # Development server
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting Classroom Assistant Backend on port {port}...")
    app.run(debug=False, host='0.0.0.0', port=port)
