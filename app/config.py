"""
Application Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Application Settings
    APP_NAME = os.environ.get('APP_NAME', 'Cloud Deployment Dashboard')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # DigitalOcean Configuration
    DIGITALOCEAN_ACCESS_TOKEN = os.environ.get('DIGITALOCEAN_ACCESS_TOKEN')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}