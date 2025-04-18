#!/bin/bash

# QuizLaw Frontend Deployment Script

set -e  # Exit on any error

# Default values
BUILD=false
PUSH=false
ENV="dev"
DOCKER_REGISTRY="quizlaw"  # Change this to your Docker registry
TAG="latest"

# Function to display usage
show_usage() {
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  --build       Build Docker image"
  echo "  --push        Push Docker image to registry"
  echo "  --env ENV     Specify environment: dev, staging, prod (default: dev)"
  echo "  --help        Show this help message"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --build)
      BUILD=true
      shift
      ;;
    --push)
      PUSH=true
      shift
      ;;
    --env)
      ENV="$2"
      shift 2
      ;;
    --help)
      show_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      show_usage
      exit 1
      ;;
  esac
done

# Set the image name and tag based on environment
IMAGE_NAME="${DOCKER_REGISTRY}/quizlaw-frontend"
if [[ "$ENV" == "prod" ]]; then
  TAG="production"
  DOCKERFILE="Dockerfile"
  API_URL="https://api.quizlaw.com" # Change this to your production API URL
elif [[ "$ENV" == "staging" ]]; then
  TAG="staging"
  DOCKERFILE="Dockerfile"
  API_URL="https://staging-api.quizlaw.com" # Change this to your staging API URL
else
  TAG="development"
  DOCKERFILE="Dockerfile.dev"
  API_URL="http://localhost:5000" # Local development API URL
fi

# Ensure we're in the frontend directory
cd "$(dirname "$0")"

echo "========================================="
echo "QuizLaw Frontend Deployment"
echo "Environment: $ENV"
echo "Image: ${IMAGE_NAME}:${TAG}"
echo "Using Dockerfile: ${DOCKERFILE}"
echo "API URL: ${API_URL}"
echo "========================================="

# Create environment file for build
echo "Creating .env file for build..."
echo "VITE_API_BASE_URL=${API_URL}" > .env

# Build Docker image if requested
if [[ "$BUILD" == "true" ]]; then
  echo "Building frontend Docker image..."
  docker build -t ${IMAGE_NAME}:${TAG} -f ${DOCKERFILE} .
  
  # Also tag as latest for production
  if [[ "$ENV" == "prod" ]]; then
    docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_NAME}:latest
  fi
  
  echo "Build completed successfully."
fi

# Push Docker image if requested
if [[ "$PUSH" == "true" ]]; then
  echo "Pushing frontend Docker image to registry..."
  docker push ${IMAGE_NAME}:${TAG}
  
  # Also push latest tag for production
  if [[ "$ENV" == "prod" ]]; then
    docker push ${IMAGE_NAME}:latest
  fi
  
  echo "Push completed successfully."
fi

# Deploy to environment-specific infrastructure
case "$ENV" in
  prod)
    echo "Deploying to production environment..."
    # Add production deployment commands here (e.g., kubectl, docker-compose, etc.)
    # docker-compose -f docker-compose.prod.yml up -d frontend
    ;;
    
  staging)
    echo "Deploying to staging environment..."
    # Add staging deployment commands here
    # docker-compose -f docker-compose.staging.yml up -d frontend
    ;;
    
  *)
    echo "Deploying to development environment..."
    # Add development deployment commands here
    docker-compose up -d frontend
    ;;
esac

echo "Frontend deployment completed successfully!"
exit 0