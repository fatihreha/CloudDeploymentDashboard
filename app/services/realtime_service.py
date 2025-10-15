"""
Real-time monitoring and streaming service
Handles WebSocket connections and live data streaming
"""

import threading
import time
import json
import logging
from datetime import datetime
from flask import request
from flask_socketio import emit, join_room, leave_room
from app.services.monitoring_service import MonitoringService
from app.services.deployment_service import DeploymentService

logger = logging.getLogger(__name__)

class RealtimeService:
    def __init__(self, socketio):
        self.socketio = socketio
        self.monitoring_service = MonitoringService()
        self.deployment_service = DeploymentService()
        self.active_connections = set()
        self.streaming_threads = {}
        self.is_running = False
        
        # Register Socket.IO event handlers
        self.register_handlers()
        
    def register_handlers(self):
        """Register Socket.IO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            logger.info(f"Client connected: {request.sid}")
            self.active_connections.add(request.sid)
            
            # Send initial data
            self.emit_system_status()
            self.emit_deployment_metrics()
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            logger.info(f"Client disconnected: {request.sid}")
            self.active_connections.discard(request.sid)
            
        @self.socketio.on('join_logs')
        def handle_join_logs(data):
            """Handle joining log streaming room"""
            job_id = data.get('job_id')
            if job_id:
                join_room(f"logs_{job_id}")
                logger.info(f"Client {request.sid} joined logs room for job {job_id}")
                
        @self.socketio.on('leave_logs')
        def handle_leave_logs(data):
            """Handle leaving log streaming room"""
            job_id = data.get('job_id')
            if job_id:
                leave_room(f"logs_{job_id}")
                logger.info(f"Client {request.sid} left logs room for job {job_id}")
                
        @self.socketio.on('start_monitoring')
        def handle_start_monitoring():
            """Start real-time monitoring"""
            if not self.is_running:
                self.start_monitoring()
                
        @self.socketio.on('stop_monitoring')
        def handle_stop_monitoring():
            """Stop real-time monitoring"""
            self.stop_monitoring()
            
    def start_monitoring(self):
        """Start real-time monitoring threads"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("Starting real-time monitoring")
        
        # Start system metrics monitoring
        self.streaming_threads['system_metrics'] = threading.Thread(
            target=self._stream_system_metrics,
            daemon=True
        )
        self.streaming_threads['system_metrics'].start()
        
        # Start deployment monitoring
        self.streaming_threads['deployments'] = threading.Thread(
            target=self._stream_deployment_updates,
            daemon=True
        )
        self.streaming_threads['deployments'].start()
        
        # Start container monitoring
        self.streaming_threads['containers'] = threading.Thread(
            target=self._stream_container_stats,
            daemon=True
        )
        self.streaming_threads['containers'].start()
        
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_running = False
        logger.info("Stopping real-time monitoring")
        
    def _stream_system_metrics(self):
        """Stream system metrics to connected clients"""
        while self.is_running:
            try:
                if self.active_connections:
                    self.emit_system_status()
                time.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.error(f"Error streaming system metrics: {e}")
                time.sleep(10)
                
    def _stream_deployment_updates(self):
        """Stream deployment updates to connected clients"""
        while self.is_running:
            try:
                if self.active_connections:
                    self.emit_deployment_metrics()
                    self.emit_recent_deployments()
                time.sleep(10)  # Update every 10 seconds
            except Exception as e:
                logger.error(f"Error streaming deployment updates: {e}")
                time.sleep(15)
                
    def _stream_container_stats(self):
        """Stream container statistics to connected clients"""
        while self.is_running:
            try:
                if self.active_connections:
                    self.emit_container_stats()
                time.sleep(15)  # Update every 15 seconds
            except Exception as e:
                logger.error(f"Error streaming container stats: {e}")
                time.sleep(20)
                
    def emit_system_status(self):
        """Emit current system status"""
        try:
            status = self.monitoring_service.get_system_status()
            self.socketio.emit('system_status', {
                'timestamp': datetime.now().isoformat(),
                'data': status
            })
        except Exception as e:
            logger.error(f"Error emitting system status: {e}")
            
    def emit_deployment_metrics(self):
        """Emit deployment metrics"""
        try:
            metrics = self.monitoring_service.get_deployment_metrics()
            self.socketio.emit('deployment_metrics', {
                'timestamp': datetime.now().isoformat(),
                'data': metrics
            })
        except Exception as e:
            logger.error(f"Error emitting deployment metrics: {e}")
            
    def emit_recent_deployments(self):
        """Emit recent deployments"""
        try:
            deployments = self.deployment_service.get_recent_deployments(limit=10)
            self.socketio.emit('recent_deployments', {
                'timestamp': datetime.now().isoformat(),
                'data': deployments
            })
        except Exception as e:
            logger.error(f"Error emitting recent deployments: {e}")
            
    def emit_container_stats(self):
        """Emit container statistics"""
        try:
            containers = self.monitoring_service.get_container_stats()
            self.socketio.emit('container_stats', {
                'timestamp': datetime.now().isoformat(),
                'data': containers
            })
        except Exception as e:
            logger.error(f"Error emitting container stats: {e}")
            
    def stream_deployment_logs(self, job_id):
        """Stream logs for a specific deployment"""
        def log_streamer():
            try:
                # Get existing logs first
                logs = self.monitoring_service.get_deployment_logs(job_id)
                if logs:
                    self.socketio.emit('deployment_logs', {
                        'job_id': job_id,
                        'logs': logs,
                        'timestamp': datetime.now().isoformat()
                    }, room=f"logs_{job_id}")
                
                # Stream new logs (simulated for demo)
                log_messages = [
                    "Starting deployment process...",
                    "Pulling Docker image...",
                    "Image pulled successfully",
                    "Creating container...",
                    "Container created with ID: abc123",
                    "Starting container...",
                    "Container started successfully",
                    "Running health checks...",
                    "Health checks passed",
                    "Deployment completed successfully"
                ]
                
                for i, message in enumerate(log_messages):
                    if not self.is_running:
                        break
                        
                    log_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'level': 'INFO',
                        'message': message,
                        'job_id': job_id
                    }
                    
                    self.socketio.emit('new_log', log_entry, room=f"logs_{job_id}")
                    time.sleep(2)  # Simulate real-time log generation
                    
            except Exception as e:
                logger.error(f"Error streaming logs for job {job_id}: {e}")
                
        # Start log streaming in a separate thread
        thread = threading.Thread(target=log_streamer, daemon=True)
        thread.start()
        self.streaming_threads[f"logs_{job_id}"] = thread
        
    def emit_notification(self, notification_type, title, message, severity='info'):
        """Emit notification to all connected clients"""
        try:
            notification = {
                'type': notification_type,
                'title': title,
                'message': message,
                'severity': severity,
                'timestamp': datetime.now().isoformat()
            }
            
            self.socketio.emit('notification', notification)
            logger.info(f"Notification sent: {title}")
            
        except Exception as e:
            logger.error(f"Error emitting notification: {e}")
            
    def emit_deployment_status_update(self, job_id, status, progress=None):
        """Emit deployment status update"""
        try:
            update = {
                'job_id': job_id,
                'status': status,
                'progress': progress,
                'timestamp': datetime.now().isoformat()
            }
            
            self.socketio.emit('deployment_status_update', update)
            logger.info(f"Deployment status update sent for job {job_id}: {status}")
            
        except Exception as e:
            logger.error(f"Error emitting deployment status update: {e}")
            
    def emit_health_check_result(self, result):
        """Emit health check result"""
        try:
            self.socketio.emit('health_check_result', {
                'timestamp': datetime.now().isoformat(),
                'data': result
            })
        except Exception as e:
            logger.error(f"Error emitting health check result: {e}")
            
    def get_connection_count(self):
        """Get number of active connections"""
        return len(self.active_connections)
        
    def broadcast_message(self, event, data):
        """Broadcast message to all connected clients"""
        try:
            self.socketio.emit(event, {
                'timestamp': datetime.now().isoformat(),
                'data': data
            })
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")

# Global instance (will be initialized in app.py)
realtime_service = None

def init_realtime_service(socketio):
    """Initialize the real-time service"""
    global realtime_service
    realtime_service = RealtimeService(socketio)
    return realtime_service

def get_realtime_service():
    """Get the real-time service instance"""
    return realtime_service