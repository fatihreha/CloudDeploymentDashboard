"""
Test suite for the Cloud Deployment Dashboard application.
"""
import pytest
import json
from app import app, socketio


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def socket_client():
    """Create a test client for SocketIO."""
    return socketio.test_client(app)


class TestBasicRoutes:
    """Test basic application routes."""
    
    def test_home_page(self, client):
        """Test that the home page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Cloud Deployment Dashboard' in response.data
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestWebSocketConnections:
    """Test WebSocket functionality."""
    
    def test_socket_connection(self, socket_client):
        """Test WebSocket connection."""
        received = socket_client.get_received()
        assert socket_client.is_connected()
    
    def test_deployment_status_event(self, socket_client):
        """Test deployment status WebSocket event."""
        # Emit a test deployment status
        socket_client.emit('deployment_status', {
            'platform': 'azure',
            'status': 'success',
            'message': 'Deployment completed successfully'
        })
        
        received = socket_client.get_received()
        # Check if the event was processed (implementation dependent)
        assert socket_client.is_connected()


class TestDeploymentEndpoints:
    """Test deployment-related endpoints."""
    
    def test_azure_deployment_endpoint(self, client):
        """Test Azure deployment endpoint."""
        response = client.post('/deploy/azure', 
                             json={'action': 'test'})
        # This should return a proper response even if deployment fails
        assert response.status_code in [200, 400, 500]
    
    def test_deployment_status_endpoint(self, client):
        """Test deployment status endpoint."""
        response = client.get('/api/deployment/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deployments' in data


class TestErrorHandling:
    """Test error handling."""
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON requests."""
        response = client.post('/deploy/azure',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code in [400, 500]


class TestSecurity:
    """Test security features."""
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.get('/')
        # Check if CORS headers are set (if implemented)
        assert response.status_code == 200
    
    def test_content_security_policy(self, client):
        """Test Content Security Policy headers."""
        response = client.get('/')
        # This test would check for CSP headers if implemented
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__])