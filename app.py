"""
Cloud Deployment Automation Dashboard
Main Flask Application Entry Point
"""

import os
import logging
from app import create_app
from app.services.realtime_service import init_realtime_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Create Flask app and SocketIO
    app, socketio = create_app()
    
    # Initialize real-time service
    realtime_service = init_realtime_service(socketio)
    
    # Start real-time monitoring
    realtime_service.start_monitoring()
    
    logger.info("Starting Cloud Deployment Dashboard...")
    logger.info("Real-time monitoring enabled")
    
    # Run the application
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)