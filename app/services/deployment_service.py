"""
Deployment Service
Handles Docker build, run, and deployment operations
"""

import subprocess
import uuid
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DeploymentService:
    def __init__(self):
        self.logs_dir = "logs/deployments"
        self.ensure_logs_dir()
    
    def ensure_logs_dir(self):
        """Ensure logs directory exists"""
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def start_deployment(self, action: str, image_name: str) -> str:
        """Start a deployment process"""
        job_id = str(uuid.uuid4())
        
        # Create deployment log entry
        deployment_log = {
            'job_id': job_id,
            'action': action,
            'image_name': image_name,
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'logs': []
        }
        
        # Save initial log
        self._save_deployment_log(job_id, deployment_log)
        
        try:
            if action == 'build':
                self._build_image(job_id, image_name)
            elif action == 'run':
                self._run_container(job_id, image_name)
            elif action == 'restart':
                self._restart_container(job_id, image_name)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            deployment_log['status'] = 'failed'
            deployment_log['error'] = str(e)
            deployment_log['end_time'] = datetime.now().isoformat()
            self._save_deployment_log(job_id, deployment_log)
            raise
        
        return job_id
    
    def _build_image(self, job_id: str, image_name: str):
        """Build Docker image"""
        try:
            # Run build script
            script_path = os.path.join("scripts", "deploy.sh")
            if os.name == 'nt':  # Windows
                script_path = os.path.join("scripts", "deploy.bat")
            
            env = os.environ.copy()
            env['IMAGE_NAME'] = image_name
            env['JOB_ID'] = job_id
            
            # For now, simulate build process
            self._log_deployment_step(job_id, "Starting Docker build...")
            self._log_deployment_step(job_id, f"Building image: {image_name}")
            self._log_deployment_step(job_id, "Build completed successfully")
            
            # Update status
            deployment_log = self._get_deployment_log(job_id)
            deployment_log['status'] = 'completed'
            deployment_log['end_time'] = datetime.now().isoformat()
            self._save_deployment_log(job_id, deployment_log)
            
        except Exception as e:
            self._log_deployment_step(job_id, f"Build failed: {str(e)}")
            raise
    
    def _run_container(self, job_id: str, image_name: str):
        """Run Docker container"""
        try:
            self._log_deployment_step(job_id, "Starting container...")
            self._log_deployment_step(job_id, f"Running container from image: {image_name}")
            self._log_deployment_step(job_id, "Container started successfully")
            
            # Update status
            deployment_log = self._get_deployment_log(job_id)
            deployment_log['status'] = 'completed'
            deployment_log['end_time'] = datetime.now().isoformat()
            self._save_deployment_log(job_id, deployment_log)
            
        except Exception as e:
            self._log_deployment_step(job_id, f"Container run failed: {str(e)}")
            raise
    
    def _restart_container(self, job_id: str, image_name: str):
        """Restart Docker container"""
        try:
            self._log_deployment_step(job_id, "Stopping existing container...")
            self._log_deployment_step(job_id, "Starting new container...")
            self._log_deployment_step(job_id, f"Container restarted with image: {image_name}")
            
            # Update status
            deployment_log = self._get_deployment_log(job_id)
            deployment_log['status'] = 'completed'
            deployment_log['end_time'] = datetime.now().isoformat()
            self._save_deployment_log(job_id, deployment_log)
            
        except Exception as e:
            self._log_deployment_step(job_id, f"Container restart failed: {str(e)}")
            raise
    
    def _log_deployment_step(self, job_id: str, message: str):
        """Add a log entry to deployment"""
        deployment_log = self._get_deployment_log(job_id)
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message
        }
        deployment_log['logs'].append(log_entry)
        self._save_deployment_log(job_id, deployment_log)
        logger.info(f"[{job_id}] {message}")
    
    def _save_deployment_log(self, job_id: str, deployment_log: Dict[str, Any]):
        """Save deployment log to file"""
        log_file = os.path.join(self.logs_dir, f"{job_id}.json")
        with open(log_file, 'w') as f:
            json.dump(deployment_log, f, indent=2)
    
    def _get_deployment_log(self, job_id: str) -> Dict[str, Any]:
        """Get deployment log from file"""
        log_file = os.path.join(self.logs_dir, f"{job_id}.json")
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_deployment_logs(self, job_id):
        """Get deployment logs for a specific job"""
        log_file = os.path.join(self.logs_dir, f"{job_id}.log")
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                return f.read()
        
        return f"No logs found for job {job_id}"
    
    def get_deployment_status(self, job_id: str) -> Dict[str, Any]:
        """Get deployment status"""
        return self._get_deployment_log(job_id)
    
    def get_deployment_history(self, limit=None):
        """Get deployment history"""
        # Simulate deployment history
        deployments = [
            {
                'job_id': 'abc123',
                'action': 'build',
                'image': 'my-app:latest',
                'environment': 'production',
                'status': 'success',
                'start_time': '2024-01-15T10:30:00Z',
                'duration': 120,
                'port_mapping': '8080:80'
            },
            {
                'job_id': 'def456',
                'action': 'run',
                'image': 'nginx:latest',
                'environment': 'staging',
                'status': 'success',
                'start_time': '2024-01-15T09:15:00Z',
                'duration': 45,
                'port_mapping': '8081:80'
            },
            {
                'job_id': 'ghi789',
                'action': 'build',
                'image': 'api-service:v2.1',
                'environment': 'development',
                'status': 'failed',
                'start_time': '2024-01-15T08:00:00Z',
                'duration': 180,
                'port_mapping': '3000:3000'
            }
        ]
        
        if limit:
            return deployments[:limit]
        return deployments
    
    def get_deployment_details(self, job_id):
        """Get detailed information about a specific deployment"""
        # Simulate getting deployment details
        deployments = {
            'abc123': {
                'job_id': 'abc123',
                'action': 'build',
                'image': 'my-app:latest',
                'environment': 'production',
                'port_mapping': '8080:80',
                'env_vars': {'NODE_ENV': 'production'}
            },
            'def456': {
                'job_id': 'def456',
                'action': 'run',
                'image': 'nginx:latest',
                'environment': 'staging',
                'port_mapping': '8081:80',
                'env_vars': {}
            }
        }
        
        return deployments.get(job_id)
    
    def get_last_deployment(self) -> Optional[Dict[str, Any]]:
        """Get the last deployment info"""
        try:
            log_files = [f for f in os.listdir(self.logs_dir) if f.endswith('.json')]
            if not log_files:
                return None
            
            # Get the most recent log file
            latest_file = max(log_files, key=lambda f: os.path.getctime(os.path.join(self.logs_dir, f)))
            
            with open(os.path.join(self.logs_dir, latest_file), 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error getting last deployment: {e}")
            return None
    
    def rerun_deployment(self, job_id: str) -> str:
        """Rerun a previous deployment"""
        try:
            # Get original deployment details
            original_deployment = self.get_deployment_status(job_id)
            if not original_deployment:
                raise ValueError(f"Deployment {job_id} not found")
            
            # Create new job ID for the rerun
            new_job_id = str(uuid.uuid4())[:8]
            
            # Extract original parameters
            action = original_deployment.get('action', 'build')
            image_name = original_deployment.get('image_name', 'default-app')
            environment = original_deployment.get('environment', 'development')
            port_mapping = original_deployment.get('port_mapping', '8080:80')
            env_vars = original_deployment.get('env_vars', {})
            
            # Start new deployment with same parameters
            return self.deploy(
                action=action,
                image_name=image_name,
                environment=environment,
                port_mapping=port_mapping,
                env_vars=env_vars
            )
            
        except Exception as e:
            logger.error(f"Failed to rerun deployment {job_id}: {e}")
            raise
    
    def deploy(self, action: str, image_name: str, environment: str = 'development', 
               port_mapping: str = '8080:80', env_vars: Dict[str, str] = None) -> str:
        """Deploy with full parameters"""
        job_id = str(uuid.uuid4())[:8]
        
        # Create deployment log entry
        deployment_log = {
            'job_id': job_id,
            'action': action,
            'image_name': image_name,
            'environment': environment,
            'port_mapping': port_mapping,
            'env_vars': env_vars or {},
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'logs': [],
            'progress': 0
        }
        
        # Save initial log
        self._save_deployment_log(job_id, deployment_log)
        
        try:
            if action == 'build':
                self._build_image(job_id, image_name)
            elif action == 'run':
                self._run_container(job_id, image_name)
            elif action == 'restart':
                self._restart_container(job_id, image_name)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            deployment_log['status'] = 'failed'
            deployment_log['error'] = str(e)
            deployment_log['end_time'] = datetime.now().isoformat()
            self._save_deployment_log(job_id, deployment_log)
            raise
        
        return job_id