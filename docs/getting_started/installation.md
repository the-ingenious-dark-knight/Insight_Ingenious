---

    weight: 2
    
---

# Installation Guide

## System Setup


### PowerShell Installation

=== "Windows"

    Install PowerShell using the Windows Package Manager (Winget):

    ```powershell
    winget install --id Microsoft.PowerShell --source winget
    ```

=== "macOS"

    Install PowerShell using Homebrew:

    ```bash
    brew install --cask powershell
    ```

    Verify installation:

    ```bash
    pwsh --version
    ```


### Container Setup (Podman)

=== "Windows"

    To install Podman on Windows, follow these steps:

    1. Download the Podman installer from the official website: [Podman Windows Installer](https://podman.io/getting-started/installation).
    2. Run the installer and follow the on-screen instructions to complete the setup.
    3. After installation, run below command in your terminal:

    ```bash    
    podman machine init
    ```


=== "macOS"

    Install Podman using Homebrew:

    ```bash
    brew install podman
    ```

    After installation, ensure Podman is added to your PATH by verifying it:

    ```bash
    podman --version
    podman machine init
    ```


### Repository Setup

Clone the repository from GitHub:

```bash
git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
```

Navigate to the project directory:

```bash
cd Insight_Ingenious
```

### Profile Setup

1. **Create Your Profile.yaml:**

=== "Windows"

    Use PowerShell to create or edit `profiles.yml`:

    ```powershell
    # Create or edit profiles.yml using your default code editor
    # Follow the template at /conversation_pattern_example/profile.yml
    code $home\.ingenious\profiles.yml
    ```

=== "macOS"

    Set up the path for `profiles.yml`:

    ```bash
    export INGENIOUS_PROFILE="$HOME/.ingenious/profiles.yml"
    
    # Create or edit profiles.yml using a preferred text editor (e.g., nano, vim, or code)
    # Follow the template at /conversation_pattern_example/profile.yml
    code $INGENIOUS_PROFILE
    ```

### Build the Docker Image

There are two methods to build and run the Docker image:

=== "Simple SH"

    Run the installation script using PowerShell:

    ```powershell
    pwsh .\container_installation.ps1
    ```

=== "Alternative Method"

    Build the development Docker image using Podman:

    ```bash
    podman build -f ./docker/linux_development_image.dockerfile -t localhost/ingen_dev2 ./docker/
    ```

    After building the image, run the container using the PowerShell script:

    ```powershell
    pwsh .\run_image_in_podman.ps1
    ```
    ### Verify Running Containers

    Check the status of your containers to ensure everything is running correctly:
      
      ```bash
      podman ps -a
      ```
    This command displays a list of all running and stopped containers.



### Access the Container (Optional)

If you use the simple `Simple SH` deployment, the script will automatically SSH into the container.
The following steps will be optional. 

=== "Windows (VSCode)"

    To use Podman with the "Dev Containers" extension in Visual Studio Code:

    1. Open VSCode and navigate to Settings:
       - Press `Ctrl + ,` or `Cmd + ,` (on macOS) to open settings.
       - Search for `Dev Containers: Docker Path`.
       - Change the path from `docker` to `podman`.
    
    2. Open the Command Palette (`Ctrl + Shift + P` or `Cmd + Shift + P` on macOS).
       - Type `Dev Containers: Attach to Running Container...` and select your running Podman container.

    This configuration enables you to use Podman as the container runtime within VSCode's "Dev Containers" extension.

=== "Non-VSCode"

    You can access the running container directly via the command line:

    ```bash
    podman exec -it <container-id> /bin/bash
    ```

    Replace `<container-id>` with the ID or name of your running container.


### Run the Python Script Inside the Container

Now you can test your container setup by running the Python CLI (Fast API):

```bash
Write-Output "Running the Python CLI..."
python run_ingen_cli.py
```

### Open the Localhost URL

Open your browser and navigate to:

```
http://localhost:9000/docs
```

Or follow [how to use guide](./getting_started/how_to_use) for your first conversation in Python. 

