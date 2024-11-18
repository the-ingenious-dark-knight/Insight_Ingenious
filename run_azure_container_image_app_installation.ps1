param (
    [string]$ImageName = "ca_ai_orchestrator:latest",
    [string]$ContainerAppName = "ca-ai-orchestrator-app",
    [string]$DockerfilePath = "./docker/production_images/linux_no_chat_summariser.dockerfile",
    [string]$ResourceGroup = "AI_Sandbox",
    [string]$AcrName = "aifansacsboxacr01",
    [string]$ContainerAppEnvironment = "managedEnvironment-AISandbox-99d0"
)

# Azure Login
az login
az acr login --name $AcrName

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

docker buildx build --platform linux/amd64 -f $DockerfilePath -t $ImageName --output type=docker .
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to build the Docker image."
    exit 1
}

# Push the image to Azure Container Registry
Write-Output "Tagging and pushing the image to Azure Container Registry..."
docker tag $ImageName "$AcrName.azurecr.io/$ImageName"
docker push "$AcrName.azurecr.io/$ImageName"
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to push the image to Azure Container Registry."
    exit 1
}
#
## Check if the container app exists
## az containerapp delete -n $ContainerAppName -g $ResourceGroup --yes
#Write-Output "Checking if Azure Container App '$ContainerAppName' exists..."
#$appExists = az containerapp show -n $ContainerAppName  -g $ResourceGroup --query "name" -o tsv
#
#if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($appExists))
#{
#    # Create a new container app
#    Write-Output "Container App '$ContainerAppName' does not exist. Creating a new app..."
##    az containerapp create `
##        -n $ContainerAppName `
##        -g $ResourceGroup `
##        --environment $ContainerAppEnvironment `
##        --image $($AcrName).azurecr.io/$ImageName
##
##    if ($LASTEXITCODE -ne 0)
##    {
##        Write-Output "Error: Failed to create Azure Container App."
##        exit 1
##    }
##    Write-Output "Azure Container App '$ContainerAppName' created successfully."
##
##    Write-Output "Creating secrets for the container app..."
##    az containerapp secret set `
##        -n $ContainerAppName `
##        -g $ResourceGroup `
##        --secrets config="" profile=""
##
##    if ($LASTEXITCODE -ne 0)
##    {
##        Write-Output "Error: Failed to create secrets."
##        exit 1
##    }
##    Write-Output "Secrets created successfully."
##
##
##
##    # Reference the secrets in environment variables
##    Write-Output "Updating Azure Container App '$ContainerAppName' to reference secrets in environment variables..."
##    $revisionSuffix = $( Get-Random -Minimum 21000 -Maximum 99999 )
##    az containerapp update `
##        -n $ContainerAppName `
##        -g $ResourceGroup `
##        --image $ImageName `
##        --revision-suffix "rev-$revisionSuffix" `
##        --env-vars APPSETTING_INGENIOUS_CONFIG=secretref:config APPSETTING_INGENIOUS_PROFILE=secretref:profile
##
##    if ($LASTEXITCODE -ne 0)
##    {
##        Write-Output "Error: Failed to update Azure Container App."
##        exit 1
##    }
#}
#else
#{
#    # Update the existing container app
#    Write-Output "Updating Azure Container App '$ContainerAppName' with the new image..."
#    az containerapp update `
#        -n $ContainerAppName `
#        -g $ResourceGroup `
#        --image $ImageName `
#
#    if ($LASTEXITCODE -ne 0)
#    {
#        Write-Output "Error: Failed to update Azure Container App."
#        exit 1
#    }
#
#    Write-Output "Azure Container App '$ContainerAppName' updated successfully."
#}

# Confirmation
Write-Output "Image successfully built for amd64, pushed to Azure, and deployed to the container app."
