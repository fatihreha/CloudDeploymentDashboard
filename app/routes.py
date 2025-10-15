"""Cloud Deployment Automation Dashboard
Main routes and API endpoints
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, Response
from app.services.deployment_service import DeploymentService
from app.services.monitoring_service import MonitoringService
print("MonitoringService imported in routes.py!")
from app.services.health_service import HealthService
from app.services.database_service import DatabaseService
import uuid
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize services
deployment_service = DeploymentService()
monitoring_service = MonitoringService()
health_service = HealthService()

# Initialize database service (optional for testing)
try:
    database_service = DatabaseService()
except ValueError as e:
    print(f"Info: Database service not available: {e}")
    database_service = None

# Main routes
@main_bp.route('/')
@main_bp.route('/dashboard')
def dashboard():
    """Dashboard page with overview of system status"""
    return render_template('dashboard.html')

@main_bp.route('/deployment')
def deployment():
    """Deployment management page"""
    return render_template('deployment.html')

@main_bp.route('/monitoring')
def monitoring():
    """System monitoring page"""
    return render_template('monitoring.html')

@main_bp.route('/health')
def health():
    """Health check page"""
    return render_template('health.html')

# API routes
@api_bp.route('/deploy', methods=['POST'])
def deploy():
    """Deploy application or container"""
    try:
        data = request.get_json()
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())[:8]
        
        # Extract deployment parameters
        action = data.get('action', 'build')
        image_name = data.get('image', 'my-app')
        environment = data.get('environment', 'development')
        port_mapping = data.get('port_mapping', '8080:80')
        env_vars = data.get('env_vars', {})
        
        # Start deployment
        result = deployment_service.deploy(
            action=action,
            image_name=image_name,
            environment=environment,
            port_mapping=port_mapping,
            env_vars=env_vars
        )
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Deployment {action} started successfully',
            'status': 'running',
            'action': action,
            'image': image_name,
            'progress': 10
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/status')
def status():
    """Get system status and metrics"""
    try:
        # Get real system stats
        system_stats = monitoring_service.get_system_stats()
        
        # Get deployment metrics from database
        deployment_metrics = database_service.get_deployment_metrics() if database_service else {}
        
        # Get container stats
        container_stats = monitoring_service.get_container_stats()
        
        return jsonify({
            'cpu_usage': system_stats.get('cpu', {}).get('percent', 0),
            'memory_usage': system_stats.get('memory', {}).get('percent', 0),
            'disk_usage': system_stats.get('disk', {}).get('percent', 0),
            'network_io': system_stats.get('network', {}),
            'total_deployments': deployment_metrics.get('total_deployments', 0),
            'successful_deployments': deployment_metrics.get('successful_deployments', 0),
            'failed_deployments': deployment_metrics.get('failed_deployments', 0),
            'running_deployments': deployment_metrics.get('running_deployments', 0),
            'pending_deployments': deployment_metrics.get('pending_deployments', 0),
            'success_rate': deployment_metrics.get('success_rate', 0),
            'active_containers': len(container_stats),
            'system_health': 'healthy' if system_stats.get('cpu', {}).get('percent', 0) < 80 else 'warning',
            'timestamp': system_stats.get('timestamp')
        })
        
    except Exception as e:
        logger.error(f"Error in /api/status: {e}")
        return jsonify({
            'error': str(e)
        }), 500

@api_bp.route('/logs')
def all_logs():
    """Get all recent logs"""
    try:
        logs = monitoring_service.get_recent_logs()
        
        return Response(logs, mimetype='text/plain')
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api_bp.route('/logs/<job_id>')
def logs(job_id):
    """Get deployment logs for specific job"""
    try:
        logs = deployment_service.get_deployment_logs(job_id)
        
        return jsonify({
            'job_id': job_id,
            'logs': logs
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api_bp.route('/health-check', methods=['GET', 'POST'])
def health_check():
    """Perform comprehensive health check"""
    try:
        health_result = health_service.perform_health_check()
        
        return jsonify(health_result)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'overall_status': 'critical'
        }), 500

@api_bp.route('/deployment-status/<job_id>')
def deployment_status(job_id):
    """Get status of specific deployment"""
    try:
        status = deployment_service.get_deployment_status(job_id)
        
        return jsonify({
            'job_id': job_id,
            'status': status.get('status', 'unknown'),
            'progress': status.get('progress', 0),
            'message': status.get('message', ''),
            'start_time': status.get('start_time'),
            'end_time': status.get('end_time')
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api_bp.route('/deployment-metrics')
def deployment_metrics():
    """Get deployment metrics for dashboard"""
    try:
        # Get metrics from database
        metrics = database_service.get_deployment_metrics() if database_service else {}
        
        # Add recent deployments
        recent_deployments = database_service.get_deployments(limit=5) if database_service else []
        metrics['recent_deployments'] = recent_deployments
        metrics['last_updated'] = datetime.now().isoformat()
        
        return jsonify(metrics)
        
    except Exception as e:
        logger.error(f"Error in /api/deployment-metrics: {e}")
        return jsonify({
            'error': str(e)
        }), 500

@api_bp.route('/deployments')
def deployments():
    """Get deployment history"""
    try:
        # Get deployment history from service
        deployments = deployment_service.get_deployment_history()
        
        return jsonify(deployments)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api_bp.route('/deployments/recent')
def recent_deployments():
    """Get recent deployments for dashboard"""
    try:
        # Get recent deployments from database
        deployments = database_service.get_deployments(limit=10) if database_service else []
        
        return jsonify(deployments)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api_bp.route('/containers')
def containers():
    """Get container information"""
    print("TEST: /api/containers endpoint called!")
    try:
        containers_data = monitoring_service.get_container_stats()
        
        # Check if it's an error response
        if isinstance(containers_data, dict) and 'error' in containers_data:
            return jsonify(containers_data), 503  # Service Unavailable
        
        return jsonify(containers_data)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve container information',
            'message': str(e),
            'containers': []
        }), 500

@api_bp.route('/deploy/<job_id>/rerun', methods=['POST'])
def rerun_deployment(job_id):
    """Rerun a previous deployment"""
    try:
        # Get original deployment details
        original_deployment = deployment_service.get_deployment_details(job_id)
        
        if not original_deployment:
            return jsonify({
                'success': False,
                'message': 'Original deployment not found'
            }), 404
        
        # Generate new job ID
        new_job_id = str(uuid.uuid4())[:8]
        
        # Start new deployment with same parameters
        result = deployment_service.deploy(
            action=original_deployment.get('action'),
            image_name=original_deployment.get('image'),
            environment=original_deployment.get('environment'),
            port_mapping=original_deployment.get('port_mapping'),
            env_vars=original_deployment.get('env_vars', {})
        )
        
        return jsonify({
            'success': True,
            'job_id': new_job_id,
            'message': 'Deployment rerun started successfully',
            'original_job_id': job_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/system/info')
def system_info():
    """Get detailed system information"""
    try:
        system_info = monitoring_service.get_detailed_system_info()
        
        return jsonify(system_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api_bp.route('/logs/stream/<job_id>')
def stream_logs(job_id):
    """Stream logs for a deployment job"""
    try:
        def generate():
            # This would be implemented with Server-Sent Events
            # For now, return the current logs
            logs = deployment_service.get_deployment_logs(job_id)
            yield f"data: {json.dumps({'logs': logs})}\n\n"
        
        return Response(generate(), mimetype='text/plain')
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api_bp.route('/logs/stream/start/<job_id>', methods=['POST'])
def start_log_streaming(job_id):
    """Start real-time log streaming for a deployment"""
    try:
        from app.services.realtime_service import get_realtime_service
        
        realtime_service = get_realtime_service()
        if realtime_service:
            realtime_service.stream_deployment_logs(job_id)
            
            return jsonify({
                'success': True,
                'message': f'Log streaming started for job {job_id}',
                'job_id': job_id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Real-time service not available'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@api_bp.route('/notifications/send', methods=['POST'])
def send_notification():
    """Send notification to all connected clients"""
    try:
        from app.services.realtime_service import get_realtime_service
        
        data = request.get_json()
        notification_type = data.get('type', 'info')
        title = data.get('title', 'Notification')
        message = data.get('message', '')
        severity = data.get('severity', 'info')
        
        realtime_service = get_realtime_service()
        if realtime_service:
            realtime_service.emit_notification(notification_type, title, message, severity)
            
            return jsonify({
                'success': True,
                'message': 'Notification sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Real-time service not available'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500