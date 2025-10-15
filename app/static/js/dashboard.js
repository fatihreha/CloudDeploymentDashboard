// Dashboard JavaScript Functions

// Global variables
let charts = {};
let updateIntervals = {};
let socket = null;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    startAutoRefresh();
});

// Initialize dashboard components
function initializeDashboard() {
    console.log('Initializing dashboard...');
    
    // Initialize Socket.IO if available
    if (typeof io !== 'undefined') {
        initializeSocketIO();
    }
    
    // Load initial data
    loadDashboardData();
    
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
    
    // Add fade-in animation to cards
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('fade-in');
    });
}

// Setup event listeners
function setupEventListeners() {
    // Deployment form submission
    const deployForm = document.getElementById('deployForm');
    if (deployForm) {
        deployForm.addEventListener('submit', handleDeployment);
    }
    
    // Health check button
    const healthCheckBtn = document.getElementById('healthCheckBtn');
    if (healthCheckBtn) {
        healthCheckBtn.addEventListener('click', performHealthCheck);
    }
    
    // Refresh buttons
    document.querySelectorAll('.refresh-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const target = this.dataset.target;
            refreshData(target);
        });
    });
    
    // Log viewer auto-scroll toggle
    const logViewer = document.getElementById('logViewer');
    if (logViewer) {
        logViewer.addEventListener('scroll', function() {
            const isAtBottom = this.scrollTop + this.clientHeight >= this.scrollHeight - 10;
            this.dataset.autoScroll = isAtBottom;
        });
    }
}

// Initialize Socket.IO connection
function initializeSocketIO() {
    try {
        socket = io({
            transports: ['websocket', 'polling'],
            timeout: 5000,
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 5
        });
        
        socket.on('connect', function() {
            console.log('Connected to server');
            showNotification('Connected to server', 'success');
            updateConnectionStatus('connected');
            
            // Start monitoring when connected
            socket.emit('start_monitoring');
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from server');
            showNotification('Disconnected from server', 'warning');
            updateConnectionStatus('disconnected');
        });
        
        socket.on('connect_error', function(error) {
            console.error('Connection error:', error);
            showNotification('Connection error', 'error');
            updateConnectionStatus('error');
        });
        
        socket.on('reconnect', function() {
            console.log('Reconnected to server');
            showNotification('Reconnected to server', 'success');
            updateConnectionStatus('connected');
        });
        
        // Real-time system status updates
        socket.on('system_status', function(data) {
            console.log('Received system status update:', data);
            if (data && data.data) {
                updateSystemStatus(data.data);
                
                // Update charts with real-time data
                const timestamp = new Date(data.timestamp).toLocaleTimeString();
                updateChart('cpu', timestamp, data.data.cpu_usage || 0);
                updateChart('memory', timestamp, data.data.memory_usage || 0);
            }
        });
        
        // Real-time deployment metrics updates
        socket.on('deployment_metrics', function(data) {
            console.log('Received deployment metrics update:', data);
            if (data && data.data) {
                updateDeploymentMetrics(data.data);
            }
        });
        
        // Container stats updates
        socket.on('container_stats', function(data) {
            console.log('Received container stats update:', data);
            if (data && data.data) {
                updateContainerStats(data.data);
            }
        });
        
        // Health check results
        socket.on('health_check_result', function(data) {
            console.log('Received health check result:', data);
            if (data && data.data) {
                updateHealthCheckResults(data.data);
            }
        });
        
        // Deployment logs
        socket.on('deployment_logs', function(data) {
            console.log('Received deployment logs:', data);
            if (data && data.logs) {
                displayDeploymentLogs(data);
            }
        });
        
        // Deployment status updates
        socket.on('deployment_status_update', function(data) {
            console.log('Received deployment status update:', data);
            if (data) {
                updateDeploymentStatusDisplay(data);
            }
        });
        
    } catch (error) {
        console.error('Error initializing Socket.IO:', error);
        showNotification('Failed to initialize real-time connection', 'error');
        updateConnectionStatus('error');
     }
}
    
    // Real-time deployment updates
    socket.on('recent_deployments', function(data) {
        console.log('Received recent deployments update:', data);
        updateRecentDeployments(data.data);
    });
    
    // Container statistics updates
    socket.on('container_stats', function(data) {
        console.log('Received container stats update:', data);
        updateContainerStats(data.data);
    });
    
    // Real-time log streaming
    socket.on('deployment_logs', function(data) {
        console.log('Received deployment logs:', data);
        displayDeploymentLogs(data);
    });
    
    // New log entries
    socket.on('new_log', function(data) {
        console.log('Received new log entry:', data);
        appendLogEntry(data);
    });
    
    // Deployment status updates
    socket.on('deployment_status_update', function(data) {
        console.log('Received deployment status update:', data);
        updateDeploymentStatusDisplay(data);
    });
    
    // Health check results
    socket.on('health_check_result', function(data) {
        console.log('Received health check result:', data);
        updateHealthCheckResults(data.data);
    });
    
    // Notifications
    socket.on('notification', function(data) {
        console.log('Received notification:', data);
        showNotification(data.message, data.severity, data.title);
    });
    
    // Connection error handling
    socket.on('connect_error', function(error) {
        console.error('Socket.IO connection error:', error);
        showNotification('Connection error occurred', 'error');
    });
    
    socket.on('reconnect', function(attemptNumber) {
        console.log('Reconnected to server after', attemptNumber, 'attempts');
        showNotification('Reconnected to server', 'success');
    });
    
    socket.on('reconnect_error', function(error) {
        console.error('Socket.IO reconnection error:', error);
        showNotification('Reconnection failed', 'error');
    });
}

// Update connection status indicator
function updateConnectionStatus(status) {
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
        statusElement.className = 'connection-status';
        
        switch (status) {
            case 'connected':
                statusElement.classList.add('connected');
                statusElement.textContent = 'Connected';
                statusElement.title = 'Real-time connection active';
                break;
            case 'disconnected':
                statusElement.classList.add('disconnected');
                statusElement.textContent = 'Disconnected';
                statusElement.title = 'Real-time connection lost';
                break;
            case 'error':
                statusElement.classList.add('error');
                statusElement.textContent = 'Connection Error';
                statusElement.title = 'Failed to establish connection';
                break;
            default:
                statusElement.classList.add('connecting');
                statusElement.textContent = 'Connecting...';
                statusElement.title = 'Establishing connection';
        }
    }
}

// Load dashboard data
async function loadDashboardData() {
    try {
        // Load system status
        try {
            const statusResponse = await fetch('/api/status');
            if (statusResponse.ok) {
                const statusData = await statusResponse.json();
                if (statusData) {
                    updateSystemStatus(statusData);
                }
            } else {
                console.warn('Failed to load system status:', statusResponse.status);
            }
        } catch (error) {
            console.error('Error loading system status:', error);
        }
        
        // Load deployment metrics
        try {
            const metricsResponse = await fetch('/api/deployment-metrics');
            if (metricsResponse.ok) {
                const metricsData = await metricsResponse.json();
                if (metricsData) {
                    updateDeploymentMetrics(metricsData);
                }
            } else {
                console.warn('Failed to load deployment metrics:', metricsResponse.status);
            }
        } catch (error) {
            console.error('Error loading deployment metrics:', error);
        }
        
        // Load recent deployments
        try {
            const deploymentsResponse = await fetch('/api/deployments/recent');
            if (deploymentsResponse.ok) {
                const deploymentsData = await deploymentsResponse.json();
                if (deploymentsData) {
                    updateRecentDeployments(deploymentsData);
                }
            } else {
                console.warn('Failed to load recent deployments:', deploymentsResponse.status);
            }
        } catch (error) {
            console.error('Error loading recent deployments:', error);
        }

        // Load container stats
        try {
            const containersResponse = await fetch('/api/containers');
            if (containersResponse.ok) {
                const containersData = await containersResponse.json();
                if (containersData) {
                    updateContainerStats(containersData);
                }
            } else {
                console.warn('Failed to load container stats:', containersResponse.status);
            }
        } catch (error) {
            console.error('Error loading container stats:', error);
        }

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Error loading dashboard data', 'error');
    }
}

// Update system status display
function updateSystemStatus(data) {
    if (!data) {
        console.warn('No data provided to updateSystemStatus');
        return;
    }
    
    // Update CPU usage
    const cpuElement = document.getElementById('cpuUsage');
    if (cpuElement) {
        const cpuUsage = data.cpu_usage || 0;
        cpuElement.textContent = `${cpuUsage}%`;
        updateProgressBar('cpuProgress', cpuUsage);
    }
    
    // Update Memory usage
    const memoryElement = document.getElementById('memoryUsage');
    if (memoryElement) {
        const memoryUsage = data.memory_usage || 0;
        memoryElement.textContent = `${memoryUsage}%`;
        updateProgressBar('memoryProgress', memoryUsage);
    }
    
    // Update Disk usage
    const diskElement = document.getElementById('diskUsage');
    if (diskElement) {
        const diskUsage = data.disk_usage || 0;
        diskElement.textContent = `${diskUsage}%`;
        updateProgressBar('diskProgress', diskUsage);
    }
    
    // Update container count
    const containerElement = document.getElementById('containerCount');
    if (containerElement) {
        containerElement.textContent = data.active_containers || 0;
    }
    
    // Update network stats if available
    const networkElement = document.getElementById('networkStats');
    if (networkElement && data.network_stats) {
        networkElement.textContent = `${data.network_stats.bytes_sent || 0} / ${data.network_stats.bytes_recv || 0}`;
    }
}

// Update deployment metrics
function updateDeploymentMetrics(data) {
    const elements = {
        'totalDeployments': data.total_deployments,
        'successfulDeployments': data.successful_deployments,
        'failedDeployments': data.failed_deployments,
        'successRate': `${data.success_rate}%`
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

// Update recent deployments table
function updateRecentDeployments(deployments) {
    const tbody = document.getElementById('recentDeploymentsTable');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    deployments.forEach(deployment => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${deployment.id}</td>
            <td>${deployment.image}</td>
            <td><span class="status-badge status-${deployment.status.toLowerCase()}">${deployment.status}</span></td>
            <td>${new Date(deployment.timestamp).toLocaleString()}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewDeploymentDetails('${deployment.id}')">
                    <i class="fas fa-eye"></i> View
                </button>
                <button class="btn btn-sm btn-outline-success" onclick="rerunDeployment('${deployment.id}')">
                    <i class="fas fa-redo"></i> Rerun
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Update progress bar
function updateProgressBar(id, percentage) {
    if (!id) {
        console.warn('No ID provided to updateProgressBar');
        return;
    }
    
    const progressBar = document.getElementById(id);
    if (progressBar) {
        // Ensure percentage is a valid number between 0 and 100
        const validPercentage = Math.max(0, Math.min(100, parseFloat(percentage) || 0));
        
        progressBar.style.width = `${validPercentage}%`;
        progressBar.setAttribute('aria-valuenow', validPercentage);
        
        // Change color based on percentage
        progressBar.className = 'progress-bar';
        if (validPercentage > 80) {
            progressBar.classList.add('bg-danger');
        } else if (validPercentage > 60) {
            progressBar.classList.add('bg-warning');
        } else {
            progressBar.classList.add('bg-success');
        }
    } else {
        console.warn(`Progress bar element with ID '${id}' not found`);
    }
}

// Handle deployment form submission
async function handleDeployment(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const deploymentData = {
        action: formData.get('action'),
        image: formData.get('image'),
        environment: formData.get('environment'),
        port_mapping: formData.get('port_mapping'),
        env_vars: formData.get('env_vars')
    };
    
    try {
        showLoadingSpinner('deployBtn');
        
        const response = await fetch('/api/deploy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(deploymentData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('Deployment started successfully', 'success');
            // Redirect to monitoring page or update UI
            if (result.job_id) {
                window.location.href = `/monitoring?job_id=${result.job_id}`;
            }
        } else {
            showNotification(`Deployment failed: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Deployment error:', error);
        showNotification('Deployment request failed', 'error');
    } finally {
        hideLoadingSpinner('deployBtn');
    }
}

// Perform health check
async function performHealthCheck() {
    try {
        showLoadingSpinner('healthCheckBtn');
        
        const response = await fetch('/api/health-check', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            updateHealthCheckResults(result);
            showNotification('Health check completed', 'success');
        } else {
            showNotification('Health check failed', 'error');
        }
        
    } catch (error) {
        console.error('Health check error:', error);
        showNotification('Health check request failed', 'error');
    } finally {
        hideLoadingSpinner('healthCheckBtn');
    }
}

// Update health check results
function updateHealthCheckResults(data) {
    const resultsContainer = document.getElementById('healthCheckResults');
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = '';
    
    Object.entries(data.checks).forEach(([check, result]) => {
        const statusClass = result.status === 'healthy' ? 'success' : 
                           result.status === 'warning' ? 'warning' : 'danger';
        
        const checkElement = document.createElement('div');
        checkElement.className = 'alert alert-' + statusClass;
        checkElement.innerHTML = `
            <strong>${check}:</strong> ${result.message}
            ${result.details ? `<br><small>${result.details}</small>` : ''}
        `;
        
        resultsContainer.appendChild(checkElement);
    });
}

// Initialize charts
function initializeCharts() {
    // CPU Usage Chart
    const cpuCtx = document.getElementById('cpuChart');
    if (cpuCtx) {
        charts.cpu = new Chart(cpuCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU Usage (%)',
                    data: [],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    // Memory Usage Chart
    const memoryCtx = document.getElementById('memoryChart');
    if (memoryCtx) {
        charts.memory = new Chart(memoryCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Memory Usage (%)',
                    data: [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

// Update chart data
function updateChart(chartName, label, value) {
    const chart = charts[chartName];
    if (!chart) return;
    
    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(value);
    
    // Keep only last 20 data points
    if (chart.data.labels.length > 20) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }
    
    chart.update();
}

// Append to log viewer
function appendToLogViewer(message) {
    const logViewer = document.getElementById('logViewer');
    if (!logViewer) return;
    
    logViewer.textContent += message + '\n';
    
    // Auto-scroll if enabled
    if (logViewer.dataset.autoScroll !== 'false') {
        logViewer.scrollTop = logViewer.scrollHeight;
    }
}

// Update container statistics
function updateContainerStats(containers) {
    const containersList = document.getElementById('containersList');
    if (!containersList) return;
    
    containersList.innerHTML = '';
    
    containers.forEach(container => {
        const containerElement = document.createElement('div');
        containerElement.className = 'container-item';
        containerElement.innerHTML = `
            <div class="container-info">
                <h6>${container.name || container.id}</h6>
                <p>Status: <span class="status-badge status-${container.status.toLowerCase()}">${container.status}</span></p>
                <p>CPU: ${container.cpu_usage || 0}% | Memory: ${container.memory_usage || 0}%</p>
            </div>
        `;
        containersList.appendChild(containerElement);
    });
}

// Display deployment logs
function displayDeploymentLogs(data) {
    const logViewer = document.getElementById('logViewer');
    if (!logViewer) return;
    
    logViewer.innerHTML = '';
    
    if (data.logs && Array.isArray(data.logs)) {
        data.logs.forEach(log => {
            appendLogEntry(log);
        });
    }
}

// Append single log entry
function appendLogEntry(logEntry) {
    const logViewer = document.getElementById('logViewer');
    if (!logViewer) return;
    
    const logElement = document.createElement('div');
    logElement.className = `log-entry log-${logEntry.level.toLowerCase()}`;
    logElement.innerHTML = `
        <span class="log-timestamp">[${new Date(logEntry.timestamp).toLocaleTimeString()}]</span>
        <span class="log-level">${logEntry.level}</span>
        <span class="log-message">${logEntry.message}</span>
    `;
    
    logViewer.appendChild(logElement);
    
    // Auto-scroll if enabled
    if (logViewer.dataset.autoScroll !== 'false') {
        logViewer.scrollTop = logViewer.scrollHeight;
    }
}

// Update deployment status display
function updateDeploymentStatusDisplay(data) {
    const statusElement = document.getElementById(`deployment-status-${data.job_id}`);
    if (statusElement) {
        statusElement.textContent = data.status;
        statusElement.className = `status-badge status-${data.status.toLowerCase()}`;
    }
    
    const progressElement = document.getElementById(`deployment-progress-${data.job_id}`);
    if (progressElement && data.progress !== null) {
        progressElement.style.width = `${data.progress}%`;
        progressElement.setAttribute('aria-valuenow', data.progress);
    }
    
    // Show notification for status changes
    if (data.status === 'completed') {
        showNotification(`Deployment ${data.job_id} completed successfully`, 'success');
    } else if (data.status === 'failed') {
        showNotification(`Deployment ${data.job_id} failed`, 'error');
    }
}

// Join log streaming room
function joinLogStreaming(jobId) {
    if (socket) {
        socket.emit('join_logs', { job_id: jobId });
        console.log(`Joined log streaming for job ${jobId}`);
    }
}

// Leave log streaming room
function leaveLogStreaming(jobId) {
    if (socket) {
        socket.emit('leave_logs', { job_id: jobId });
        console.log(`Left log streaming for job ${jobId}`);
    }
}

// Start log streaming for deployment
async function startLogStreaming(jobId) {
    try {
        const response = await fetch(`/api/logs/stream/start/${jobId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            joinLogStreaming(jobId);
            showNotification('Log streaming started', 'success');
        } else {
            showNotification(`Failed to start log streaming: ${result.message}`, 'error');
        }
    } catch (error) {
        console.error('Error starting log streaming:', error);
        showNotification('Error starting log streaming', 'error');
    }
}

// Send test notification
async function sendTestNotification() {
    try {
        const response = await fetch('/api/notifications/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: 'test',
                title: 'Test Notification',
                message: 'This is a test notification from the dashboard',
                severity: 'info'
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            console.error('Failed to send test notification:', result.message);
        }
    } catch (error) {
        console.error('Error sending test notification:', error);
    }
}

// Show notification with enhanced features
function showNotification(message, type = 'info', title = null) {
    // Create notification container if it doesn't exist
    let notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const iconMap = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="${iconMap[type] || iconMap.info}"></i>
            <div class="notification-text">
                ${title ? `<div class="notification-title">${title}</div>` : ''}
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    notificationContainer.appendChild(notification);
    
    // Add animation
    setTimeout(() => {
        notification.classList.add('notification-show');
    }, 100);
    
    // Auto-remove notification after 5 seconds
    setTimeout(() => {
        notification.classList.remove('notification-show');
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }, 5000);
}

// Show loading spinner
function showLoadingSpinner(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="loading-spinner"></span> Loading...';
    }
}

// Hide loading spinner
function hideLoadingSpinner(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = false;
        // Restore original text (you might want to store this)
        button.innerHTML = button.dataset.originalText || 'Submit';
    }
}

// Start auto-refresh
function startAutoRefresh() {
    // Refresh system status every 5 seconds
    updateIntervals.status = setInterval(() => {
        loadDashboardData();
    }, 5000);
    
    // Update charts every 10 seconds
    updateIntervals.charts = setInterval(() => {
        if (Object.keys(charts).length > 0) {
            const now = new Date().toLocaleTimeString();
            // Simulate data updates (replace with real API calls)
            updateChart('cpu', now, Math.random() * 100);
            updateChart('memory', now, Math.random() * 100);
        }
    }, 10000);
}

// Stop auto-refresh
function stopAutoRefresh() {
    Object.values(updateIntervals).forEach(interval => {
        clearInterval(interval);
    });
    updateIntervals = {};
}

// Refresh specific data
async function refreshData(target) {
    switch (target) {
        case 'status':
            loadDashboardData();
            break;
        case 'logs':
            await loadLogs();
            break;
        case 'health':
            await performHealthCheck();
            break;
        default:
            loadDashboardData();
    }
}

// Load logs
async function loadLogs() {
    try {
        const response = await fetch('/api/logs');
        if (response.ok) {
            const logs = await response.text();
            const logViewer = document.getElementById('logViewer');
            if (logViewer) {
                logViewer.textContent = logs;
                logViewer.scrollTop = logViewer.scrollHeight;
            }
        }
    } catch (error) {
        console.error('Error loading logs:', error);
        showNotification('Error loading logs', 'error');
    }
}

// View deployment details
function viewDeploymentDetails(deploymentId) {
    window.location.href = `/deployment/${deploymentId}`;
}

// Rerun deployment
async function rerunDeployment(deploymentId) {
    if (!confirm('Are you sure you want to rerun this deployment?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/deployments/${deploymentId}/rerun`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('Deployment rerun started', 'success');
            if (result.job_id) {
                window.location.href = `/monitoring?job_id=${result.job_id}`;
            }
        } else {
            showNotification(`Rerun failed: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Rerun error:', error);
        showNotification('Rerun request failed', 'error');
    }
}

// Cleanup when page unloads
window.addEventListener('beforeunload', function() {
    stopAutoRefresh();
    if (socket) {
        socket.disconnect();
    }
});