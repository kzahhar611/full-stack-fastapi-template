#!/bin/bash
# TenderWise AI - Production Deployment Script
# Automated deployment with health checks and rollback capability

set -e  # Exit on any error

# Configuration
PROJECT_NAME="tenderwise-ai"
COMPOSE_FILE="docker-compose.production.yml"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
    log "INFO: $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING: $1"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    log "ERROR: $1"
}

# Check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker is not running. Please start Docker service."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [[ ! -f .env ]]; then
        error ".env file not found. Please create .env file with required environment variables."
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Create necessary directories
setup_directories() {
    info "Setting up directories..."
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p "./logs"
    mkdir -p "./uploads"
    mkdir -p "./nginx/ssl"
    
    success "Directories created"
}

# Backup current deployment
backup_current() {
    info "Creating backup of current deployment..."
    
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/backup_$BACKUP_TIMESTAMP"
    
    mkdir -p "$BACKUP_PATH"
    
    # Backup database
    if docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U postgres tenderwise_ai > "$BACKUP_PATH/database.sql" 2>/dev/null; then
        success "Database backup created"
    else
        warning "Database backup failed or no existing database"
    fi
    
    # Backup uploads
    if [[ -d "./uploads" ]]; then
        cp -r "./uploads" "$BACKUP_PATH/"
        success "Uploads backup created"
    fi
    
    # Backup configuration
    cp -r "./logs" "$BACKUP_PATH/" 2>/dev/null || true
    
    echo "$BACKUP_TIMESTAMP" > "./logs/last_backup"
    success "Backup completed: $BACKUP_PATH"
}

# Build and deploy
deploy() {
    info "Starting deployment..."
    
    # Pull latest images
    info "Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Build application
    info "Building application..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # Start services
    info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    success "Deployment started"
}

# Health check
health_check() {
    info "Performing health check..."
    
    local max_attempts=30
    local attempt=1
    local health_endpoint="http://localhost:8000/health"
    
    while [[ $attempt -le $max_attempts ]]; do
        info "Health check attempt $attempt/$max_attempts"
        
        if curl -s -f "$health_endpoint" > /dev/null 2>&1; then
            success "Application is healthy!"
            return 0
        fi
        
        sleep 10
        ((attempt++))
    done
    
    error "Health check failed after $max_attempts attempts"
    return 1
}

# Rollback function
rollback() {
    error "Deployment failed. Starting rollback..."
    
    # Stop current deployment
    docker-compose -f "$COMPOSE_FILE" down
    
    # Restore from backup
    if [[ -f "./logs/last_backup" ]]; then
        LAST_BACKUP=$(cat "./logs/last_backup")
        BACKUP_PATH="$BACKUP_DIR/backup_$LAST_BACKUP"
        
        if [[ -d "$BACKUP_PATH" ]]; then
            info "Restoring from backup: $BACKUP_PATH"
            
            # Restore uploads
            if [[ -d "$BACKUP_PATH/uploads" ]]; then
                rm -rf "./uploads"
                cp -r "$BACKUP_PATH/uploads" "./"
            fi
            
            # Restore database
            if [[ -f "$BACKUP_PATH/database.sql" ]]; then
                docker-compose -f "$COMPOSE_FILE" up -d db
                sleep 10
                docker-compose -f "$COMPOSE_FILE" exec -T db psql -U postgres -d tenderwise_ai < "$BACKUP_PATH/database.sql"
            fi
            
            success "Rollback completed"
        else
            error "Backup not found: $BACKUP_PATH"
        fi
    else
        error "No backup information found"
    fi
}

# Show status
show_status() {
    info "Deployment status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    info "Service logs (last 20 lines):"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20
}

# Main deployment function
main() {
    info "🚀 Starting TenderWise AI Production Deployment"
    
    # Create log file
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Run deployment steps
    check_prerequisites
    setup_directories
    backup_current
    
    # Deploy and check health
    if deploy && health_check; then
        success "🎉 Deployment completed successfully!"
        show_status
        
        info "Application is now available at:"
        info "  - API: http://localhost:8000"
        info "  - Health: http://localhost:8000/health"
        info "  - Docs: http://localhost:8000/docs"
        info "  - Monitoring: http://localhost:3000 (Grafana)"
        
    else
        error "Deployment failed!"
        rollback
        exit 1
    fi
}

# Script usage
usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  deploy     - Deploy to production (default)"
    echo "  rollback   - Rollback to previous version"
    echo "  status     - Show deployment status"
    echo "  logs       - Show service logs"
    echo "  stop       - Stop all services"
    echo "  restart    - Restart all services"
    echo "  backup     - Create manual backup"
    echo "  help       - Show this help message"
}

# Handle command line arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    rollback)
        rollback
        ;;
    status)
        show_status
        ;;
    logs)
        docker-compose -f "$COMPOSE_FILE" logs -f
        ;;
    stop)
        info "Stopping all services..."
        docker-compose -f "$COMPOSE_FILE" down
        success "Services stopped"
        ;;
    restart)
        info "Restarting all services..."
        docker-compose -f "$COMPOSE_FILE" restart
        health_check
        success "Services restarted"
        ;;
    backup)
        backup_current
        ;;
    help)
        usage
        ;;
    *)
        error "Unknown command: $1"
        usage
        exit 1
        ;;
esac