# Add parameters
param (
    [string]$image_name = "localhost/ingen_dev_ubuntu",
    [string]$container_name = "ingen_dev_ubuntu",
    [string]$dockerfile_path = "./docker/development_images/linux_development_image_ubuntu.dockerfile"
)

# Build the Podman image
Write-Output "Start Podman and Building the Podman image..."
podman machine start
podman build -f $dockerfile_path -t $image_name ./
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to build the Podman image."
    exit 1
}

# Run the PowerShell script to start the container
Write-Output "Running the PowerShell script to start the container..."
if (Get-Command pwsh -ErrorAction SilentlyContinue) {
    .\run_image_in_podman.ps1 -container_name $container_name -image_name $image_name
} else {
    Write-Output "Error: PowerShell (pwsh) is not installed or not available in the path."
    exit 1
}

# Get the container ID
$container_id = podman ps -q --filter "ancestor=$image_name"
if (-not $container_id) {
    Write-Output "Error: No running container found for the image $image_name."
    exit 1
}
Write-Output "Container ID: $container_id"

# SSH into the container
Write-Output "SSH into the container..."
podman exec -it $container_id bash
if ($LASTEXITCODE -ne 0) {
    Write-Output "Exited SSH into the container."
    exit 1
}
