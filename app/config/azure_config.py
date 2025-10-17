"""
Azure-specific configuration for Cloud Deployment Dashboard
"""
import os
import re
from urllib.parse import urlparse

class AzureConfig:
    """Azure configuration class"""
    
    def __init__(self):
        self.setup_azure_environment()
    
    def setup_azure_environment(self):
        """Setup Azure-specific environment variables"""
        
        # Azure App Service automatically provides these
        self.port = int(os.environ.get('PORT', 8000))
        self.host = os.environ.get('HOST', '0.0.0.0')
        
        # Azure Database connection
        self.database_url = self.get_database_url()
        
        # Azure-specific settings
        self.azure_resource_group = os.environ.get('AZURE_RESOURCE_GROUP', '')
        self.azure_subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID', '')
        
        # Application settings
        self.secret_key = os.environ.get('SECRET_KEY', 'azure-dev-key-change-in-production')
        self.flask_env = os.environ.get('FLASK_ENV', 'production')
        
        # Supabase settings (can be used alongside Azure PostgreSQL)
        self.supabase_url = os.environ.get('SUPABASE_URL', '')
        self.supabase_anon_key = os.environ.get('SUPABASE_ANON_KEY', '')
        self.supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY', '')
    
    def get_database_url(self):
        """
        Get database URL, handling both Azure PostgreSQL and Supabase formats
        """
        # Try Azure PostgreSQL first
        azure_db_url = os.environ.get('DATABASE_URL')
        if azure_db_url:
            return self.convert_azure_postgres_url(azure_db_url)
        
        # Fallback to Supabase
        supabase_url = os.environ.get('SUPABASE_URL')
        if supabase_url:
            return self.build_supabase_connection_string()
        
        # Default local development
        return 'postgresql://localhost:5432/cloud_deployment_dashboard'
    
    def convert_azure_postgres_url(self, url):
        """
        Convert Azure PostgreSQL connection string to standard format
        Azure format: postgres://username:password@server:port/database?sslmode=require
        """
        if not url:
            return None
            
        # Parse the URL
        parsed = urlparse(url)
        
        # Handle Azure-specific SSL requirements
        if 'sslmode' not in url:
            if '?' in url:
                url += '&sslmode=require'
            else:
                url += '?sslmode=require'
        
        return url
    
    def build_supabase_connection_string(self):
        """
        Build PostgreSQL connection string from Supabase URL
        """
        supabase_url = self.supabase_url
        if not supabase_url:
            return None
        
        # Extract database info from Supabase URL
        # Format: https://xxx.supabase.co
        match = re.search(r'https://([^.]+)\.supabase\.co', supabase_url)
        if not match:
            return None
        
        project_id = match.group(1)
        
        # Build PostgreSQL connection string
        # Note: You'll need to get the actual database password from Supabase dashboard
        db_password = os.environ.get('SUPABASE_DB_PASSWORD', '')
        
        if db_password:
            return f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres?sslmode=require"
        
        return None
    
    def get_azure_credentials(self):
        """Get Azure credentials for service authentication"""
        return {
            'client_id': os.environ.get('AZURE_CLIENT_ID', ''),
            'client_secret': os.environ.get('AZURE_CLIENT_SECRET', ''),
            'tenant_id': os.environ.get('AZURE_TENANT_ID', ''),
            'subscription_id': self.azure_subscription_id
        }
    
    def is_azure_environment(self):
        """Check if running in Azure environment"""
        return bool(os.environ.get('WEBSITE_SITE_NAME'))  # Azure App Service specific
    
    def get_logging_config(self):
        """Get Azure-optimized logging configuration"""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'azure': {
                    'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'azure',
                    'level': 'INFO'
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console']
            }
        }

# Global Azure config instance
azure_config = AzureConfig()