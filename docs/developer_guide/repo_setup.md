---

    weight: 2

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
Ensure you are using **pyautogen==0.2.35**, and confirm that **autogen-agents** is not already installed in your environment.