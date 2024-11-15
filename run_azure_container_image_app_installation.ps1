param (
    [string]$image_name = "ca_ai_orchestrator:latest",
    [string]$container_name = "ca_ai_orchestrator",
    [string]$dockerfile_path = "./docker/production_images/linux_no_chat_summariser.dockerfile",
    [string]$resource_group = "AI_Sandbox",
    [string]$acr_name = "aifansacsboxacr01"
)

# Azure Login
az login
az acr login --name $acr_name

# Create directory and copy dataset
New-Item -ItemType Directory -Force -Path ./docker/ingenious/sample_dataset
Copy-Item -Path ingenious/sample_dataset/cleaned_students_performance.csv -Destination ./docker/ingenious/sample_dataset/cleaned_students_performance.csv

# Build the Python wheel package using pyproject.toml
Write-Output "Building the Python wheel package using pyproject.toml..."
python -m pip install --upgrade build
python -m build --outdir ./dist
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to build the wheel package."
    exit 1
}

# Build the Docker image for amd64 architecture
Write-Output "Building the Docker image for amd64 architecture..."
docker buildx create --use
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to initialize buildx."
    exit 1
}

docker buildx build --platform linux/amd64 -f $dockerfile_path -t $image_name --output type=docker .
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to build the Docker image."
    exit 1
}

# Push the image to Azure Container Registry
Write-Output "Tagging and pushing the image to Azure Container Registry..."
docker tag $image_name "$acr_name.azurecr.io/$image_name"
docker push "$acr_name.azurecr.io/$image_name"
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to push the image to Azure Container Registry."
    exit 1
}

# Check if the container app exists
Write-Output "Checking if Azure Container App '$containerAppName' exists..."
$appExists = az containerapp show `
    -n $containerAppName `
    -g $resourceGroup `
    --query "name" `
    -o tsv

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($appExists)) {
    # Create a new container app
    Write-Output "Container App '$containerAppName' does not exist. Creating a new app..."
    az containerapp create `
        -n $containerAppName `
        -g $resourceGroup `
        --image $imageFullName `
        --set-env-vars APPSETTING_INGENIOUS_CONFIG=secretref:config APPSETTING_INGENIOUS_PROFILE=secretref:profile

    if ($LASTEXITCODE -ne 0) {
        Write-Output "Error: Failed to create Azure Container App."
        exit 1
    }

    Write-Output "Azure Container App '$containerAppName' created successfully with initial secrets."
} else {
    # Update the existing container app
    Write-Output "Updating Azure Container App '$containerAppName' with the new image..."
    az containerapp update `
        -n $containerAppName `
        -g $resourceGroup `
        --image $imageFullName `
        --set-env-vars APPSETTING_INGENIOUS_CONFIG=secretref:config APPSETTING_INGENIOUS_PROFILE=secretref:profile

    if ($LASTEXITCODE -ne 0) {
        Write-Output "Error: Failed to update Azure Container App."
        exit 1
    }

    Write-Output "Azure Container App '$containerAppName' updated successfully."
}

# Confirmation
Write-Output "Image successfully built for amd64, pushed to Azure, and deployed to the container app."
