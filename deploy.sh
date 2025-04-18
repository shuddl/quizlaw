#!/bin/bash

# QuizLaw Deployment Script
# This script handles the deployment of both frontend and backend components

set -e  # Exit on any error

# Display ASCII art banner
echo "========================================"
echo "  ___        _      _                   "
echo " / _ \ _   _(_)____| |    __ ___      __"
echo "| | | | | | | |_  /| |   / _\` \ \ /\ / /"
echo "| |_| | |_| | |/ / | |__| (_| |\ V  V / "
echo " \__\_\\__,_|_/___||_____\__,_| \_/\_/  "
echo "                                        "
echo "========================================"
echo "Deployment Script"
echo "========================================"

# Function to display usage information
show_usage() {
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  --all             Deploy both frontend and backend"
  echo "  --frontend        Deploy only the frontend"
  echo "  --backend         Deploy only the backend"
  echo "  --build           Build Docker images (default: true)"
  echo "  --no-build        Skip building Docker images"
  echo "  --push            Push Docker images to registry (default: false)"
  echo "  --env ENV         Specify environment: dev, staging, prod (default: dev)"
  echo "  --skip-migrations Skip database migrations (useful when dependencies are missing)"
  echo "  --clean           Clean up environment before deploying (close ports, remove stale files)"
  echo "  --help            Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0 --all --env prod --push"
  echo "  $0 --frontend --build"
  echo "  $0 --all --skip-migrations"
}

# Default values
DEPLOY_FRONTEND=false
DEPLOY_BACKEND=false
BUILD=true
PUSH=false
ENV="dev"
SKIP_MIGRATIONS=false
CLEAN_ENV=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      DEPLOY_FRONTEND=true
      DEPLOY_BACKEND=true
      shift
      ;;
    --frontend)
      DEPLOY_FRONTEND=true
      shift
      ;;
    --backend)
      DEPLOY_BACKEND=true
      shift
      ;;
    --build)
      BUILD=true
      shift
      ;;
    --no-build)
      BUILD=false
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
    --clean)
      CLEAN_ENV=true
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

# Check if at least one component is selected
if [[ "$DEPLOY_FRONTEND" == "false" && "$DEPLOY_BACKEND" == "false" ]]; then
  echo "Error: You must specify at least one component to deploy (--all, --frontend, or --backend)"
  show_usage
  exit 1
fi

# Display deployment configuration
echo "Deployment Configuration:"
echo "  Environment: $ENV"
echo "  Frontend: $DEPLOY_FRONTEND"
echo "  Backend: $DEPLOY_BACKEND"
echo "  Build Images: $BUILD"
echo "  Push Images: $PUSH"
echo "  Skip Migrations: $SKIP_MIGRATIONS"
echo "  Clean Environment: $CLEAN_ENV"
echo ""

# Ensure we're in the project root directory
cd "$(dirname "$0")"

# Clean up environment if requested or by default
echo "Cleaning up environment before deployment..."
# Stop any running Docker containers
docker compose down

# Remove any stale build files
if [[ "$DEPLOY_FRONTEND" == "true" ]]; then
  echo "Removing frontend build artifacts..."
  rm -rf frontend/dist frontend/.vite frontend/node_modules/.vite
fi

if [[ "$DEPLOY_BACKEND" == "true" ]]; then
  echo "Cleaning backend cache files..."
  find backend -type d -name "__pycache__" -exec rm -rf {} +
fi

# Check for and kill any stray Vite processes
if [[ "$DEPLOY_FRONTEND" == "true" ]]; then
  echo "Checking for stray Vite processes..."
  pids=$(lsof -ti:3000,5173,5174)
  if [ ! -z "$pids" ]; then
    echo "Found processes using Vite ports. Terminating: $pids"
    kill -9 $pids 2> /dev/null || echo "No processes to kill"
  fi
fi

# Create Docker Compose override file based on environment
if [[ "$ENV" == "prod" ]]; then
  COMPOSE_FILE="docker-compose.yml -f docker-compose.prod.yml"
  echo "Using production configuration"
elif [[ "$ENV" == "staging" ]]; then
  COMPOSE_FILE="docker-compose.yml -f docker-compose.staging.yml"
  echo "Using staging configuration"
else
  COMPOSE_FILE="docker-compose.yml"
  echo "Using development configuration"
fi

# Run the appropriate deployment steps
if [[ "$BUILD" == "true" ]]; then
  # Building Docker images
  if [[ "$DEPLOY_BACKEND" == "true" ]]; then
    echo "Building backend Docker image..."
    cd backend
    docker build -t quizlaw/quizlaw-backend:${ENV} .
    cd ..
  fi
  
  if [[ "$DEPLOY_FRONTEND" == "true" ]]; then
    echo "Building frontend Docker image..."
    cd frontend
    # Set the appropriate API URL based on environment
    if [[ "$ENV" == "prod" ]]; then
      echo "VITE_API_BASE_URL=https://api.quizlaw.com" > .env
      DOCKERFILE="Dockerfile"
    elif [[ "$ENV" == "staging" ]]; then
      echo "VITE_API_BASE_URL=https://staging-api.quizlaw.com" > .env
      DOCKERFILE="Dockerfile"
    else
      echo "VITE_API_BASE_URL=http://localhost:5000" > .env
      DOCKERFILE="Dockerfile.dev"
    fi
    docker build -t quizlaw/quizlaw-frontend:${ENV} -f ${DOCKERFILE} .
    cd ..
  fi
fi

# Push Docker images if requested
if [[ "$PUSH" == "true" ]]; then
  if [[ "$DEPLOY_BACKEND" == "true" ]]; then
    echo "Pushing backend Docker image to registry..."
    docker push quizlaw/quizlaw-backend:${ENV}
  fi
  
  if [[ "$DEPLOY_FRONTEND" == "true" ]]; then
    echo "Pushing frontend Docker image to registry..."
    docker push quizlaw/quizlaw-frontend:${ENV}
  fi
fi

# Check if .env file exists for backend, create from example if not
if [[ "$DEPLOY_BACKEND" == "true" && ! -f backend/.env ]]; then
  echo "Creating backend .env file from .env.example..."
  if [[ -f backend/.env.example ]]; then
    cp backend/.env.example backend/.env
    echo "Backend .env file created. Please verify the values before continuing."
  else
    echo "Warning: No .env.example found for backend. You'll need to create a .env file manually."
  fi
fi

# Handle database migrations if deploying backend
if [[ "$DEPLOY_BACKEND" == "true" && "$SKIP_MIGRATIONS" == "false" ]]; then
  echo "Running database migrations..."
  
  # Find Python command
  PYTHON_CMD=""
  for cmd in python python3 python3.9 python3.10 python3.11; do
    if command -v $cmd &> /dev/null; then
      PYTHON_CMD=$cmd
      break
    fi
  done
  
  if [ -z "$PYTHON_CMD" ]; then
    echo "Warning: Python not found. Skipping migrations. Use Docker to run migrations."
  else
    # Set up Python environment and run migrations
    cd backend
    
    # Create or activate virtual environment
    if [[ ! -d "venv" ]]; then
      echo "Creating virtual environment..."
      $PYTHON_CMD -m venv venv || echo "Virtual environment creation failed. Will try Docker for migrations."
    fi
    
    if [[ -d "venv" && -f "venv/bin/activate" ]]; then
      source venv/bin/activate
      
      # Install dependencies
      if command -v poetry &> /dev/null; then
        echo "Using Poetry to install dependencies..."
        poetry install --without dev
      else
        echo "Using pip with requirements.txt..."
        pip install -r requirements.txt || $PYTHON_CMD -m pip install -r requirements.txt
      fi
      
      # Run migrations
      if command -v poetry &> /dev/null; then
        poetry run alembic upgrade head
      else
        $PYTHON_CMD -m alembic upgrade head
      fi
      
      deactivate
    else
      echo "Using Docker to run migrations..."
      docker-compose -f $COMPOSE_FILE run --rm backend alembic upgrade head
    fi
    
    cd ..
  fi
fi

# Deploy services using Docker Compose
echo "Deploying services with Docker Compose..."

# Setup the command
COMPOSE_CMD="docker-compose -f $COMPOSE_FILE"

# Add services based on deployment selection
SERVICES=""
if [[ "$DEPLOY_BACKEND" == "true" ]]; then
  SERVICES="$SERVICES backend db"
fi

if [[ "$DEPLOY_FRONTEND" == "true" ]]; then
  SERVICES="$SERVICES frontend"
fi

# Run the command with the selected services
if [[ ! -z "$SERVICES" ]]; then
  $COMPOSE_CMD up -d $SERVICES
  echo "Services started: $SERVICES"
else
  echo "No services were selected for deployment"
fi

# Verify services are running correctly
echo "Verifying services..."
if [[ "$DEPLOY_FRONTEND" == "true" ]]; then
  # Wait for frontend to start
  echo "Waiting for frontend to start..."
  sleep 5
  
  # Check if frontend is accessible
  if curl -s --head --fail http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running on port 3000"
  else
    echo "⚠️ Frontend may not be running. Check logs with: docker compose logs frontend"
  fi
fi

if [[ "$DEPLOY_BACKEND" == "true" ]]; then
  # Wait for backend to start
  echo "Waiting for backend to start..."
  sleep 5
  
  # Check if backend is accessible
  if curl -s --head --fail http://localhost:5000/api/health > /dev/null; then
    echo "✅ Backend is running on port 5000"
  else
    echo "⚠️ Backend may not be running. Check logs with: docker compose logs backend"
  fi
fi

echo "Deployment completed successfully!"
exit 0