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
logger.info("MonitoringService module loaded!")

class MonitoringService:
    def __init__(self):
        self.logs_dir = 'logs/monitoring'
        self.health_logs_dir = 'logs/health'
        self.deployment_logs_dir = 'logs/deployments'
        self.ensure_logs_dirs()
        
        # Initialize database service
        try:
            from app.services.database_service import DatabaseService
            self.db = DatabaseService()
        except Exception as e:
            logger.warning(f"Database service not available: {e}")
            self.db = None
    
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
        print("TEST: get_container_stats() called!")
        logger.info("get_container_stats() called - starting Docker container retrieval")
        
        try:
            import docker
            logger.info("Docker library imported successfully")
            
            client = docker.from_env()
            logger.info("Docker client created successfully")
            
            containers = []
            
            # Get all containers (including stopped ones)
            all_containers = client.containers.list(all=True)
            logger.info(f"Found {len(all_containers)} containers")
            
            for container in all_containers:
                try:
                    # Basic container info
                    container_info = {
                        'id': container.id[:12],
                        'name': container.name,
                        'status': container.status,
                        'image': container.image.tags[0] if container.image.tags else container.image.id[:12],
                        'created': container.attrs['Created'],
                        'cpu_usage': '0%',
                        'memory_usage': 'N/A',
                        'network_io': 'N/A'
                    }
                    
                    logger.info(f"Processing container: {container.name} (status: {container.status})")
                    
                    # Only get stats for running containers
                    if container.status == 'running':
                        try:
                            # Get container stats
                            stats = container.stats(stream=False)
                            
                            # Calculate CPU percentage
                            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
                            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                            cpu_percent = 0.0
                            if system_delta > 0 and cpu_delta > 0:
                                cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
                            
                            # Calculate memory usage
                            memory_usage = stats['memory_stats'].get('usage', 0)
                            memory_limit = stats['memory_stats'].get('limit', 0)
                            
                            # Calculate network I/O
                            network_rx = 0
                            network_tx = 0
                            if 'networks' in stats:
                                for interface in stats['networks'].values():
                                    network_rx += interface.get('rx_bytes', 0)
                                    network_tx += interface.get('tx_bytes', 0)
                            
                            # Update container info with stats
                            container_info.update({
                                'cpu_usage': f"{cpu_percent:.1f}%",
                                'memory_usage': f"{memory_usage / (1024*1024):.1f}MB / {memory_limit / (1024*1024):.1f}MB",
                                'network_io': f"{network_rx / (1024*1024):.1f}MB / {network_tx / (1024*1024):.1f}MB"
                            })
                            
                            logger.info(f"Stats retrieved for {container.name}: CPU {cpu_percent:.2f}%")
                            
                        except Exception as stats_error:
                            logger.warning(f"Error getting stats for running container {container.name}: {stats_error}")
                    
                    containers.append(container_info)
                    
                except Exception as e:
                    logger.warning(f"Error processing container {container.id}: {e}")
                    continue
            
            logger.info(f"Successfully retrieved stats for {len(containers)} containers")
            return containers
            
        except docker.errors.DockerException as e:
            logger.error(f"Docker daemon connection error: {e}")
            return {
                'error': 'Docker daemon not available',
                'message': 'Please ensure Docker is running',
                'containers': []
            }
        except Exception as e:
            logger.error(f"Unexpected error getting container stats: {e}")
            return {
                'error': 'Failed to retrieve container statistics',
                'message': str(e),
                'containers': []
            }
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            import requests
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
                'message': f"CPU: {system_stats.get('cpu', {}).get('percent', 0):.1f}%, Memory: {system_stats.get('memory', {}).get('percent', 0):.1f}%, Disk: {system_stats.get('disk', {}).get('percent', 0):.1f}%",
                'cpu_ok': cpu_healthy,
                'memory_ok': memory_healthy,
                'disk_ok': disk_healthy
            }
            
            # Web server health
            web_server_healthy = True
            try:
                response = requests.get('http://localhost:5000/health', timeout=5)
                web_server_healthy = response.status_code == 200
            except:
                web_server_healthy = False
            
            health_status['checks']['web_server'] = {
                'status': 'healthy' if web_server_healthy else 'critical',
                'message': 'Web server is responding' if web_server_healthy else 'Web server is not responding'
            }
            
            # Database health
            database_healthy = True
            try:
                # Try to connect to PostgreSQL
                import psycopg2
                conn = psycopg2.connect(
                    host='localhost',
                    port=5432,
                    database='postgres',
                    user='postgres',
                    password='postgres'
                )
                conn.close()
            except:
                database_healthy = False
            
            health_status['checks']['database'] = {
                'status': 'healthy' if database_healthy else 'critical',
                'message': 'Database connection successful' if database_healthy else 'Database connection failed'
            }
            
            # API endpoints health
            api_healthy = True
            try:
                response = requests.get('http://localhost:5000/api/status', timeout=5)
                api_healthy = response.status_code == 200
            except:
                api_healthy = False
            
            health_status['checks']['api_endpoints'] = {
                'status': 'healthy' if api_healthy else 'critical',
                'message': 'API endpoints are responsive' if api_healthy else 'API endpoints are not responding'
            }
            
            # Container health
            containers = self.get_container_stats()
            running_containers = [c for c in containers if c['status'] == 'running']
            
            health_status['checks']['containers'] = {
                'status': 'healthy' if len(running_containers) > 0 else 'warning',
                'message': f"{len(running_containers)} of {len(containers)} containers running",
                'total_containers': len(containers),
                'running_containers': len(running_containers)
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
                'error': str(e),
                'checks': {
                    'system': {'status': 'critical', 'message': f'Health check failed: {str(e)}'},
                    'web_server': {'status': 'critical', 'message': 'Unable to check web server'},
                    'database': {'status': 'critical', 'message': 'Unable to check database'},
                    'api_endpoints': {'status': 'critical', 'message': 'Unable to check API endpoints'},
                    'containers': {'status': 'critical', 'message': 'Unable to check containers'}
                }
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
        """Save monitoring stats to database and log file"""
        try:
            # Save to database if available
            if self.db:
                metrics_data = {
                    'cpu_usage': stats['cpu']['percent'],
                    'memory_usage': stats['memory']['percent'],
                    'disk_usage': stats['disk']['percent'],
                    'network_io': stats['network'],
                    'active_containers': len(self.get_container_stats())
                }
                self.db.save_system_metrics(metrics_data)
            
            # Also save to log file as backup
            log_file = os.path.join(self.logs_dir, f"monitoring_{datetime.now().strftime('%Y%m%d')}.log")
            with open(log_file, 'a') as f:
                f.write(json.dumps(stats) + '\n')
        except Exception as e:
            logger.error(f"Error saving monitoring log: {e}")
    
    def _save_health_check_log(self, health_status: Dict[str, Any]):
        """Save health check results to database and log file"""
        try:
            # Save to database if available
            if self.db:
                self.db.save_health_check(health_status)
            
            # Also save to log file as backup
            log_file = os.path.join(self.health_logs_dir, f"health_{datetime.now().strftime('%Y%m%d')}.log")
            with open(log_file, 'a') as f:
                f.write(json.dumps(health_status) + '\n')
        except Exception as e:
            logger.error(f"Error saving health check log: {e}")
    
    def get_deployment_metrics(self):
        """Get deployment metrics from database"""
        try:
            if self.db:
                # Get metrics from database
                metrics = self.db.get_deployment_metrics()
                metrics['last_updated'] = datetime.now().isoformat()
                return metrics
            else:
                # Fallback to simulated data if database is not available
                return {
                    'total_deployments': 5,
                    'successful_deployments': 4,
                    'failed_deployments': 1,
                    'success_rate': 80.0,
                    'recent_deployments': [],
                    'last_updated': datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error getting deployment metrics: {e}")
            return {
                'total_deployments': 0,
                'successful_deployments': 0,
                'failed_deployments': 0,
                'success_rate': 0,
                'recent_deployments': [],
                'last_updated': datetime.now().isoformat()
            }
    

    
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