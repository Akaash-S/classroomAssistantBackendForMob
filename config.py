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
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'your_supabase_url')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your_supabase_anon_key')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', 'your_supabase_service_key')
    
    # RapidAPI Configuration
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'your_rapidapi_key')
    RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'your_rapidapi_host')
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your_gemini_api_key')
    GEMINI_MODEL_NAME = 'gemini-2.0-flash'
    GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models'
    
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
