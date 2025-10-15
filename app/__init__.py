"""
Cloud Deployment Automation Dashboard
Flask application initialization
"""

from flask import Flask
from flask_socketio import SocketIO
import os

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize SocketIO for real-time features
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app, socketio