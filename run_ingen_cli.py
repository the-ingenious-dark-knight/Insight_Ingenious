import ingenious.cli as cli
import ingenious.config.config as config
import threading
import time


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
cli_thread = threading.Thread(target=run_cli)
cli_thread.start()

# Give the server some time to start
time.sleep(1)
