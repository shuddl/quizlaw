#!/bin/bash

# QuizLaw Backend Deployment Script

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
IMAGE_NAME="${DOCKER_REGISTRY}/quizlaw-backend"
if [[ "$ENV" == "prod" ]]; then
  TAG="production"
elif [[ "$ENV" == "staging" ]]; then
  TAG="staging"
else
  TAG="development"
fi

# Ensure we're in the backend directory
cd "$(dirname "$0")"

echo "========================================="
echo "QuizLaw Backend Deployment"
echo "Environment: $ENV"
echo "Image: ${IMAGE_NAME}:${TAG}"
echo "========================================="

# Check if .env file exists, create from example if not
if [[ ! -f .env ]]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
  echo "WARNING: Please update the .env file with appropriate values before continuing."
  exit 1
fi

# Run database migrations
echo "Running database migrations..."
poetry run alembic upgrade head

# Build Docker image if requested
if [[ "$BUILD" == "true" ]]; then
  echo "Building backend Docker image..."
  docker build -t ${IMAGE_NAME}:${TAG} .
  
  # Also tag as latest for production
  if [[ "$ENV" == "prod" ]]; then
    docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_NAME}:latest
  fi
  
  echo "Build completed successfully."
fi

# Push Docker image if requested
if [[ "$PUSH" == "true" ]]; then
  echo "Pushing backend Docker image to registry..."
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
    # docker-compose -f docker-compose.prod.yml up -d backend
    ;;
    
  staging)
    echo "Deploying to staging environment..."
    # Add staging deployment commands here
    # docker-compose -f docker-compose.staging.yml up -d backend
    ;;
    
  *)
    echo "Deploying to development environment..."
    # Add development deployment commands here
    docker-compose up -d backend
    ;;
esac

echo "Backend deployment completed successfully!"
exit 0