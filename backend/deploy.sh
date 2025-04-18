#!/bin/bash

# QuizLaw Backend Deployment Script

set -e  # Exit on any error

# Default values
BUILD=false
PUSH=false
ENV="dev"
DOCKER_REGISTRY="quizlaw"  # Change this to your Docker registry
TAG="latest"
SKIP_MIGRATIONS=false  # Add flag to skip migrations

# Function to display usage
show_usage() {
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  --build           Build Docker image"
  echo "  --push            Push Docker image to registry"
  echo "  --env ENV         Specify environment: dev, staging, prod (default: dev)"
  echo "  --skip-migrations Skip database migrations (useful when dependencies are missing)"
  echo "  --help            Show this help message"
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
    --skip-migrations)
      SKIP_MIGRATIONS=true
      shift
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
echo "Skip Migrations: ${SKIP_MIGRATIONS}"
echo "========================================="

# Check if requirements.txt exists
if [[ ! -f requirements.txt ]]; then
  echo "ERROR: requirements.txt file is missing. Please ensure it exists in the backend directory."
  exit 1
fi

# Check if .env file exists, create from example if not
if [[ ! -f .env ]]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
  echo "WARNING: Please update the .env file with appropriate values before continuing."
  exit 1
fi

# Find Python command - try different common names
echo "Finding Python executable..."
PYTHON_CMD=""
for cmd in python python3 python3.9 python3.10 python3.11; do
  if command -v $cmd &> /dev/null; then
    PYTHON_CMD=$cmd
    echo "Found Python: $PYTHON_CMD"
    break
  fi
done

if [ -z "$PYTHON_CMD" ]; then
  echo "Error: Python executable not found. Please install Python 3.9 or later."
  echo "Proceeding with Docker deployment only (without local Python setup)."
else
  # Create or use a virtual environment
  echo "Setting up Python environment..."
  if [[ ! -d "venv" ]]; then
    echo "Creating new virtual environment..."
    $PYTHON_CMD -m venv venv || echo "Virtual environment creation failed, continuing without it"
  fi

  # Only proceed with venv if it was successfully created
  if [[ -d "venv" && -f "venv/bin/activate" ]]; then
    # Activate the virtual environment
    source venv/bin/activate

    # Install dependencies
    echo "Installing dependencies..."
    if command -v poetry &> /dev/null; then
      echo "Using Poetry to install dependencies..."
      poetry install --no-dev
    else
      echo "Poetry not found. Using pip with requirements.txt instead..."
      pip install -r requirements.txt || $PYTHON_CMD -m pip install -r requirements.txt
    fi

    # Run database migrations if not skipped
    if [[ "$SKIP_MIGRATIONS" == "false" ]]; then
      echo "Running database migrations..."
      if command -v poetry &> /dev/null; then
        poetry run alembic upgrade head
      else
        $PYTHON_CMD -m alembic upgrade head
      fi
    else
      echo "Skipping database migrations as requested."
    fi

    # Deactivate virtual environment (clean up)
    deactivate
  else
    echo "Skipping Python virtual environment setup due to errors."
  fi
fi

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