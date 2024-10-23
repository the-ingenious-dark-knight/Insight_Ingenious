---

    weight: 2

---


# Installation

## System Setup

### Container Setup (Podman)

=== "Windows"
    
    To install Podman on Windows, you can use the following steps:
    
    1. Download the Podman installer from [Podman Windows Installer](https://podman.io/getting-started/installation).
    2. Follow the installation instructions to set up Podman on your system.
    3. After installation, add Podman to your PATH for easy access.

=== "MacOS"
    
    Install Podman using Homebrew:
    
    ```bash
    brew install podman
    ```
    
    After installation, ensure Podman is added to your PATH.

### PowerShell Installation

=== "Windows"

    Install PowerShell using the Windows Package Manager:

    ```powershell
    winget install --id Microsoft.PowerShell --source winget
    ```

=== "MacOS"

    Install PowerShell using Homebrew:

    ```bash
    brew install --cask powershell
    ```

### Repository Setup

Clone the repository from GitHub:

```bash
git clone git+https://github.com/Insight-Services-APAC/Insight_Ingenious.git
```

### Profile Setup

1. **Set Environment Variables:**

=== "Windows"
    
    ```powershell
    # Set the project path environment variable
    $env:INGENIOUS_PROJECT_PATH = "C:/<your_project_folder>/Insight_Ingenious/conversation_pattern_example/config.yml"
    
    # Disable parallelism for tokenizers to avoid potential issues
    $env:TOKENIZERS_PARALLELISM = "false"
    
    # Create or edit profiles.yml using your default code editor
    # Please follow template at /conversation_pattern_example/profile.yml
    code $home/.ingenious/profiles.yml
    ```

=== "MacOS"
    
    ```bash
    # Set the project path environment variable
    export INGENIOUS_PROJECT_PATH="/<your_project_folder>/Insight_Ingenious/conversation_pattern_example/config.yml"
    
    # Disable parallelism for tokenizers to avoid potential issues
    export TOKENIZERS_PARALLELISM=false
    
    # Set the path for profiles.yml
    export INGENIOUS_PROFILE="$HOME/.ingenious/profiles.yml"
    
    # Create or edit profiles.yml using your preferred editor (e.g., nano, vim, or code)
    # Please follow template at /conversation_pattern_example/profile.yml
    code $INGENIOUS_PROFILE
    ```

### Build the Docker Image

Build the development Docker image:

```bash
podman build -f ./docker/linux_development_image.dockerfile -t localhost/ingen_dev2 ./docker/
```

Run the container using the PowerShell script:

```powershell
pwsh .\run_image_in_podman.ps1
```

Verify the running containers:

```bash
podman ps
```

### Access the Container

=== "Windows (VSCode)"

    Use the "Remote - Containers" extension in Visual Studio Code to attach to the running container.

=== "Non-VSCode"

    Access the container using Podman:

    ```bash
    podman exec -it <container-id> /bin/bash
    ```
```




