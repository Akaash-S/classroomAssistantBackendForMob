import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///classroom_assistant.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require'
        }
    }
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', 'classroom-assistant-audio')
    
    # RapidAPI Configuration
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'your_rapidapi_key')
    RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'your_rapidapi_host')
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your_gemini_api_key')
    GEMINI_MODEL_NAME = 'gemini-2.0-flash'
    GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models'
    
    # Groq API Configuration (for task extraction)
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'your_groq_api_key')
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8081').split(',')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Production-specific database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 30,
        'connect_args': {
            'sslmode': 'require'
        }
    }
    
    # Production CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://your-production-domain.com').split(',')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
