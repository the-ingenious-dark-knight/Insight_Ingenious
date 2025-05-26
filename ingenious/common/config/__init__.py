# Auto-generated __init__.py

def get_config(config_path=None, project_path=None):
    """
    Load the configuration from config.yml

    Args:
        config_path (str, optional): Path to the config.yml file.
        project_path (str, optional): Path to the project directory.

    Returns:
        config_ns_models.Config: Configuration object
    """
    from ingenious.common.config.config import Config
    return Config.get_config(config_path)
