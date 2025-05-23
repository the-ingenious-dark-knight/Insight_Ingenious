def test_config_is_working():
    """Test that our Config implementation is actually working."""
    # Create a test config file
    from pathlib import Path

    import yaml

    from ingenious.common.config.config import Config

    # Create a temporary directory
    temp_dir = Path(".tmp-test")
    temp_dir.mkdir(exist_ok=True)

    # Create a config file
    config_path = temp_dir / "config.yml"
    with open(config_path, "w") as f:
        yaml.dump(
            {
                "profile": "test",
                "models": [
                    {
                        "name": "test-model",
                        "model": "gpt-3.5-turbo",
                        "base_url": "https://example.com/openai",
                        "api_key": "test-api-key",
                        "api_version": "2023-05-15",
                    }
                ],
                "file_storage": {
                    "storage_type": "local",
                    "path": "./storage",
                    "containers": [
                        {"name": "data", "path": "./data"},
                        {"name": "revisions", "path": "./revisions"},
                    ],
                },
                "chat_history": {
                    "database_type": "sqlite",
                    "connection_string": ":memory:",
                },
                "chat_service": {"type": "basic"},
                "web_configuration": {
                    "authentication": {
                        "enable": False,
                        "username": "admin",
                        "password": "password",
                    }
                },
            },
            f,
        )

    # Try to get config
    try:
        config = Config.get_config(str(config_path))
        assert config is not None
        import shutil

        shutil.rmtree(temp_dir)
    except Exception as e:
        import shutil

        shutil.rmtree(temp_dir)
        raise e
