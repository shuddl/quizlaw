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
echo " \__\_\\\\__,_|_/___||_____\__,_| \_/\_/  "
echo "                                        "
echo "========================================"
echo "Deployment Script"
echo "========================================"

# Function to display usage information
show_usage() {
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  --all         Deploy both frontend and backend"
  echo "  --frontend    Deploy only the frontend"
  echo "  --backend     Deploy only the backend"
  echo "  --build       Build Docker images (default: true)"
  echo "  --push        Push Docker images to registry (default: false)"
  echo "  --env ENV     Specify environment: dev, staging, prod (default: dev)"
  echo "  --help        Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0 --all --env prod --push"
  echo "  $0 --frontend --build"
}

# Default values
DEPLOY_FRONTEND=false
DEPLOY_BACKEND=false
BUILD=true
PUSH=false
ENV="dev"

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
echo ""

# Ensure we're in the project root directory
cd "$(dirname "$0")"

# Run the appropriate deployment scripts
if [[ "$DEPLOY_BACKEND" == "true" ]]; then
  echo "Deploying backend..."
  chmod +x ./backend/deploy.sh
  ./backend/deploy.sh --env "$ENV" $([ "$BUILD" == "true" ] && echo "--build") $([ "$PUSH" == "true" ] && echo "--push")
fi

if [[ "$DEPLOY_FRONTEND" == "true" ]]; then
  echo "Deploying frontend..."
  chmod +x ./frontend/deploy.sh
  ./frontend/deploy.sh --env "$ENV" $([ "$BUILD" == "true" ] && echo "--build") $([ "$PUSH" == "true" ] && echo "--push")
fi

echo "Deployment completed successfully!"
exit 0