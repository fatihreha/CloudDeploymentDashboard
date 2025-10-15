#!/bin/bash

# Cloud Deployment Dashboard - Deployment Script
# This script automates the deployment process for the dashboard application

set -e  # Exit on any error

# Configuration
APP_NAME="cloud-deployment-dashboard"
IMAGE_NAME="$APP_NAME:latest"
CONTAINER_NAME="$APP_NAME-container"
PORT="5000"
LOG_DIR="./logs/deployments"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/deploy_$TIMESTAMP.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to check if Docker is running
check_docker() {
    log "Checking Docker status..."
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    success "Docker is running"
}

# Function to stop and remove existing container
cleanup_existing() {
    log "Cleaning up existing containers..."
    
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        log "Stopping existing container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" || true
    fi
    
    if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
        log "Removing existing container: $CONTAINER_NAME"
        docker rm "$CONTAINER_NAME" || true
    fi
    
    success "Cleanup completed"
}

# Function to build Docker image
build_image() {
    log "Building Docker image: $IMAGE_NAME"
    
    if docker build -t "$IMAGE_NAME" .; then
        success "Docker image built successfully"
    else
        error "Failed to build Docker image"
        exit 1
    fi
}

# Function to run the container
run_container() {
    log "Starting new container: $CONTAINER_NAME"
    
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p "$PORT:5000" \
        -v "$(pwd)/logs:/app/logs" \
        -v "/var/run/docker.sock:/var/run/docker.sock" \
        --restart unless-stopped \
        "$IMAGE_NAME"
    
    if [ $? -eq 0 ]; then
        success "Container started successfully"
        log "Container is running on port $PORT"
    else
        error "Failed to start container"
        exit 1
    fi
}

# Function to check container health
check_health() {
    log "Checking container health..."
    
    # Wait for container to start
    sleep 10
    
    # Check if container is running
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        success "Container is running"
        
        # Check application health
        if curl -f "http://localhost:$PORT/api/health-check" >/dev/null 2>&1; then
            success "Application health check passed"
        else
            warning "Application health check failed, but container is running"
        fi
    else
        error "Container is not running"
        log "Container logs:"
        docker logs "$CONTAINER_NAME" | tail -20 | tee -a "$LOG_FILE"
        exit 1
    fi
}

# Function to show deployment info
show_info() {
    log "Deployment Information:"
    echo "========================" | tee -a "$LOG_FILE"
    echo "Application: $APP_NAME" | tee -a "$LOG_FILE"
    echo "Image: $IMAGE_NAME" | tee -a "$LOG_FILE"
    echo "Container: $CONTAINER_NAME" | tee -a "$LOG_FILE"
    echo "Port: $PORT" | tee -a "$LOG_FILE"
    echo "URL: http://localhost:$PORT" | tee -a "$LOG_FILE"
    echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "========================" | tee -a "$LOG_FILE"
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -b, --build    Build image only"
    echo "  -r, --run      Run container only (assumes image exists)"
    echo "  -c, --clean    Clean up containers and images"
    echo "  --no-cache     Build without cache"
    echo ""
    echo "Examples:"
    echo "  $0              # Full deployment (build + run)"
    echo "  $0 --build      # Build image only"
    echo "  $0 --run        # Run container only"
    echo "  $0 --clean      # Clean up everything"
}

# Function to clean up everything
cleanup_all() {
    log "Performing complete cleanup..."
    
    # Stop and remove container
    cleanup_existing
    
    # Remove image
    if docker images -q "$IMAGE_NAME" | grep -q .; then
        log "Removing Docker image: $IMAGE_NAME"
        docker rmi "$IMAGE_NAME" || true
    fi
    
    # Remove unused images and volumes
    log "Cleaning up unused Docker resources..."
    docker system prune -f
    
    success "Complete cleanup finished"
}

# Main deployment function
deploy() {
    log "Starting deployment of $APP_NAME"
    log "Timestamp: $TIMESTAMP"
    
    check_docker
    cleanup_existing
    build_image
    run_container
    check_health
    show_info
    
    success "Deployment completed successfully!"
    log "Access your application at: http://localhost:$PORT"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
    -b|--build)
        log "Building image only..."
        check_docker
        build_image
        success "Build completed!"
        ;;
    -r|--run)
        log "Running container only..."
        check_docker
        cleanup_existing
        run_container
        check_health
        show_info
        success "Container started!"
        ;;
    -c|--clean)
        cleanup_all
        ;;
    --no-cache)
        log "Building with --no-cache option..."
        check_docker
        cleanup_existing
        docker build --no-cache -t "$IMAGE_NAME" .
        run_container
        check_health
        show_info
        success "Deployment completed!"
        ;;
    "")
        # Default: full deployment
        deploy
        ;;
    *)
        error "Unknown option: $1"
        usage
        exit 1
        ;;
esac