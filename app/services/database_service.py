"""
Database Service for Cloud Deployment Dashboard
Handles Supabase database connections and operations
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            logger.info("Supabase credentials not found in environment variables - running in test mode")
            raise ValueError("Supabase credentials not configured")
        
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    def get_deployments(self, limit: int = 10) -> List[Dict]:
        """Get recent deployments"""
        try:
            response = self.supabase.table('deployments').select('*').order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting deployments: {e}")
            return []
    
    def get_deployment_by_id(self, deployment_id: str) -> Optional[Dict]:
        """Get deployment by ID"""
        try:
            response = self.supabase.table('deployments').select('*').eq('id', deployment_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting deployment by ID: {e}")
            return None
    
    def create_deployment(self, deployment_data: Dict) -> bool:
        """Create a new deployment"""
        try:
            # Prepare data with defaults
            data = {
                'id': deployment_data.get('id'),
                'image': deployment_data.get('image'),
                'action': deployment_data.get('action'),
                'environment': deployment_data.get('environment', 'development'),
                'port_mapping': deployment_data.get('port_mapping'),
                'env_vars': deployment_data.get('env_vars'),
                'status': deployment_data.get('status', 'pending'),
                'progress': deployment_data.get('progress', 0),
                'start_time': deployment_data.get('start_time', datetime.now().isoformat()),
                'created_by': deployment_data.get('created_by')
            }
            
            response = self.supabase.table('deployments').insert(data).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error creating deployment: {e}")
            return False
    
    def update_deployment(self, deployment_id: str, updates: Dict) -> bool:
        """Update deployment status and progress"""
        try:
            # Add updated_at timestamp
            updates['updated_at'] = datetime.now().isoformat()
            
            response = self.supabase.table('deployments').update(updates).eq('id', deployment_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error updating deployment: {e}")
            return False
    
    def get_health_checks(self, limit: int = 10) -> List[Dict]:
        """Get recent health checks"""
        try:
            response = self.supabase.table('health_checks').select('*').order('timestamp', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting health checks: {e}")
            return []
    
    def save_health_check(self, health_data: Dict) -> bool:
        """Save health check result"""
        try:
            data = {
                'overall_status': health_data.get('overall_status'),
                'checks': health_data.get('checks', {}),
                'duration_ms': health_data.get('duration_ms', 0)
            }
            
            response = self.supabase.table('health_checks').insert(data).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error saving health check: {e}")
            return False
    
    def get_system_metrics(self, limit: int = 20) -> List[Dict]:
        """Get recent system metrics"""
        try:
            response = self.supabase.table('system_metrics').select('*').order('timestamp', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return []
    
    def save_system_metrics(self, metrics_data: Dict) -> bool:
        """Save system metrics"""
        try:
            data = {
                'cpu_usage': metrics_data.get('cpu_usage'),
                'memory_usage': metrics_data.get('memory_usage'),
                'disk_usage': metrics_data.get('disk_usage'),
                'network_io': metrics_data.get('network_io', {}),
                'active_containers': metrics_data.get('active_containers', 0)
            }
            
            response = self.supabase.table('system_metrics').insert(data).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error saving system metrics: {e}")
            return False
    
    def get_deployment_logs(self, deployment_id: str = None, limit: int = 100) -> List[Dict]:
        """Get deployment logs"""
        try:
            query = self.supabase.table('deployment_logs').select('*')
            
            if deployment_id:
                query = query.eq('deployment_id', deployment_id)
            
            response = query.order('timestamp', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting deployment logs: {e}")
            return []
    
    def save_deployment_log(self, log_data: Dict) -> bool:
        """Save deployment log"""
        try:
            response = self.supabase.table('deployment_logs').insert(log_data).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error saving deployment log: {e}")
            return False
    
    def get_containers(self) -> List[Dict]:
        """Get all containers"""
        try:
            response = self.supabase.table('containers').select('*').order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting containers: {e}")
            return []
    
    def save_container(self, container_data: Dict) -> bool:
        """Save or update container information"""
        try:
            container_id = container_data.get('id')
            
            # Check if container exists
            existing = self.supabase.table('containers').select('id').eq('id', container_id).execute()
            
            data = {
                'id': container_data.get('id'),
                'name': container_data.get('name'),
                'image': container_data.get('image'),
                'status': container_data.get('status'),
                'ports': container_data.get('ports', []),
                'started_at': container_data.get('started_at'),
                'deployment_id': container_data.get('deployment_id')
            }
            
            if existing.data:
                # Update existing container
                response = self.supabase.table('containers').update(data).eq('id', container_id).execute()
            else:
                # Insert new container
                response = self.supabase.table('containers').insert(data).execute()
            
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error saving container: {e}")
            return False
    
    def get_deployment_metrics(self) -> Dict:
        """Get deployment metrics for dashboard"""
        try:
            # Get all deployments
            all_deployments = self.supabase.table('deployments').select('status, created_at').execute()
            
            if not all_deployments.data:
                return {
                    'total_deployments': 0,
                    'success_rate': 0,
                    'recent_deployments': []
                }
            
            # Count by status
            status_counts = {}
            recent_count = 0
            total_last_week = 0
            successful_last_week = 0
            
            from datetime import datetime, timedelta
            now = datetime.now()
            yesterday = now - timedelta(days=1)
            week_ago = now - timedelta(days=7)
            
            for deployment in all_deployments.data:
                status = deployment['status']
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Parse created_at timestamp
                try:
                    created_at = datetime.fromisoformat(deployment['created_at'].replace('Z', '+00:00'))
                    
                    if created_at >= yesterday:
                        recent_count += 1
                    
                    if created_at >= week_ago:
                        total_last_week += 1
                        if status == 'completed':
                            successful_last_week += 1
                except:
                    pass
            
            success_rate = 0
            if total_last_week > 0:
                success_rate = (successful_last_week / total_last_week) * 100
            
            # Get recent deployments
            recent_deployments = self.get_deployments(5)
            
            return {
                'total_deployments': len(all_deployments.data),
                'success_rate': round(success_rate, 2),
                'recent_deployments': recent_deployments
            }
        except Exception as e:
            logger.error(f"Error getting deployment metrics: {e}")
            return {
                'total_deployments': 0,
                'success_rate': 0,
                'recent_deployments': []
            }
    
    def close_connection(self):
        """Close database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None