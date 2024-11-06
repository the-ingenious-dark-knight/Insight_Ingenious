---

    weight: 4

---

## Chainlit Setup

**Navigate to the `Insight_Ingenious` Root Folder of the Container**  
This folder contains all the necessary files required to run the conversation test script. Use the following command:

```powershell
cd ..
```

This command will move you one level up from your current directory into the `Insight_Ingenious` folder, assuming it is located in the parent directory.

### Authentication Configuration

To configure authentication for Chainlit using OAuth with GitHub, you'll need to set the following environment variables. Refer to the official Chainlit documentation for OAuth setup: [Chainlit OAuth Documentation](https://docs.chainlit.io/authentication/oauth).

```powershell
export OAUTH_GITHUB_CLIENT_SECRET="<secret>"
export OAUTH_GITHUB_CLIENT_ID="<client_id>"
export CHAINLIT_AUTH_SECRET="<secret>"
```

Make sure to replace `<secret>` and `<client_id>` with your actual GitHub OAuth credentials.

### Locate and Modify `chainlit_test.py`

Next, locate the `chainlit_test.py` file. You will need to modify the conversation pattern used in the script. Open the file and look for the following code snippet:

```python
    async def main(message: cl.Message):
        user: cl.User = cl.user_session.get('user')
        new_guid = uuid.uuid4()
        chat_request: ChatRequest = ChatRequest(
            thread_id=str(new_guid),
            user_id="test",
            user_prompt="",
            user_name="test",
            topic="",
            memory_record=True,
            conversation_flow=<pattern>  # Change the pattern here
        )
```

Replace `<pattern>` with the desired conversation flow pattern you wish to implement.

### Running the Script

Finally, you can run the Chainlit test script using the following command:

```powershell
chainlit run chainlit_test.py
```

This will start the Chainlit server, and you can interact with the conversation test as configured.

