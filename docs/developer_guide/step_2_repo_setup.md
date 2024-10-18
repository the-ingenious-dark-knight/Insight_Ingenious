---

    weight: 4

---

# Step 2 - Setting Up the Repository

Follow these instructions to set up the **Ingenious** package on your local machine:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
    ```

2. **Navigate to the repository folder**:
    ```bash
    cd Insight_Ingenious
    ```

3. **Create a virtual environment**:
    ```bash
    python -m venv .venv
    ```

   4. **Activate the virtual environment**:
       
    === "Windows"
          ```bash
          .venv\Scripts\activate
          ```
    === "macOS"
          ```bash
          source .venv/bin/activate
          ```

5. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
!!! important
    Ensure you are using **pyautogen==0.2.35**, and confirm that **autogen-agents** is not installed in your environment.



6. **Local Profile Setup**
Please set up your OpenAI API by visiting [https://oai.azure.com/](https://oai.azure.com/).

<p style="text-align: center;">
    <img src="../images/oai_1.png" alt="OpenAI API Setup" width="800", height="300">
</p>

!!! important
    You will need to configure two types of deployments: a language model for completions and an embedding model for the current version.

<p style="text-align: center;">
    <img src="../images/oai_2.png" alt="OpenAI Deployment" width="800", height="200">
</p>


Once deployed, please put the credentials and configurations to the profile.yml as well as the config.yml:

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

