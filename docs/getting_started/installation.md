---

    weight: 2

---



# Installation Guide

## System Setup

### Container Setup (Podman)

#### Windows
To install Podman on Windows, follow these steps:

1. **Download the Podman installer:**  
   Visit [Podman Windows Installer](https://podman.io/getting-started/installation) and download the installer.
2. **Run the installer:**  
   Follow the on-screen installation instructions.
3. **Add Podman to your PATH:**  
   Ensure Podman is accessible from the command line by adding it to your PATH.

#### MacOS
Install Podman using Homebrew:

```bash
brew install podman
```

After installation, verify Podman is in your PATH.

### PowerShell Installation

#### Windows
Install PowerShell using the Windows Package Manager:

```powershell
winget install --id Microsoft.PowerShell --source winget
```

#### MacOS
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

1. **Create Your Profile.yaml**

#### Windows

```powershell
# Create or edit profiles.yml using your default code editor
# Follow the template at /conversation_pattern_example/profile.yml
code $home/.ingenious/profiles.yml
```

#### MacOS

```bash
# Set the path for profiles.yml
export INGENIOUS_PROFILE="$HOME/.ingenious/profiles.yml"

# Edit profiles.yml using your preferred editor (e.g., nano, vim, code)
# Follow the template at /conversation_pattern_example/profile.yml
code $INGENIOUS_PROFILE
```

### Build the Docker Image

=== Simple Installation
      
      Run the installation script:
      
      ```powershell
      pwsh .\run_container_installation.ps1
      ```

=== Alternative Method
      
      Build and run the development Docker image manually:
      
      1. **Build the image:**
      
          ```bash
          podman build -f ./docker/linux_development_image.dockerfile -t localhost/ingen_dev2 ./docker/
          ```
      
      2. **Run the container:**
      
          ```powershell
          pwsh .\run_image_in_podman.ps1
          ```
      
      3. **Verify the running containers:**

       ```bash
       podman ps -a
       ```

      This command will show all running and stopped containers, helping you ensure that everything is functioning correctly.


### Access the Container

#### Windows (VSCode)

Use the "Dev Containers" extension in Visual Studio Code to attach to the running container:

1. **Open VSCode settings:**
   - Press `Ctrl + ,` (or `Cmd + ,` on Mac) to access settings.
   - Search for `Dev Containers: Docker Path` and change it from `docker` to `podman`.
2. **Attach to container:**
   - Open the Command Palette (`Ctrl + Shift + P` or `Cmd + Shift + P` on Mac).
   - Type `Dev Containers: Attach to Running Container...` and select the Podman container.

This allows Podman to act as the container runtime within the "Dev Containers" extension in VSCode.

#### Non-VSCode

You can access the container using Podman from the command line:

```bash
podman exec -it <container-id> /bin/bash
```

Replace `<container-id>` with your running container's ID or name.

This command provides direct shell access, similar to using `docker exec`.

## Running the Python Script Inside the Container

1. **Start the Python CLI:**

    ```powershell
    Write-Output "Running the Python CLI..."
    python run_ingen_cli.py
    ```

2. **Open the localhost URL in your browser:**

    ```plaintext
    Opening http://localhost:9000/docs
    ```

