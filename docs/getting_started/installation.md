---

    weight: 2
    
---

# Installation Guide

## System Setup


### PowerShell Installation

=== "Windows"

    Install PowerShell using the Windows Package Manager (Winget):

    ```bash
    winget install --id Microsoft.PowerShell --source winget
    ```
    Verify installation PowerShell 7+:

    ```bash
    pwsh --version
    ```

=== "macOS"

    Install PowerShell using Homebrew:

    ```bash
    brew install --cask powershell
    ```

    Verify installation PowerShell 7.4.5:

    ```bash
    pwsh --version
    ```
!!! tip
    Please run all command using the latest version of PowerShell (pwsh) to ensure cross-platform compatibility. 



### Container Setup (Podman)

=== "Windows"

    To install Podman on Windows, follow these steps:

    1. Download the Podman installer from the official website: [Podman Windows Installer](https://podman.io/getting-started/installation).
    2. Run the installer and follow the on-screen instructions to complete the setup.
    3. After installation, run below command in your terminal:

    ```powershell    
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


## Repository Setup

Clone the repository from GitHub:

```bash
git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
```

Navigate to the project directory and get the latest release:

```bash
cd Insight_Ingenious

git checkout v0.0.1
```

### Profile Setup
1. Please set up your OpenAI API by visiting [https://oai.azure.com/](https://oai.azure.com/) and [developer_guide](/developer_guide/step_2_repo_setup)

2. Create Your [profiles.yml](../profile_file):

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

## Build the Docker Image

There are two methods to build and run the Docker image:

=== "Simple SH"

    Run the installation script using PowerShell:

    ```powershell
    pwsh .\run_container_installation_dev.ps1
    ```
    or 

    ```powershell
    pwsh .\run_container_installation_prod.ps1
    ```
    if want deploy with a client site. 


    !!! tip
        The default parameter for the installer is:

        ```powershell
            param (
            [string]$podman_path = "C:\Program Files\Podman\bin\podman.exe",
            [string]$image_name = "localhost/ingen_dev_ubuntu",
            [string]$container_name = "ingen_dev_ubuntu",
            [string]$dockerfile_path = "./docker/development_images/linux_development_image_ubuntu.dockerfile"
        
        ```
         you can modify it for difference images and base container. 

=== "Alternative Method"

    Build the development Docker image using Podman:

    ```powershell
    podman build -f ./docker/linux_development_image.dockerfile -t localhost/ingen_dev2 ./docker/
    ```

    After building the image, run the container using the PowerShell script:

    ```powershell
    pwsh .\run_image_in_podman.ps1
    ```
    ### Verify Running Containers

    Check the status of your containers to ensure everything is running correctly:
      
      ```powershell
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

    ```powershell
    podman exec -it <container-id> /bin/bash
    ```

    Replace `<container-id>` with the ID or name of your running container.


## Run Tests

Now you can test your container setup:

=== "Fast API"
    ```powershell
    python run_ingen_cli.py
    ```

    Open your browser and navigate to, to authenticate, click `Authorize`, and using Web Configuration credentials in profile.yaml.
    
    ```
    http://localhost:9000/docs
    ```
    
    Click on `POST`, then select `Try it Out`, and enter the following request for testing:
    ```
    {
      "thread_id": "sample",
      "user_prompt": "Tell me about basketball?",
      "user_id": "testuser123",
      "user_name": "testuser",
      "topic": "basketball, tennis, soccer",
      "memory_record": true,
      "conversation_flow": "classification_agent"
    }
    ```
    Please refer to [service prefabs](/developer_guide/service_prefabs) for available conversation flows. 


=== "Http Test"
    In one Terminal:
  
    While your session from run_ingen_cli.py is still active, **OPEN** another Terminal and SSH into the container:

    ```powershell
    python run_tests_http.py
    ```

=== "Python Test File"

     Follow [how to use guide](./getting_started/how_to_use) for your first conversation in Python. 

