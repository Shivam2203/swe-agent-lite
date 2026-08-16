#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying SWE Agent Lite to Azure...${NC}"

# Check prerequisites
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install it first.${NC}"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Resource group
RESOURCE_GROUP=${AZURE_RESOURCE_GROUP:-swe-agent-rg}
CONTAINER_NAME=${AZURE_CONTAINER_NAME:-swe-agent-lite}
REGISTRY=${AZURE_REGISTRY:-sweagentregistry}
IMAGE_NAME=swe-agent-lite
TAG=$(git rev-parse --short HEAD)

echo -e "${BLUE}📦 Building Docker image...${NC}"
docker build -t $REGISTRY/$IMAGE_NAME:$TAG -f docker/Dockerfile .

echo -e "${BLUE}☁️  Pushing to Azure Container Registry...${NC}"
docker push $REGISTRY/$IMAGE_NAME:$TAG

echo -e "${BLUE}🚀 Deploying to Azure Container Instances...${NC}"
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image $REGISTRY/$IMAGE_NAME:$TAG \
    --dns-name-label swe-agent-${TAG} \
    --restart-policy OnFailure \
    --environment-variables \
        GROQ_API_KEY=$GROQ_API_KEY \
        ENVIRONMENT=production \
        LOG_LEVEL=INFO

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo "Container: $CONTAINER_NAME"
echo "Resource Group: $RESOURCE_GROUP"