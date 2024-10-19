---

    weight: 2

---


# Installation

Follow these steps to set up the **Ingenious** package locally:



1. **pip install from Git**:
    ```bash
    pip install git+https://github.com/Insight-Services-APAC/Insight_Ingenious.git
    ```
    If you are using windows install the optional windows dependencies:
    ```bash
    pip install git+https://github.com/Insight-Services-APAC/Insight_Ingenious.git[windows]
    ```

    There are other optional dependencies that can be installed. For example, if you wish to include local chat summarization capabilities, you can install the optional `ChatHistorySummariser` dependencies. 

    ```bash
    pip install git+https://github.com/Insight-Services-APAC/Insight_Ingenious.git#[ChatHistorySummariser]
    ```
    These optional dependencies can be stacked together. For example, to install both the windows and chat summarization dependencies, you can run the following command:
    ```bash
    pip install git+https://github.com/Insight-Services-APAC/Insight_Ingenious.git#[windows,ChatHistorySummariser]
    ```

2. **Profile Setup**

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




