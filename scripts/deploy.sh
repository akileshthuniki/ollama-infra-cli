#!/bin/bash
set -euo pipefail

# Configuration
PROJECT="ollama-infra"
ENV=${1:-staging}  # Default to staging if no environment specified
WITH_ANALYZER=${2:-false}  # Optional: --with-analyzer

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    echo "Usage: $0 [ENVIRONMENT] [--with-analyzer]"
    echo ""
    echo "ENVIRONMENTS:"
    echo "  staging     Deploy to staging environment (default)"
    echo "  production  Deploy to production environment"
    echo ""
    echo "OPTIONS:"
    echo "  --with-analyzer  Also run DevOps analyzer after deployment"
    echo ""
    echo "EXAMPLES:"
    echo "  $0 staging                    # Deploy to staging"
    echo "  $0 production                 # Deploy to production"
    echo "  $0 staging --with-analyzer    # Deploy to staging and run analyzer"
}

# Validate environment
validate_environment() {
    if [[ ! "$ENV" =~ ^(staging|production)$ ]]; then
        log_error "Invalid environment: $ENV"
        log_error "Valid environments: staging, production"
        show_help
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed"
        exit 1
    fi
    
    # Check Docker (for building)
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured"
        log_error "Run: aws configure"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION:-us-east-1}.amazonaws.com"
    IMAGE_NAME="ollama-api"
    TAG="$(git rev-parse --short HEAD)"
    IMAGE_URI="${ECR_REGISTRY}/${IMAGE_NAME}:${TAG}"
    
    # Login to ECR
    log_info "Logging into ECR..."
    aws ecr get-login-password --region ${AWS_DEFAULT_REGION:-us-east-1} | docker login --username AWS --password-stdin $ECR_REGISTRY
    
    # Create repository if it doesn't exist
    if ! aws ecr describe-repositories --repository-names $IMAGE_NAME &> /dev/null; then
        log_info "Creating ECR repository..."
        aws ecr create-repository --repository-name $IMAGE_NAME --region ${AWS_DEFAULT_REGION:-us-east-1}
    fi
    
    # Build image
    log_info "Building Docker image: $IMAGE_URI"
    docker build -t $IMAGE_URI -f docker/Dockerfile.api .
    
    # Also tag as latest
    docker tag $IMAGE_URI "${ECR_REGISTRY}/${IMAGE_NAME}:latest"
    
    log_success "Docker image built successfully"
    echo "IMAGE_URI=$IMAGE_URI"
}

# Push Docker image
push_image() {
    local image_uri=$1
    log_info "Pushing Docker image..."
    
    docker push $image_uri
    docker push "${ECR_REGISTRY}/${IMAGE_NAME}:latest"
    
    log_success "Docker image pushed successfully"
}

# Deploy infrastructure
deploy_infrastructure() {
    local image_uri=$1
    log_info "Deploying infrastructure to $ENV environment..."
    
    # Navigate to environment directory
    cd "$(dirname "$0")/../infra/environments/$ENV"
    
    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    log_info "Planning Terraform deployment..."
    terraform plan -out=tfplan -var "image_uri=$image_uri"
    
    # Apply deployment
    log_info "Applying Terraform deployment..."
    terraform apply -auto-approve tfplan
    
    # Get outputs
    ALB_URL=$(terraform output -raw alb_url 2>/dev/null || echo "")
    CLUSTER_NAME=$(terraform output -raw cluster_name 2>/dev/null || echo "")
    
    log_success "Infrastructure deployed successfully"
    
    # Return to original directory
    cd - > /dev/null
    
    # Export outputs for other functions
    export ALB_URL
    export CLUSTER_NAME
}

# Health check
health_check() {
    local alb_url=$1
    local max_attempts=30
    local attempt=1
    
    if [[ -z "$alb_url" ]]; then
        log_warning "No ALB URL available for health check"
        return 0
    fi
    
    log_info "Performing health check on $alb_url..."
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$alb_url/health" > /dev/null; then
            log_success "Health check passed (attempt $attempt/$max_attempts)"
            return 0
        fi
        
        log_info "Health check failed, retrying... ($attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Run DevOps analyzer
run_analyzer() {
    local alb_url=$1
    local cluster_name=$2
    
    log_info "Running DevOps analyzer..."
    
    # Check if analyzer exists
    if [[ ! -d "devops-analyzer" ]]; then
        log_warning "DevOps analyzer not found, skipping analysis"
        return 0
    fi
    
    # Install analyzer dependencies
    cd devops-analyzer
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    fi
    
    # Create reports directory
    mkdir -p reports
    
    # Run URL analysis
    if [[ -n "$alb_url" ]]; then
        log_info "Running URL analysis..."
        python devops-analyzer.py url "$alb_url" --question "Is the deployment successful?" --output "reports/deployment_analysis_$(date +%Y%m%d_%H%M%S).md"
    fi
    
    # Run infrastructure analysis
    if [[ -n "$cluster_name" ]]; then
        log_info "Running infrastructure analysis..."
        python devops-analyzer.py infrastructure --type health --cluster "$cluster_name" --output "reports/health_check_$(date +%Y%m%d_%H%M%S).md"
    fi
    
    cd - > /dev/null
    log_success "DevOps analyzer completed"
}

# Show deployment summary
show_summary() {
    local alb_url=$1
    local cluster_name=$2
    
    echo ""
    echo "=================================="
    echo "🎉 Deployment Summary"
    echo "=================================="
    echo "Environment: $ENV"
    echo "Project: $PROJECT"
    
    if [[ -n "$alb_url" ]]; then
        echo "ALB URL: $alb_url"
        echo "Health Endpoint: $alb_url/health"
        echo "API Endpoint: $alb_url/api/analyze"
    fi
    
    if [[ -n "$cluster_name" ]]; then
        echo "ECS Cluster: $cluster_name"
    fi
    
    echo ""
    echo "🔍 Next Steps:"
    echo "1. Test the API: curl $alb_url/health"
    echo "2. Check the logs: aws logs tail /ecs/ollama-api-$ENV --follow"
    echo "3. Run analyzer: cd devops-analyzer && python devops-analyzer.py infrastructure --type health --cluster $cluster_name"
    echo ""
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    # Remove terraform plan files
    find infra/environments -name "tfplan" -delete 2>/dev/null || true
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    echo "🚀 Starting deployment for $PROJECT to $ENV environment"
    echo "=================================="
    
    # Parse arguments
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then
        show_help
        exit 0
    fi
    
    # Validate environment
    validate_environment
    
    # Check prerequisites
    check_prerequisites
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Build and push image
    IMAGE_URI=$(build_image | grep "IMAGE_URI=" | cut -d'=' -f2)
    push_image "$IMAGE_URI"
    
    # Deploy infrastructure
    deploy_infrastructure "$IMAGE_URI"
    
    # Health check
    if ! health_check "$ALB_URL"; then
        log_error "Deployment failed health check"
        exit 1
    fi
    
    # Run analyzer if requested
    if [[ "$WITH_ANALYZER" == "--with-analyzer" ]]; then
        run_analyzer "$ALB_URL" "$CLUSTER_NAME"
    fi
    
    # Show summary
    show_summary "$ALB_URL" "$CLUSTER_NAME"
    
    log_success "🎉 Deployment completed successfully!"
}

# Run main function with all arguments
main "$@"
