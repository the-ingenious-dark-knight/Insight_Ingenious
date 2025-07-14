"""Unit tests for the dependency injection container."""

import os
import pytest
from unittest.mock import Mock, patch

from ingenious.services.container import (
    Container,
    get_container,
    init_container,
    configure_for_testing,
    override_for_testing,
    reset_overrides,
)


class TestDependencyContainer:
    """Test cases for the dependency injection container."""

    def test_container_singleton(self):
        """Test that get_container returns the same instance."""
        container1 = get_container()
        container2 = get_container()
        assert container1 is container2

    def test_container_initialization(self):
        """Test container initialization."""
        container = init_container()
        assert container is not None
        assert hasattr(container, 'config')
        assert hasattr(container, 'chat_history_repository')
        assert hasattr(container, 'openai_service')

    @patch.dict(os.environ, {"INGENIOUS_PROFILE_PATH": "/test/path"})
    def test_config_provider(self):
        """Test config provider works correctly."""
        container = Container()
        with patch("ingenious.services.container._get_config") as mock_get_config:
            mock_config = Mock()
            mock_get_config.return_value = mock_config
            
            config = container.config()
            assert config is mock_config
            mock_get_config.assert_called_once()

    def test_profile_provider(self):
        """Test profile provider works correctly."""
        container = Container()
        with patch("ingenious.services.container.Profiles") as mock_profiles:
            mock_profile = Mock()
            mock_profiles.return_value = mock_profile
            
            profile = container.profile()
            assert profile is mock_profile

    def test_openai_service_provider(self):
        """Test OpenAI service provider configuration."""
        container = Container()
        
        # Mock config with model settings
        mock_config = Mock()
        mock_model = Mock()
        mock_model.base_url = "https://test.openai.azure.com"
        mock_model.api_key = "test-key"
        mock_model.api_version = "2024-02-01"
        mock_model.model = "gpt-4"
        mock_config.models = [mock_model]
        
        with patch.object(container.config, '__call__', return_value=mock_config):
            with patch("ingenious.services.container.OpenAIService") as mock_openai:
                mock_service = Mock()
                mock_openai.return_value = mock_service
                
                service = container.openai_service()
                
                mock_openai.assert_called_once_with(
                    azure_endpoint="https://test.openai.azure.com",
                    api_key="test-key",
                    api_version="2024-02-01",
                    open_ai_model="gpt-4"
                )

    def test_chat_history_repository_provider(self):
        """Test chat history repository provider."""
        container = Container()
        
        # Mock config
        mock_config = Mock()
        mock_config.chat_history.database_type = "sqlite"
        
        with patch.object(container.config, '__call__', return_value=mock_config):
            with patch("ingenious.services.container.ChatHistoryRepository") as mock_repo:
                with patch("ingenious.services.container._get_database_type") as mock_db_type:
                    from ingenious.db.chat_history_repository import DatabaseClientType
                    mock_db_type.return_value = DatabaseClientType.SQLITE
                    
                    mock_repository = Mock()
                    mock_repo.return_value = mock_repository
                    
                    repo = container.chat_history_repository()
                    
                    mock_repo.assert_called_once()
                    assert repo is mock_repository

    def test_file_storage_providers(self):
        """Test file storage providers for data and revisions."""
        container = Container()
        
        mock_config = Mock()
        
        with patch.object(container.config, '__call__', return_value=mock_config):
            with patch("ingenious.services.container.FileStorage") as mock_storage:
                mock_data_storage = Mock()
                mock_revisions_storage = Mock()
                mock_storage.side_effect = [mock_data_storage, mock_revisions_storage]
                
                data_storage = container.file_storage_data()
                revisions_storage = container.file_storage_revisions()
                
                assert mock_storage.call_count == 2
                assert data_storage is mock_data_storage
                assert revisions_storage is mock_revisions_storage

    def test_chat_service_factory(self):
        """Test chat service factory provider."""
        container = Container()
        
        mock_config = Mock()
        mock_config.chat_service.type = "multi_agent"
        mock_repo = Mock()
        
        with patch.object(container.config, '__call__', return_value=mock_config):
            with patch.object(container.chat_history_repository, '__call__', return_value=mock_repo):
                with patch("ingenious.services.container._create_chat_service") as mock_create:
                    mock_service = Mock()
                    mock_create.return_value = mock_service
                    
                    service = container.chat_service_factory()
                    
                    mock_create.assert_called_once_with(
                        config=mock_config,
                        chat_history_repository=mock_repo
                    )

    def test_message_feedback_service_provider(self):
        """Test message feedback service provider."""
        container = Container()
        
        mock_repo = Mock()
        
        with patch.object(container.chat_history_repository, '__call__', return_value=mock_repo):
            with patch("ingenious.services.container.MessageFeedbackService") as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                
                service = container.message_feedback_service()
                
                mock_service_class.assert_called_once_with(
                    chat_history_repository=mock_repo
                )

    def test_configure_for_testing(self):
        """Test testing configuration setup."""
        container = configure_for_testing()
        assert container is not None
        
        # Verify that OpenAI service is mocked
        openai_service = container.openai_service()
        assert isinstance(openai_service, Mock)

    def test_override_for_testing(self):
        """Test manual provider overrides for testing."""
        container = get_container()
        
        # Create mock override
        mock_config = Mock()
        mock_config.test_setting = "test_value"
        
        # Override config
        override_for_testing(config=mock_config)
        
        # Verify override works
        config = container.config()
        assert config is mock_config
        assert config.test_setting == "test_value"
        
        # Reset overrides
        reset_overrides()

    def test_reset_overrides(self):
        """Test resetting all container overrides."""
        container = get_container()
        
        # Set an override
        mock_service = Mock()
        override_for_testing(openai_service=mock_service)
        
        # Verify override is active
        service = container.openai_service()
        assert service is mock_service
        
        # Reset overrides
        reset_overrides()
        
        # Verify override is cleared (this should create a new instance)
        # Note: We can't directly test this without a real config,
        # but we can verify the reset method doesn't error


class TestDatabaseTypeHelper:
    """Test cases for database type helper function."""

    def test_get_database_type_valid(self):
        """Test getting valid database type."""
        from ingenious.services.container import _get_database_type
        from ingenious.db.chat_history_repository import DatabaseClientType
        
        mock_config = Mock()
        mock_config.chat_history.database_type = "sqlite"
        
        db_type = _get_database_type(mock_config)
        assert db_type == DatabaseClientType.SQLITE

    def test_get_database_type_invalid(self):
        """Test getting invalid database type raises error."""
        from ingenious.services.container import _get_database_type
        from ingenious.errors import ConfigurationError
        
        mock_config = Mock()
        mock_config.chat_history.database_type = "invalid_type"
        
        with pytest.raises(ConfigurationError) as exc_info:
            _get_database_type(mock_config)
        
        assert "Unknown database type: invalid_type" in str(exc_info.value)


class TestChatServiceFactory:
    """Test cases for chat service factory function."""

    def test_create_chat_service(self):
        """Test chat service creation."""
        from ingenious.services.container import _create_chat_service
        
        mock_config = Mock()
        mock_config.chat_service.type = "multi_agent"
        mock_repo = Mock()
        
        with patch("ingenious.services.container.ChatService") as mock_chat_service:
            mock_service = Mock()
            mock_chat_service.return_value = mock_service
            
            service = _create_chat_service(
                config=mock_config,
                chat_history_repository=mock_repo,
                conversation_flow="test_flow"
            )
            
            mock_chat_service.assert_called_once_with(
                chat_service_type="multi_agent",
                chat_history_repository=mock_repo,
                conversation_flow="test_flow",
                config=mock_config
            )
            assert service is mock_service


class TestSecurityServiceFactory:
    """Test cases for security service factory function."""

    def test_create_security_service(self):
        """Test security service configuration creation."""
        from ingenious.services.container import _create_security_service
        
        mock_config = Mock()
        mock_config.web_configuration.authentication.enable = True
        mock_config.web_configuration.authentication.username = "test_user"
        mock_config.web_configuration.authentication.password = "test_pass"
        
        security_config = _create_security_service(mock_config)
        
        expected = {
            "config": mock_config,
            "authentication_enabled": True,
            "username": "test_user",
            "password": "test_pass",
        }
        
        assert security_config == expected