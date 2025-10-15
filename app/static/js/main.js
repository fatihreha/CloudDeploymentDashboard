// Cloud Deployment Dashboard Main JavaScript

// Global variables
let socket = null;
let dashboardCharts = {};
let autoRefresh = true;
let refreshInterval = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize Socket.IO connection
    initializeSocket();
    
    // Initialize sidebar toggle
    initializeSidebar();
    
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Initialize auto-refresh
    initializeAutoRefresh();
    
    // Initialize page-specific functionality
    initializePageSpecific();
    
    // Initialize flash message auto-hide
    initializeFlashMessages();
    
    console.log('Cloud Deployment Dashboard initialized successfully');
}

// Socket.IO initialization
function initializeSocket() {
    if (typeof io !== 'undefined') {
        socket = io();
        
        // Connection events
        socket.on('connect', function() {
            console.log('Connected to server');
            updateConnectionStatus(true);
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from server');
            updateConnectionStatus(false);
        });
        
        // Global event listeners
        socket.on('deployment_update', function(data) {
            handleDeploymentUpdate(data);
        });
        
        socket.on('system_update', function(data) {
            handleSystemUpdate(data);
        });
        
        socket.on('log_update', function(data) {
            handleLogUpdate(data);
        });
        
        socket.on('health_update', function(data) {
            handleHealthUpdate(data);
        });
        
        socket.on('error', function(error) {
            console.error('Socket error:', error);
            showNotification('Connection error occurred', 'error');
        });
    } else {
        console.warn('Socket.IO not available');
    }
}

// Sidebar functionality
function initializeSidebar() {
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebarToggle && sidebar && mainContent) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
            
            // Save sidebar state to localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
        
        // Restore sidebar state from localStorage
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (sidebarCollapsed) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('expanded');
        }
    }
    
    // Highlight active navigation item
    highlightActiveNavItem();
}

function highlightActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Bootstrap components initialization
function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Auto-refresh functionality
function initializeAutoRefresh() {
    const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
    
    if (autoRefreshToggle) {
        autoRefreshToggle.addEventListener('change', function() {
            autoRefresh = this.checked;
            if (autoRefresh) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        });
    }
    
    // Start auto-refresh by default
    if (autoRefresh) {
        startAutoRefresh();
    }
}

function startAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    refreshInterval = setInterval(function() {
        if (autoRefresh) {
            refreshPageData();
        }
    }, 30000); // Refresh every 30 seconds
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

function refreshPageData() {
    const currentPage = getCurrentPage();
    
    switch (currentPage) {
        case 'dashboard':
            refreshDashboardData();
            break;
        case 'deployment':
            refreshDeploymentData();
            break;
        case 'monitoring':
            refreshMonitoringData();
            break;
        case 'health':
            refreshHealthData();
            break;
    }
}

function getCurrentPage() {
    const path = window.location.pathname;
    if (path === '/' || path === '/dashboard') return 'dashboard';
    if (path === '/deployment') return 'deployment';
    if (path === '/monitoring') return 'monitoring';
    if (path === '/health') return 'health';
    return 'unknown';
}

// Page-specific initialization
function initializePageSpecific() {
    const currentPage = getCurrentPage();
    
    switch (currentPage) {
        case 'dashboard':
            initializeDashboard();
            break;
        case 'deployment':
            initializeDeployment();
            break;
        case 'monitoring':
            initializeMonitoring();
            break;
        case 'health':
            initializeHealth();
            break;
    }
}

// Dashboard specific functions
function initializeDashboard() {
    // Initialize dashboard charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeDashboardCharts();
    }
    
    // Load initial dashboard data
    refreshDashboardData();
}

function initializeDashboardCharts() {
    // CPU Usage Chart
    const cpuCtx = document.getElementById('cpu-chart');
    if (cpuCtx) {
        dashboardCharts.cpu = new Chart(cpuCtx, {
            type: 'doughnut',
            data: {
                labels: ['Used', 'Free'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#e74a3b', '#f8f9fc'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Memory Usage Chart
    const memoryCtx = document.getElementById('memory-chart');
    if (memoryCtx) {
        dashboardCharts.memory = new Chart(memoryCtx, {
            type: 'doughnut',
            data: {
                labels: ['Used', 'Free'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#f6c23e', '#f8f9fc'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Disk Usage Chart
    const diskCtx = document.getElementById('disk-chart');
    if (diskCtx) {
        dashboardCharts.disk = new Chart(diskCtx, {
            type: 'doughnut',
            data: {
                labels: ['Used', 'Free'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#36b9cc', '#f8f9fc'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

function refreshDashboardData() {
    // Fetch dashboard data
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            updateDashboardStats(data);
            updateDashboardCharts(data);
        })
        .catch(error => {
            console.error('Error fetching dashboard data:', error);
        });
    
    // Fetch recent deployments
    fetch('/api/deployments/recent')
        .then(response => response.json())
        .then(data => {
            updateRecentDeployments(data);
        })
        .catch(error => {
            console.error('Error fetching recent deployments:', error);
        });
}

function updateDashboardStats(data) {
    // Update stats cards
    updateElement('total-deployments', data.total_deployments || 0);
    updateElement('success-rate', (data.success_rate || 0) + '%');
    updateElement('active-containers', data.active_containers || 0);
    updateElement('system-health', data.system_health || 'Unknown');
}

function updateDashboardCharts(data) {
    if (dashboardCharts.cpu && data.cpu_usage !== undefined) {
        dashboardCharts.cpu.data.datasets[0].data = [data.cpu_usage, 100 - data.cpu_usage];
        dashboardCharts.cpu.update();
    }
    
    if (dashboardCharts.memory && data.memory_usage !== undefined) {
        dashboardCharts.memory.data.datasets[0].data = [data.memory_usage, 100 - data.memory_usage];
        dashboardCharts.memory.update();
    }
    
    if (dashboardCharts.disk && data.disk_usage !== undefined) {
        dashboardCharts.disk.data.datasets[0].data = [data.disk_usage, 100 - data.disk_usage];
        dashboardCharts.disk.update();
    }
}

function updateRecentDeployments(deployments) {
    const tbody = document.getElementById('recent-deployments-tbody');
    if (!tbody) return;
    
    if (!deployments || deployments.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    No recent deployments found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = deployments.map(deployment => `
        <tr>
            <td>${deployment.job_id}</td>
            <td>${deployment.action}</td>
            <td>${deployment.image}</td>
            <td>${getStatusBadge(deployment.status)}</td>
            <td>${formatDateTime(deployment.start_time)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewDeploymentLogs('${deployment.job_id}')">
                    <i class="bi bi-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Deployment specific functions
function initializeDeployment() {
    // Initialize deployment form
    const deploymentForm = document.getElementById('deployment-form');
    if (deploymentForm) {
        deploymentForm.addEventListener('submit', handleDeploymentSubmit);
    }
    
    // Load deployment history
    refreshDeploymentData();
}

function handleDeploymentSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const deploymentData = {
        action: formData.get('action'),
        image: formData.get('image'),
        environment: formData.get('environment'),
        port_mapping: formData.get('port_mapping'),
        env_vars: formData.get('env_vars')
    };
    
    // Submit deployment
    fetch('/api/deploy', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(deploymentData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Deployment started successfully', 'success');
            updateDeploymentStatus(data);
        } else {
            showNotification('Deployment failed: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error submitting deployment:', error);
        showNotification('Error submitting deployment', 'error');
    });
}

function refreshDeploymentData() {
    // Fetch deployment history
    fetch('/api/deployments')
        .then(response => response.json())
        .then(data => {
            updateDeploymentHistory(data);
        })
        .catch(error => {
            console.error('Error fetching deployment data:', error);
        });
}

// Monitoring specific functions
function initializeMonitoring() {
    // Load monitoring data
    refreshMonitoringData();
}

function refreshMonitoringData() {
    // Fetch system status
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            updateSystemInfo(data);
        })
        .catch(error => {
            console.error('Error fetching monitoring data:', error);
        });
    
    // Fetch container data
    fetch('/api/containers')
        .then(response => response.json())
        .then(data => {
            updateContainerList(data);
        })
        .catch(error => {
            console.error('Error fetching container data:', error);
        });
}

// Health specific functions
function initializeHealth() {
    // Load health data
    refreshHealthData();
}

function refreshHealthData() {
    // This will be implemented in the health.html template
    if (typeof runHealthCheck === 'function') {
        runHealthCheck();
    }
}

// Event handlers
function handleDeploymentUpdate(data) {
    updateDeploymentStatus(data);
    
    // Update deployment history if on deployment page
    if (getCurrentPage() === 'deployment') {
        refreshDeploymentData();
    }
    
    // Update dashboard stats if on dashboard
    if (getCurrentPage() === 'dashboard') {
        refreshDashboardData();
    }
}

function handleSystemUpdate(data) {
    updateSystemInfo(data);
    
    // Update dashboard charts if on dashboard
    if (getCurrentPage() === 'dashboard') {
        updateDashboardCharts(data);
    }
}

function handleLogUpdate(data) {
    updateLogDisplay(data);
}

function handleHealthUpdate(data) {
    // Update health status if on health page
    if (getCurrentPage() === 'health' && typeof updateHealthStatus === 'function') {
        updateHealthStatus(data);
    }
}

// Utility functions
function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function getStatusBadge(status) {
    const badges = {
        'running': '<span class="badge bg-primary">Running</span>',
        'success': '<span class="badge bg-success">Success</span>',
        'failed': '<span class="badge bg-danger">Failed</span>',
        'pending': '<span class="badge bg-warning">Pending</span>',
        'stopped': '<span class="badge bg-secondary">Stopped</span>'
    };
    return badges[status] || '<span class="badge bg-secondary">Unknown</span>';
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

function formatDuration(seconds) {
    if (!seconds) return 'N/A';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

function updateConnectionStatus(connected) {
    const statusIndicator = document.getElementById('connection-status');
    if (statusIndicator) {
        statusIndicator.className = `status-indicator ${connected ? 'success' : 'danger'}`;
        statusIndicator.title = connected ? 'Connected' : 'Disconnected';
    }
}

function updateDeploymentStatus(data) {
    const statusElement = document.getElementById('deployment-status');
    if (statusElement && data) {
        statusElement.innerHTML = `
            <div class="deployment-status ${data.status}">
                <h6>Job ID: ${data.job_id}</h6>
                <p>Action: ${data.action}</p>
                <p>Image: ${data.image}</p>
                <p>Status: ${getStatusBadge(data.status)}</p>
                ${data.progress ? `
                    <div class="progress mb-2">
                        <div class="progress-bar" role="progressbar" style="width: ${data.progress}%">
                            ${data.progress}%
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }
}

function updateLogDisplay(data) {
    const logElement = document.getElementById('deployment-logs');
    if (logElement && data) {
        logElement.textContent += data.message + '\n';
        logElement.scrollTop = logElement.scrollHeight;
    }
}

function updateSystemInfo(data) {
    // Update system information display
    if (data.cpu_usage !== undefined) {
        updateElement('cpu-usage', data.cpu_usage + '%');
    }
    if (data.memory_usage !== undefined) {
        updateElement('memory-usage', data.memory_usage + '%');
    }
    if (data.disk_usage !== undefined) {
        updateElement('disk-usage', data.disk_usage + '%');
    }
}

function updateContainerList(containers) {
    const containerList = document.getElementById('container-list');
    if (!containerList) return;
    
    if (!containers || containers.length === 0) {
        containerList.innerHTML = '<p class="text-muted">No containers found</p>';
        return;
    }
    
    containerList.innerHTML = containers.map(container => `
        <div class="container-card ${container.status}">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">${container.name}</h6>
                    <p class="mb-1 text-muted">${container.image}</p>
                    <small class="text-muted">ID: ${container.id.substring(0, 12)}</small>
                </div>
                <div class="text-end">
                    ${getStatusBadge(container.status)}
                    <div class="btn-group mt-2" role="group">
                        <button class="btn btn-sm btn-outline-primary" onclick="viewContainerLogs('${container.id}')">
                            <i class="bi bi-file-text"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="inspectContainer('${container.id}')">
                            <i class="bi bi-info-circle"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function updateDeploymentHistory(deployments) {
    const tbody = document.getElementById('deployment-history-tbody');
    if (!tbody) return;
    
    if (!deployments || deployments.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted">
                    No deployment history found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = deployments.map(deployment => `
        <tr>
            <td>${deployment.job_id}</td>
            <td>${deployment.action}</td>
            <td>${deployment.image}</td>
            <td>${deployment.environment}</td>
            <td>${getStatusBadge(deployment.status)}</td>
            <td>${formatDateTime(deployment.start_time)}</td>
            <td>${formatDuration(deployment.duration)}</td>
            <td>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-outline-primary" onclick="viewDeploymentLogs('${deployment.job_id}')">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="rerunDeployment('${deployment.job_id}')">
                        <i class="bi bi-arrow-clockwise"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Flash messages
function initializeFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert[data-auto-dismiss]');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const alert = new bootstrap.Alert(message);
            alert.close();
        }, 5000);
    });
}

// Action functions
function viewDeploymentLogs(jobId) {
    fetch(`/api/logs/${jobId}`)
        .then(response => response.json())
        .then(data => {
            // Show logs in modal or dedicated area
            showLogsModal(data.logs);
        })
        .catch(error => {
            console.error('Error fetching logs:', error);
            showNotification('Error fetching logs', 'error');
        });
}

function viewContainerLogs(containerId) {
    // Implement container logs viewing
    showNotification('Container logs feature coming soon', 'info');
}

function inspectContainer(containerId) {
    // Implement container inspection
    showNotification('Container inspection feature coming soon', 'info');
}

function rerunDeployment(jobId) {
    if (confirm('Are you sure you want to rerun this deployment?')) {
        fetch(`/api/deploy/${jobId}/rerun`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Deployment rerun started', 'success');
                refreshDeploymentData();
            } else {
                showNotification('Failed to rerun deployment: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error rerunning deployment:', error);
            showNotification('Error rerunning deployment', 'error');
        });
    }
}

function showLogsModal(logs) {
    // Create and show logs modal
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Deployment Logs</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="log-terminal">${logs || 'No logs available'}</div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Remove modal from DOM when hidden
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

// Export functions for global access
window.CloudDashboard = {
    refreshDashboardData,
    refreshDeploymentData,
    refreshMonitoringData,
    refreshHealthData,
    viewDeploymentLogs,
    viewContainerLogs,
    inspectContainer,
    rerunDeployment,
    showNotification,
    updateDeploymentStatus,
    updateLogDisplay
};