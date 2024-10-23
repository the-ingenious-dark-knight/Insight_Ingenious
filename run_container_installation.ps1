# Build the Podman image
Write-Output "Building the Podman image..."
podman machine init
podman build -f ./docker/linux_development_image.dockerfile -t localhost/ingen_dev2 ./docker/
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to build the Podman image."
    exit 1
}

# Run the PowerShell script to start the container
Write-Output "Running the PowerShell script to start the container..."
if (Get-Command pwsh -ErrorAction SilentlyContinue) {
    .\run_image_in_podman.ps1
} else {
    Write-Output "Error: PowerShell (pwsh) is not installed or not available in the path."
    exit 1
}

# Get the container ID
$container_id = podman ps -q --filter "ancestor=localhost/ingen_dev2"
if (-not $container_id) {
    Write-Output "Error: No running container found for the image localhost/ingen_dev2."
    exit 1
}
Write-Output "Container ID: $container_id"

# SSH into the container
Write-Output "SSH into the container..."
podman exec -it $container_id bash
if ($LASTEXITCODE -ne 0) {
    Write-Output "Error: Failed to SSH into the container."
    exit 1
}
