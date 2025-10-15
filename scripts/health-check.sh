#!/bin/bash

# Cloud Deployment Dashboard - Health Check Script
# This script performs comprehensive health checks on the application and infrastructure

set -e

# Configuration
APP_NAME="cloud-deployment-dashboard"
CONTAINER_NAME="$APP_NAME-container"
APP_URL="http://localhost:5000"
LOG_DIR="./logs/health-checks"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/health_check_$TIMESTAMP.log"

# Health check thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
DISK_THRESHOLD=85
RESPONSE_TIME_THRESHOLD=5000  # milliseconds

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Status counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Logging functions
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    ((FAILED_CHECKS++))
}

success() {
    echo -e "${GREEN}[PASS]${NC} $1" | tee -a "$LOG_FILE"
    ((PASSED_CHECKS++))
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
    ((WARNING_CHECKS++))
}

# Function to increment total checks
check_start() {
    ((TOTAL_CHECKS++))
}

# Function to check Docker daemon
check_docker_daemon() {
    check_start
    log "Checking Docker daemon status..."
    
    if docker info >/dev/null 2>&1; then
        success "Docker daemon is running"
    else
        error "Docker daemon is not running"
        return 1
    fi
}

# Function to check container status
check_container_status() {
    check_start
    log "Checking container status..."
    
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        success "Container '$CONTAINER_NAME' is running"
        
        # Get container stats
        local stats=$(docker stats --no-stream --format "table {{.CPUPerc}}\t{{.MemPerc}}" "$CONTAINER_NAME" 2>/dev/null | tail -n 1)
        if [ -n "$stats" ]; then
            log "Container stats: $stats"
        fi
    else
        error "Container '$CONTAINER_NAME' is not running"
        
        # Check if container exists but is stopped
        if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
            warning "Container exists but is stopped"
            log "Container logs (last 10 lines):"
            docker logs --tail 10 "$CONTAINER_NAME" 2>&1 | tee -a "$LOG_FILE"
        else
            error "Container does not exist"
        fi
        return 1
    fi
}

# Function to check application health endpoint
check_app_health() {
    check_start
    log "Checking application health endpoint..."
    
    local start_time=$(date +%s%3N)
    local response=$(curl -s -w "%{http_code}" -o /tmp/health_response "$APP_URL/api/health-check" 2>/dev/null || echo "000")
    local end_time=$(date +%s%3N)
    local response_time=$((end_time - start_time))
    
    if [ "$response" = "200" ]; then
        success "Health endpoint responded with HTTP 200"
        log "Response time: ${response_time}ms"
        
        if [ $response_time -gt $RESPONSE_TIME_THRESHOLD ]; then
            warning "Response time (${response_time}ms) exceeds threshold (${RESPONSE_TIME_THRESHOLD}ms)"
        fi
        
        # Check response content
        if [ -f /tmp/health_response ]; then
            local health_status=$(cat /tmp/health_response | grep -o '"status":"[^"]*"' | cut -d'"' -f4 2>/dev/null || echo "unknown")
            log "Health status: $health_status"
            rm -f /tmp/health_response
        fi
    else
        error "Health endpoint failed with HTTP $response"
        return 1
    fi
}

# Function to check system resources
check_system_resources() {
    check_start
    log "Checking system resources..."
    
    # Check CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 2>/dev/null || echo "0")
    if [ -n "$cpu_usage" ] && [ $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l 2>/dev/null || echo 0) -eq 1 ]; then
        warning "High CPU usage: ${cpu_usage}%"
    else
        success "CPU usage is normal: ${cpu_usage}%"
    fi
    
    # Check memory usage
    local memory_info=$(free | grep Mem)
    local total_mem=$(echo $memory_info | awk '{print $2}')
    local used_mem=$(echo $memory_info | awk '{print $3}')
    local memory_usage=$(echo "scale=1; $used_mem * 100 / $total_mem" | bc -l 2>/dev/null || echo "0")
    
    if [ $(echo "$memory_usage > $MEMORY_THRESHOLD" | bc -l 2>/dev/null || echo 0) -eq 1 ]; then
        warning "High memory usage: ${memory_usage}%"
    else
        success "Memory usage is normal: ${memory_usage}%"
    fi
    
    # Check disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    if [ $disk_usage -gt $DISK_THRESHOLD ]; then
        warning "High disk usage: ${disk_usage}%"
    else
        success "Disk usage is normal: ${disk_usage}%"
    fi
}

# Function to check network connectivity
check_network() {
    check_start
    log "Checking network connectivity..."
    
    # Check if application port is listening
    if netstat -tuln | grep -q ":5000 "; then
        success "Application port 5000 is listening"
    else
        error "Application port 5000 is not listening"
        return 1
    fi
    
    # Check external connectivity (optional)
    if ping -c 1 google.com >/dev/null 2>&1; then
        success "External network connectivity is working"
    else
        warning "External network connectivity check failed"
    fi
}

# Function to check application logs for errors
check_application_logs() {
    check_start
    log "Checking application logs for errors..."
    
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        local error_count=$(docker logs --since="1h" "$CONTAINER_NAME" 2>&1 | grep -i "error\|exception\|traceback" | wc -l)
        
        if [ $error_count -eq 0 ]; then
            success "No errors found in recent logs"
        elif [ $error_count -lt 5 ]; then
            warning "Found $error_count error(s) in recent logs"
        else
            error "Found $error_count error(s) in recent logs - investigate immediately"
            log "Recent errors:"
            docker logs --since="1h" "$CONTAINER_NAME" 2>&1 | grep -i "error\|exception\|traceback" | tail -5 | tee -a "$LOG_FILE"
        fi
    else
        error "Cannot check logs - container is not running"
        return 1
    fi
}

# Function to check database connectivity (if applicable)
check_database() {
    check_start
    log "Checking database connectivity..."
    
    # This is a placeholder - implement based on your database setup
    # For now, we'll just check if any database containers are running
    local db_containers=$(docker ps --filter "name=postgres\|mysql\|mongo\|redis" --format "{{.Names}}" | wc -l)
    
    if [ $db_containers -gt 0 ]; then
        success "Database container(s) are running"
    else
        warning "No database containers detected"
    fi
}

# Function to perform load test (basic)
check_load_performance() {
    check_start
    log "Performing basic load test..."
    
    # Simple load test with curl
    local success_count=0
    local total_requests=10
    
    for i in $(seq 1 $total_requests); do
        if curl -s -f "$APP_URL" >/dev/null 2>&1; then
            ((success_count++))
        fi
        sleep 0.1
    done
    
    local success_rate=$(echo "scale=1; $success_count * 100 / $total_requests" | bc -l)
    
    if [ $(echo "$success_rate >= 95" | bc -l) -eq 1 ]; then
        success "Load test passed: ${success_rate}% success rate"
    elif [ $(echo "$success_rate >= 80" | bc -l) -eq 1 ]; then
        warning "Load test warning: ${success_rate}% success rate"
    else
        error "Load test failed: ${success_rate}% success rate"
    fi
}

# Function to generate health report
generate_report() {
    log "Generating health check report..."
    
    echo "================================" | tee -a "$LOG_FILE"
    echo "HEALTH CHECK SUMMARY" | tee -a "$LOG_FILE"
    echo "================================" | tee -a "$LOG_FILE"
    echo "Timestamp: $(date)" | tee -a "$LOG_FILE"
    echo "Total Checks: $TOTAL_CHECKS" | tee -a "$LOG_FILE"
    echo "Passed: $PASSED_CHECKS" | tee -a "$LOG_FILE"
    echo "Warnings: $WARNING_CHECKS" | tee -a "$LOG_FILE"
    echo "Failed: $FAILED_CHECKS" | tee -a "$LOG_FILE"
    echo "================================" | tee -a "$LOG_FILE"
    
    local overall_status="HEALTHY"
    if [ $FAILED_CHECKS -gt 0 ]; then
        overall_status="CRITICAL"
    elif [ $WARNING_CHECKS -gt 0 ]; then
        overall_status="WARNING"
    fi
    
    echo "Overall Status: $overall_status" | tee -a "$LOG_FILE"
    echo "Log File: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "================================" | tee -a "$LOG_FILE"
    
    # Return appropriate exit code
    if [ "$overall_status" = "CRITICAL" ]; then
        return 1
    else
        return 0
    fi
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -h, --help       Show this help message"
    echo "  -q, --quick      Quick health check (basic checks only)"
    echo "  -f, --full       Full health check (all checks)"
    echo "  -c, --continuous Monitor continuously (every 30 seconds)"
    echo "  -r, --report     Generate detailed report"
    echo ""
    echo "Examples:"
    echo "  $0               # Standard health check"
    echo "  $0 --quick       # Quick health check"
    echo "  $0 --full        # Full comprehensive check"
    echo "  $0 --continuous  # Continuous monitoring"
}

# Function for quick health check
quick_health_check() {
    log "Starting quick health check..."
    
    check_docker_daemon
    check_container_status
    check_app_health
    
    generate_report
}

# Function for full health check
full_health_check() {
    log "Starting comprehensive health check..."
    
    check_docker_daemon
    check_container_status
    check_app_health
    check_system_resources
    check_network
    check_application_logs
    check_database
    check_load_performance
    
    generate_report
}

# Function for continuous monitoring
continuous_monitoring() {
    log "Starting continuous monitoring (Press Ctrl+C to stop)..."
    
    while true; do
        echo ""
        log "Running health check cycle..."
        
        quick_health_check
        
        log "Waiting 30 seconds for next check..."
        sleep 30
    done
}

# Main function
main() {
    log "Cloud Deployment Dashboard - Health Check"
    log "=========================================="
    
    case "${1:-}" in
        -h|--help)
            usage
            exit 0
            ;;
        -q|--quick)
            quick_health_check
            ;;
        -f|--full)
            full_health_check
            ;;
        -c|--continuous)
            continuous_monitoring
            ;;
        -r|--report)
            full_health_check
            ;;
        "")
            # Default: standard health check
            check_docker_daemon
            check_container_status
            check_app_health
            check_system_resources
            check_network
            
            generate_report
            ;;
        *)
            error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"