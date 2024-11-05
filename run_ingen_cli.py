import os
from pathlib import Path

import ingenious.cli as cli
import ingenious.config.config as config

os.environ["INGENIOUS_WORKING_DIR"] = str(Path(os.getcwd()))
# Make sure you have set the environment variables 
_config: config.Config = config.get_config()


def run_cli():
    cli.run_all(
        profile_dir=None,  # This is set by your environment variables
        project_dir=None,  # This is set by your environment variables
        host=_config.web_configuration.ip_address,
        port=_config.web_configuration.port
    )


# Start the cli.run_all function in a separate thread
run_cli()

# Create an instance of the FastAgentAPI class
# fast_agent_api = FastAgentAPI()

# Access the FastAPI app instance
# app = fast_agent_api.app
# uvicorn.run(app, host=_config.web_configuration.ip_address, port=_config.web_configuration.port)
