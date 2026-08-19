#!/bin/bash
set -e

echo "🚀 Deploying to Azure Container Registry..."

# Variables
RESOURCE_GROUP="swe-agent-rg"
REGISTRY_NAME="sweagentregistry"
IMAGE_NAME="swe-agent-lite"
TAG=$(git rev-parse --short HEAD)

# Login to Azure
az login

# Create resource group if not exists
az group create --name $RESOURCE_GROUP --location eastus

# Create ACR if not exists
az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic

# Login to ACR
az acr login --name $REGISTRY_NAME

# Build and push
docker build -t $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$TAG -f Dockerfile .
docker push $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$TAG

# Deploy to Azure Container Instances
az container create \
    --resource-group $RESOURCE_GROUP \
    --name swe-agent-lite \
    --image $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$TAG \
    --dns-name-label swe-agent-$TAG \
    --restart-policy OnFailure \
    --environment-variables \
        GROQ_API_KEY=$GROQ_API_KEY \
        ENVIRONMENT=production

echo "✅ Deployed to Azure!"