---

    weight: 2

---


# Installation

Follow these steps to set up the **Ingenious** package locally:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
    ```

2. **pip Install**:
    ```bash
    pip install dist/ingenious*.whl
    ```

3. **Profile Setup**

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




