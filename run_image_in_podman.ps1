# Install the powershell-yaml module if not already installed
if (-not (Get-Module -ListAvailable -Name powershell-yaml)) {
    Install-Module -Name powershell-yaml -Scope CurrentUser -Force
}

Import-Module powershell-yaml

# Define the path to the environment file
$envFilePath = $envFilePath = $home + "/.ingenious/profiles.yml"
# Read the entire environment file into a single string
if (Test-Path $envFilePath) {
    $envFileContent = Get-Content -Path $envFilePath -Raw
} else {
    Write-Error "Environment file not found: $envFilePath"
    exit 1
}


# Convert YAML content to PowerShell object
$envVars = $envFileContent | ConvertFrom-Yaml

# Convert PowerShell object to JSON
$envVarsJson_profile =  $envVars | ConvertTo-Json -Compress
#$envVarsJson_profile = $envVarsJson_profile -replace '"', '""'
if ($envVarsJson_profile[0] -ne "[") {
    $envVarsJson_profile = "[" + $envVarsJson_profile + "]"
}
# Define the path to the environment file
$envFilePath = $envFilePath = "./conversation_pattern_example/config.yml"
# Read the entire environment file into a single string
if (Test-Path $envFilePath) {
    $envFileContent = Get-Content -Path $envFilePath -Raw
} else {
    Write-Error "Environment file not found: $envFilePath"
    exit 1
}
# Convert YAML content to PowerShell object
$envVars = $envFileContent | ConvertFrom-Yaml

# Convert PowerShell object to JSON
$envVarsJson_config = $envVars | ConvertTo-Json -Compress
#$envVarsJson_config = $envVarsJson_config -replace '"', '""'

# Output the JSON for debugging purposes
# Write-Output $envVarsJson

# Define the container name and image
$containerName = "my_python_container"
$imageName = "localhost/ingen_dev"

# Run the container with the environment variables
$podmanRunCommand = "podman run -d --publish 9000:80  --mount type=bind,src=/mnt/c/Users/jramp/source/gitjr/Insight_Ingenious/dist,target=/ingen_dist --name $containerName --env 'APPSETTING_INGENIOUS_PROFILE=$envVarsJson_profile' --env 'APPSETTING_INGENIOUS_CONFIG=$envVarsJson_config' $imageName sleep 1000"
Invoke-Expression $podmanRunCommand

# Output the command for debugging purposes
Write-Output "Executed command: $podmanRunCommand"