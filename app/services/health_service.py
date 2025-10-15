"""
Health Service Module
Handles health checks and system status monitoring
"""

import os
import json
import psutil
import time
from datetime import datetime
from typing import Dict, Any, List


class HealthService:
    """Service for performing health checks and system monitoring"""
    
    def __init__(self):
        self.health_logs_dir = "logs/health-checks"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.health_logs_dir, exist_ok=True)
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            health_data = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'checks': {
                    'system': self._check_system_health(),
                    'application': self._check_application_health(),
                    'container': self._check_container_health(),
                    'network': self._check_network_health()
                }
            }
            
            # Determine overall status
            failed_checks = [
                check for check in health_data['checks'].values() 
                if check.get('status') == 'unhealthy'
            ]
            
            if failed_checks:
                health_data['overall_status'] = 'unhealthy'
            elif any(check.get('status') == 'warning' for check in health_data['checks'].values()):
                health_data['overall_status'] = 'warning'
            
            # Save health check log
            self._save_health_log(health_data)
            
            return health_data
            
        except Exception as e:
            error_data = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'unhealthy',
                'error': str(e),
                'checks': {}
            }
            return error_data
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Check system resource health"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Determine status
            status = 'healthy'
            issues = []
            
            if cpu_percent > 80:
                status = 'warning' if cpu_percent < 90 else 'unhealthy'
                issues.append(f'High CPU usage: {cpu_percent:.1f}%')
            
            if memory_percent > 80:
                status = 'warning' if memory_percent < 90 else 'unhealthy'
                issues.append(f'High memory usage: {memory_percent:.1f}%')
            
            if disk_percent > 85:
                status = 'warning' if disk_percent < 95 else 'unhealthy'
                issues.append(f'High disk usage: {disk_percent:.1f}%')
            
            return {
                'status': status,
                'cpu_usage': cpu_percent,
                'memory_usage': memory_percent,
                'disk_usage': disk_percent,
                'issues': issues,
                'details': {
                    'cpu_count': psutil.cpu_count(),
                    'memory_total': memory.total,
                    'memory_available': memory.available,
                    'disk_total': disk.total,
                    'disk_free': disk.free
                }
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'issues': ['Failed to check system health']
            }
    
    def _check_application_health(self) -> Dict[str, Any]:
        """Check application health"""
        try:
            # Check if Flask app is responding
            # This is a basic check - in production, you might check database connections, etc.
            
            status = 'healthy'
            issues = []
            
            # Check if required directories exist
            required_dirs = ['logs', 'logs/deployments', 'logs/containers', 'logs/health-checks']
            for dir_path in required_dirs:
                if not os.path.exists(dir_path):
                    status = 'warning'
                    issues.append(f'Missing directory: {dir_path}')
            
            # Check if application is running (basic check)
            current_process = psutil.Process()
            app_uptime = time.time() - current_process.create_time()
            
            return {
                'status': status,
                'uptime_seconds': app_uptime,
                'process_id': current_process.pid,
                'memory_usage_mb': current_process.memory_info().rss / 1024 / 1024,
                'cpu_percent': current_process.cpu_percent(),
                'issues': issues
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'issues': ['Failed to check application health']
            }
    
    def _check_container_health(self) -> Dict[str, Any]:
        """Check container health (simulated)"""
        try:
            # In a real implementation, this would check actual Docker containers
            # For now, we'll simulate container health checks
            
            containers = [
                {
                    'name': 'web-app',
                    'status': 'running',
                    'health': 'healthy'
                },
                {
                    'name': 'nginx-proxy',
                    'status': 'running',
                    'health': 'healthy'
                }
            ]
            
            unhealthy_containers = [c for c in containers if c['health'] != 'healthy']
            stopped_containers = [c for c in containers if c['status'] != 'running']
            
            status = 'healthy'
            issues = []
            
            if unhealthy_containers:
                status = 'unhealthy'
                issues.extend([f"Unhealthy container: {c['name']}" for c in unhealthy_containers])
            
            if stopped_containers:
                status = 'warning' if status == 'healthy' else status
                issues.extend([f"Stopped container: {c['name']}" for c in stopped_containers])
            
            return {
                'status': status,
                'total_containers': len(containers),
                'running_containers': len([c for c in containers if c['status'] == 'running']),
                'healthy_containers': len([c for c in containers if c['health'] == 'healthy']),
                'containers': containers,
                'issues': issues
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'issues': ['Failed to check container health']
            }
    
    def _check_network_health(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            import socket
            
            status = 'healthy'
            issues = []
            
            # Check if application port is available
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex(('localhost', 5000))
                sock.close()
                
                if result != 0:
                    status = 'warning'
                    issues.append('Application port 5000 is not accessible')
                
            except Exception as e:
                status = 'warning'
                issues.append(f'Port check failed: {str(e)}')
            
            # Get network interfaces
            network_interfaces = []
            try:
                for interface, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        if addr.family == socket.AF_INET:
                            network_interfaces.append({
                                'interface': interface,
                                'ip': addr.address,
                                'netmask': addr.netmask
                            })
            except Exception:
                pass
            
            return {
                'status': status,
                'network_interfaces': network_interfaces,
                'issues': issues
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'issues': ['Failed to check network health']
            }
    
    def _save_health_log(self, health_data: Dict[str, Any]):
        """Save health check log to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(self.health_logs_dir, f"health_check_{timestamp}.json")
            
            with open(log_file, 'w') as f:
                json.dump(health_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving health log: {e}")
    
    def get_health_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent health check history"""
        try:
            health_files = []
            
            if os.path.exists(self.health_logs_dir):
                for filename in os.listdir(self.health_logs_dir):
                    if filename.startswith('health_check_') and filename.endswith('.json'):
                        file_path = os.path.join(self.health_logs_dir, filename)
                        health_files.append((filename, file_path))
            
            # Sort by filename (which contains timestamp)
            health_files.sort(reverse=True)
            
            history = []
            for filename, file_path in health_files[:limit]:
                try:
                    with open(file_path, 'r') as f:
                        health_data = json.load(f)
                        history.append(health_data)
                except Exception as e:
                    print(f"Error reading health log {filename}: {e}")
            
            return history
            
        except Exception as e:
            print(f"Error getting health history: {e}")
            return []
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health metrics and statistics"""
        try:
            history = self.get_health_history(limit=50)
            
            if not history:
                return {
                    'total_checks': 0,
                    'healthy_checks': 0,
                    'warning_checks': 0,
                    'unhealthy_checks': 0,
                    'success_rate': 0,
                    'last_check': None
                }
            
            total_checks = len(history)
            healthy_checks = len([h for h in history if h.get('overall_status') == 'healthy'])
            warning_checks = len([h for h in history if h.get('overall_status') == 'warning'])
            unhealthy_checks = len([h for h in history if h.get('overall_status') == 'unhealthy'])
            
            success_rate = (healthy_checks / total_checks * 100) if total_checks > 0 else 0
            
            return {
                'total_checks': total_checks,
                'healthy_checks': healthy_checks,
                'warning_checks': warning_checks,
                'unhealthy_checks': unhealthy_checks,
                'success_rate': round(success_rate, 2),
                'last_check': history[0] if history else None
            }
            
        except Exception as e:
            print(f"Error getting health metrics: {e}")
            return {
                'total_checks': 0,
                'healthy_checks': 0,
                'warning_checks': 0,
                'unhealthy_checks': 0,
                'success_rate': 0,
                'last_check': None,
                'error': str(e)
            }