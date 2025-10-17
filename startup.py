"""
Azure App Service Startup Script
Optimized for Azure App Service deployment
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for Azure
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def configure_azure_environment():
    """Configure environment variables for Azure App Service"""
    
    # Azure App Service specific configurations
    port = os.environ.get('PORT', '8000')
    os.environ['PORT'] = port
    
    # Set Flask environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Azure-specific database URL format
    if 'AZURE_POSTGRESQL_CONNECTIONSTRING' in os.environ:
        # Convert Azure connection string to standard format
        azure_conn = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
        # Azure format: host=xxx.postgres.database.azure.com port=5432 dbname=xxx user=xxx password=xxx sslmode=require
        if 'DATABASE_URL' not in os.environ:
            os.environ['DATABASE_URL'] = f"postgresql://{azure_conn}"
    
    logger.info(f"Azure App Service configured on port {port}")
    return port

if __name__ == "__main__":
    # Configure Azure environment
    port = configure_azure_environment()
    
    # Import and run the Flask app
    from app import create_app
    from app.services.realtime_service import init_realtime_service
    
    app = create_app()
    socketio = init_realtime_service(app)
    
    logger.info("Starting Cloud Deployment Dashboard on Azure App Service...")
    
    # Run with SocketIO support
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(port),
        debug=False,
        use_reloader=False
    )
    