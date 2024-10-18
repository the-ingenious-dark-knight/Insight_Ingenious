---

    weight: 2

---

# Step 1 - System Setup

This section outlines the applications required for developing using the dbt framework, and provides instructions for both macOS and Windows. The applications include:

- Python (latest version)
- Visual Studio Code or PyCharm
- Git for Windows/macOS

## Install Python 3.12

=== "MacOS"

      1. Open your Terminal (you can find it by searching in Spotlight or navigating to `/Applications/Utilities/Terminal.app`).
      2. Install Python 3.12 using Homebrew (make sure Homebrew is installed). Run the following command:
         ```bash
         brew install python@3.12
         ```
      3. Once installation is complete, verify the installation by running:
         ```bash
         python3 --version
         ```
         You should see `Python 3.12.x` as the output.

=== "Windows"

   1. Open PowerShell as an Administrator (press `WindowsKey + X`, then select PowerShell (Admin)).
   2. Download and install Python 3.12 from the official Python website by running:
      ```powershell
      Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe -OutFile python-3.12.0.exe
      Start-Process -FilePath .\python-3.12.0.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait
      ```
   3. After installation, verify the installation by running:
      ```powershell
      python --version
      ```
      You should see `Python 3.12.x` as the output.

## Install Visual Studio Code  (Optional)

=== "MacOS"

      1. Open Terminal and install Visual Studio Code using Homebrew:
         ```bash
         brew install --cask visual-studio-code
         ```
      Alternatively, you can download and install it manually from [Visual Studio Code](https://code.visualstudio.com/).
         2. To verify installation, launch Visual Studio Code from the Terminal:
            ```bash
            code .
            ```
=== "Windows"

      1. Download Visual Studio Code from [Visual Studio Code](https://code.visualstudio.com/).
      2. Install it by following the default installation options.
      3. After installation, you can open PowerShell and type:
            ```powershell
            code .
            ```

## Install and Configure Git

=== "MacOS"

      1. Open Terminal and install Git using Homebrew:
      ```bash
      brew install git
      ```
      2. After installation, confirm Git is installed by running:
         ```bash
         git --version
         ```

=== "Windows"

      1. Open PowerShell and download Git using the following command:
      ```powershell
      Invoke-WebRequest -Uri https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.1/Git-2.42.0-64-bit.exe -OutFile git-installer.exe
      Start-Process -FilePath .\git-installer.exe -ArgumentList '/SILENT' -Wait
      ```
      2. Verify the installation by running:
         ```powershell
         git --version
         ```

Once Git is installed, configure it to use Visual Studio Code as your default editor and set the terminal to use PowerShell (on Windows) or Terminal (on macOS).

=== "macOS"

      1. Open Terminal and configure Git to use Visual Studio Code as the default editor:
         ```bash
         git config --global core.editor "code --wait"
         ```
      
=== "Windows"

      1. Open PowerShell and configure Git to use Visual Studio Code as the default editor:
      ```powershell
      git config --global core.editor "code --wait"
      ```
      2. Ensure Git uses PowerShell by running:
         ```powershell
         git config --global core.autocrlf true
         ```

The rest of the installation options should be standard unless you need to change them for other reasons.

