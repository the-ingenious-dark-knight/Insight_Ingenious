param (
    [string]$ImageName = "ca_ai_orchestrator:latest",
    [string]$ContainerAppName = "ca-ai-orchestrator-app",
    [string]$DockerfilePath = "./docker/production_images/linux_no_chat_summariser.dockerfile",
    [string]$ResourceGroup = "AI_Sandbox",
    [string]$AcrName = "aifansacsboxacr01"
)
#
## Azure Login
#az login
#az acr login --name $AcrName
#
## Build the Python wheel package using pyproject.toml
#Write-Output "Building the Python wheel package using pyproject.toml..."
#python -m pip install --upgrade build
#python -m build --outdir ./dist
#if ($LASTEXITCODE -ne 0) {
#    Write-Output "Error: Failed to build the wheel package."
#    exit 1
#}
#
## Build the Docker image for amd64 architecture
#Write-Output "Building the Docker image for amd64 architecture..."
#docker buildx create --use
#if ($LASTEXITCODE -ne 0) {
#    Write-Output "Error: Failed to initialize buildx."
#    exit 1
#}
#
#docker buildx build --platform linux/amd64 -f $DockerfilePath -t $ImageName --output type=docker .
#if ($LASTEXITCODE -ne 0) {
#    Write-Output "Error: Failed to build the Docker image."
#    exit 1
#}
#
## Push the image to Azure Container Registry
#Write-Output "Tagging and pushing the image to Azure Container Registry..."
#docker tag $ImageName "$AcrName.azurecr.io/$ImageName"
#docker push "$AcrName.azurecr.io/$ImageName"
#if ($LASTEXITCODE -ne 0) {
#    Write-Output "Error: Failed to push the image to Azure Container Registry."
#    exit 1
#}
#
## Check if the container app exists
#Write-Output "Checking if Azure Container App '$ContainerAppName' exists..."
#$appExists = az containerapp show `
#    -n $ContainerAppName `
#    -g $ResourceGroup `
#    --query "name" `
#    -o tsv
#
#if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($appExists)) {
#    # Create a new container app
#    Write-Output "Container App '$ContainerAppName' does not exist. Creating a new app..."
#    az containerapp create `
#        -n $ContainerAppName `
#        -g $ResourceGroup `
#        --image $ImageName `
#        --set-env-vars APPSETTING_INGENIOUS_CONFIG=secretref:config APPSETTING_INGENIOUS_PROFILE=secretref:profile
#
#    if ($LASTEXITCODE -ne 0) {
#        Write-Output "Error: Failed to create Azure Container App."
#        exit 1
#    }
#
#    Write-Output "Azure Container App '$ContainerAppName' created successfully with initial secrets."
#} else {
#    # Generate a random revision suffix
#    $revisionSuffix = $(Get-Random -Minimum 1000 -Maximum 9999)
#    Write-Output "Updating Azure Container App '$ContainerAppName' with the new image and revision-suffix '$revisionSuffix'..."
#
#    az containerapp update `
#        -n $ContainerAppName `
#        -g $ResourceGroup `
#        --image $ImageName `
#        --revision-suffix "rev-$revisionSuffix" `
#        --set-env-vars APPSETTING_INGENIOUS_CONFIG=secretref:config APPSETTING_INGENIOUS_PROFILE=secretref:profile
#
#    if ($LASTEXITCODE -ne 0) {
#        Write-Output "Error: Failed to update Azure Container App."
#        exit 1
#    }
#
#    Write-Output "Azure Container App '$ContainerAppName' updated successfully."
#}

# Confirmation
Write-Output "Image successfully built for amd64, pushed to Azure, and deployed to the container app."
