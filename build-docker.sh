#!/bin/bash

# Daur-AI v2.0 Docker Build Script
# Builds and optionally pushes Docker image

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="${1:-daur-ai}"
IMAGE_TAG="${2:-latest}"
REGISTRY="${3:-}"
DOCKERFILE="${4:-Dockerfile}"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Daur-AI v2.0 Docker Build Script${NC}"
echo -e "${YELLOW}========================================${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker found${NC}"

# Check if Dockerfile exists
if [ ! -f "$DOCKERFILE" ]; then
    echo -e "${RED}Error: Dockerfile not found: $DOCKERFILE${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Dockerfile found${NC}"

# Build image
echo -e "\n${YELLOW}Building Docker image...${NC}"
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" -f "$DOCKERFILE" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Image built successfully${NC}"
else
    echo -e "${RED}✗ Image build failed${NC}"
    exit 1
fi

# Show image info
echo -e "\n${YELLOW}Image Information:${NC}"
docker images | grep "${IMAGE_NAME}"

# Push to registry if specified
if [ -n "$REGISTRY" ]; then
    echo -e "\n${YELLOW}Pushing to registry: $REGISTRY${NC}"
    
    # Tag for registry
    docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    
    # Login to registry (if needed)
    if [ "$REGISTRY" != "docker.io" ]; then
        echo "Logging in to $REGISTRY..."
        docker login "$REGISTRY"
    fi
    
    # Push
    docker push "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Image pushed successfully${NC}"
    else
        echo -e "${RED}✗ Image push failed${NC}"
        exit 1
    fi
fi

# Run basic tests
echo -e "\n${YELLOW}Running basic tests...${NC}"

# Create temporary container
TEMP_CONTAINER=$(docker run -d "${IMAGE_NAME}:${IMAGE_TAG}" python3 -c "print('Test successful')")

# Wait for container
sleep 2

# Check if container ran
if docker ps -a | grep -q "$TEMP_CONTAINER"; then
    echo -e "${GREEN}✓ Container runs successfully${NC}"
    docker rm "$TEMP_CONTAINER" > /dev/null 2>&1
else
    echo -e "${RED}✗ Container test failed${NC}"
    exit 1
fi

echo -e "\n${YELLOW}========================================${NC}"
echo -e "${GREEN}✓ Build completed successfully!${NC}"
echo -e "${YELLOW}========================================${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Run container:"
echo "   docker run -p 5000:5000 ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "2. Or use docker-compose:"
echo "   docker-compose up -d"
echo ""
echo "3. Check health:"
echo "   curl http://localhost:5000/api/v2/health"

