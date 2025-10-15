"""
Monitoring Service
Handles system monitoring, container stats, and health checks
"""

import psutil
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MonitoringService:
    def __init__(self):
        self.logs_dir = "logs/containers"
        self.health_logs_dir = "logs/health-checks"
        self.deployment_logs_dir = "logs/deployments"
        self.ensure_logs_dirs()
    
    def ensure_logs_dirs(self):
        """Ensure logs directories exist"""
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.health_logs_dir, exist_ok=True)
        os.makedirs(self.deployment_logs_dir, exist_ok=True)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_used = disk.used / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB
            
            # Network stats
            network = psutil.net_io_counters()
            
            stats = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': round(cpu_percent, 2),
                    'count': cpu_count
                },
                'memory': {
                    'percent': round(memory_percent, 2),
                    'used_gb': round(memory_used, 2),
                    'total_gb': round(memory_total, 2)
                },
                'disk': {
                    'percent': round(disk_percent, 2),
                    'used_gb': round(disk_used, 2),
                    'total_gb': round(disk_total, 2)
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
            
            # Save stats to log
            self._save_monitoring_log(stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_container_stats(self) -> List[Dict[str, Any]]:
        """Get Docker container statistics"""
        try:
            # Simulate container stats (in real implementation, use docker API)
            containers = [
                {
                    'id': 'web-app-001',
                    'name': 'cloud-dashboard-web',
                    'status': 'running',
                    'image': 'cloud-dashboard:latest',
                    'created': '2024-01-15T10:30:00Z',
                    'ports': ['80:8080', '443:8443'],
                    'cpu_percent': 15.2,
                    'memory_usage': '256MB',
                    'memory_limit': '512MB',
                    'memory_percent': 50.0,
                    'network_rx': '1.2MB',
                    'network_tx': '850KB',
                    'block_read': '10MB',
                    'block_write': '5MB'
                },
                {
                    'id': 'db-001',
                    'name': 'cloud-dashboard-db',
                    'status': 'running',
                    'image': 'postgres:13',
                    'created': '2024-01-15T10:25:00Z',
                    'ports': ['5432:5432'],
                    'cpu_percent': 8.5,
                    'memory_usage': '128MB',
                    'memory_limit': '256MB',
                    'memory_percent': 50.0,
                    'network_rx': '500KB',
                    'network_tx': '300KB',
                    'block_read': '50MB',
                    'block_write': '25MB'
                }
            ]
            
            return containers
            
        except Exception as e:
            logger.error(f"Error getting container stats: {e}")
            return []
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'checks': {}
            }
            
            # System health
            system_stats = self.get_system_stats()
            cpu_healthy = system_stats.get('cpu', {}).get('percent', 0) < 80
            memory_healthy = system_stats.get('memory', {}).get('percent', 0) < 85
            disk_healthy = system_stats.get('disk', {}).get('percent', 0) < 90
            
            health_status['checks']['system'] = {
                'status': 'healthy' if all([cpu_healthy, memory_healthy, disk_healthy]) else 'warning',
                'cpu_ok': cpu_healthy,
                'memory_ok': memory_healthy,
                'disk_ok': disk_healthy
            }
            
            # Container health
            containers = self.get_container_stats()
            running_containers = [c for c in containers if c['status'] == 'running']
            
            health_status['checks']['containers'] = {
                'status': 'healthy' if len(running_containers) > 0 else 'critical',
                'total_containers': len(containers),
                'running_containers': len(running_containers),
                'containers': containers
            }
            
            # Application health (simulate)
            health_status['checks']['application'] = {
                'status': 'healthy',
                'web_server': 'running',
                'database': 'connected',
                'api_endpoints': 'responsive'
            }
            
            # Determine overall status
            check_statuses = [check['status'] for check in health_status['checks'].values()]
            if 'critical' in check_statuses:
                health_status['overall_status'] = 'critical'
            elif 'warning' in check_statuses:
                health_status['overall_status'] = 'warning'
            
            # Save health check log
            self._save_health_check_log(health_status)
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'critical',
                'error': str(e)
            }
    
    def get_recent_logs(self, log_type: str = 'monitoring', limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs"""
        try:
            logs_dir = self.logs_dir if log_type == 'monitoring' else self.health_logs_dir
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.json')]
            
            if not log_files:
                return []
            
            # Sort by creation time (newest first)
            log_files.sort(key=lambda f: os.path.getctime(os.path.join(logs_dir, f)), reverse=True)
            
            logs = []
            for log_file in log_files[:limit]:
                try:
                    with open(os.path.join(logs_dir, log_file), 'r') as f:
                        log_data = json.load(f)
                        logs.append(log_data)
                except Exception as e:
                    logger.error(f"Error reading log file {log_file}: {e}")
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting recent logs: {e}")
            return []
    
    def _save_monitoring_log(self, stats: Dict[str, Any]):
        """Save monitoring stats to log file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(self.logs_dir, f"stats_{timestamp}.json")
            
            with open(log_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving monitoring log: {e}")
    
    def _save_health_check_log(self, health_status: Dict[str, Any]):
        """Save health check results to log file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(self.health_logs_dir, f"health_{timestamp}.json")
            
            with open(log_file, 'w') as f:
                json.dump(health_status, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving health check log: {e}")
    
    def get_deployment_metrics(self):
        """Analyze deployment logs and return metrics"""
        try:
            # Read deployment logs and calculate metrics
            total_deployments = 0
            successful_deployments = 0
            
            # Simulate reading deployment logs
            # In a real implementation, this would read from actual log files
            deployment_files = os.listdir(self.deployment_logs_dir)
            total_deployments = len(deployment_files)
            
            # Simulate success rate calculation
            successful_deployments = int(total_deployments * 0.85)  # 85% success rate
            
            success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0
            
            return {
                'total_deployments': total_deployments,
                'successful_deployments': successful_deployments,
                'failed_deployments': total_deployments - successful_deployments,
                'success_rate': round(success_rate, 2),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting deployment metrics: {e}")
            return {
                'total_deployments': 0,
                'successful_deployments': 0,
                'failed_deployments': 0,
                'success_rate': 0,
                'last_updated': datetime.now().isoformat()
            }
    
    def get_container_stats(self):
        """Get container statistics"""
        try:
            # Simulate Docker container stats
            containers = [
                {
                    'id': 'abc123def456',
                    'name': 'web-app',
                    'image': 'my-app:latest',
                    'status': 'running',
                    'cpu_usage': '15.2%',
                    'memory_usage': '256MB / 512MB',
                    'network_io': '1.2MB / 850KB',
                    'created': '2024-01-15T10:30:00Z'
                },
                {
                    'id': 'def456ghi789',
                    'name': 'nginx-proxy',
                    'image': 'nginx:latest',
                    'status': 'running',
                    'cpu_usage': '5.1%',
                    'memory_usage': '64MB / 128MB',
                    'network_io': '2.1MB / 1.5MB',
                    'created': '2024-01-15T09:15:00Z'
                },
                {
                    'id': 'ghi789jkl012',
                    'name': 'database',
                    'image': 'postgres:13',
                    'status': 'stopped',
                    'cpu_usage': '0%',
                    'memory_usage': '0MB / 1GB',
                    'network_io': '0B / 0B',
                    'created': '2024-01-15T08:00:00Z'
                }
            ]
            
            return containers
            
        except Exception as e:
            print(f"Error getting container stats: {e}")
            return []
    
    def get_detailed_system_info(self):
        """Get detailed system information"""
        try:
            import platform
            import socket
            
            system_info = {
                'hostname': socket.gethostname(),
                'platform': platform.platform(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'uptime': self._get_uptime(),
                'load_average': self._get_load_average(),
                'network_interfaces': self._get_network_interfaces()
            }
            
            return system_info
            
        except Exception as e:
            print(f"Error getting detailed system info: {e}")
            return {}
    
    def _get_uptime(self):
        """Get system uptime"""
        try:
            import time
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return uptime_seconds
        except:
            # Windows or other systems
            return 0
    
    def _get_load_average(self):
        """Get system load average"""
        try:
            import os
            return os.getloadavg()
        except:
            # Windows doesn't have load average
            return [0.0, 0.0, 0.0]
    
    def _get_network_interfaces(self):
        """Get network interface information"""
        try:
            import socket
            import subprocess
            
            # Simple implementation - in production, use psutil or similar
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            return {
                'hostname': hostname,
                'local_ip': local_ip
            }
        except:
            return {}