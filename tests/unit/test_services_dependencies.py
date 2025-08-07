"""
Tests for ingenious.services.dependencies module
"""
import pytest
import base64
from unittest.mock import Mock, patch, mock_open
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBasicCredentials, HTTPAuthorizationCredentials

from ingenious.services.dependencies import (
    get_di_container,
    get_config,
    get_openai_service,
    get_chat_history_repository,
    get_chat_service,
    get_message_feedback_service,
    get_file_storage_data,
    get_file_storage_revisions,
    get_project_config,
    get_security_service,
    get_security_service_optional,
    get_auth_user,
    get_conditional_security,
    sync_templates
)


class TestBasicDependencies:
    """Test cases for basic dependency injection functions"""

    def test_module_docstring(self):
        """Test that the module has appropriate documentation"""
        import ingenious.services.dependencies as deps_module
        docstring = deps_module.__doc__
        assert docstring is not None
        assert "FastAPI dependency injection" in docstring

    def test_module_constants(self):
        """Test that module constants are properly configured"""
        import ingenious.services.dependencies as deps_module
        assert hasattr(deps_module, 'logger')
        assert hasattr(deps_module, 'security')
        assert hasattr(deps_module, 'bearer_security')

    @patch('ingenious.services.dependencies.get_container')
    def test_get_di_container(self, mock_get_container):
        """Test get_di_container function"""
        mock_container = Mock()
        mock_get_container.return_value = mock_container
        
        result = get_di_container()
        
        mock_get_container.assert_called_once()
        assert result is mock_container

    def test_get_config(self):
        """Test get_config function"""
        mock_container = Mock()
        mock_config = Mock()
        mock_container.config.return_value = mock_config
        
        result = get_config(mock_container)
        
        mock_container.config.assert_called_once()
        assert result is mock_config

    def test_get_openai_service(self):
        """Test get_openai_service function"""
        mock_container = Mock()
        mock_service = Mock()
        mock_container.openai_service.return_value = mock_service
        
        result = get_openai_service(mock_container)
        
        mock_container.openai_service.assert_called_once()
        assert result is mock_service

    def test_get_chat_history_repository(self):
        """Test get_chat_history_repository function"""
        mock_container = Mock()
        mock_repo = Mock()
        mock_container.chat_history_repository.return_value = mock_repo
        
        result = get_chat_history_repository(mock_container)
        
        mock_container.chat_history_repository.assert_called_once()
        assert result is mock_repo

    def test_get_chat_service(self):
        """Test get_chat_service function"""
        mock_container = Mock()
        mock_service = Mock()
        mock_container.chat_service_factory.return_value = mock_service
        
        result = get_chat_service(mock_container)
        
        mock_container.chat_service_factory.assert_called_once_with(conversation_flow="")
        assert result is mock_service

    def test_get_message_feedback_service(self):
        """Test get_message_feedback_service function"""
        mock_container = Mock()
        mock_service = Mock()
        mock_container.message_feedback_service.return_value = mock_service
        
        result = get_message_feedback_service(mock_container)
        
        mock_container.message_feedback_service.assert_called_once()
        assert result is mock_service

    def test_get_file_storage_data(self):
        """Test get_file_storage_data function"""
        mock_container = Mock()
        mock_storage = Mock()
        mock_container.file_storage_data.return_value = mock_storage
        
        result = get_file_storage_data(mock_container)
        
        mock_container.file_storage_data.assert_called_once()
        assert result is mock_storage

    def test_get_file_storage_revisions(self):
        """Test get_file_storage_revisions function"""
        mock_container = Mock()
        mock_storage = Mock()
        mock_container.file_storage_revisions.return_value = mock_storage
        
        result = get_file_storage_revisions(mock_container)
        
        mock_container.file_storage_revisions.assert_called_once()
        assert result is mock_storage

    def test_get_project_config(self):
        """Test get_project_config function"""
        mock_container = Mock()
        mock_config = Mock()
        mock_container.config.return_value = mock_config
        
        result = get_project_config(mock_container)
        
        mock_container.config.assert_called_once()
        assert result is mock_config


class TestSecurityService:
    """Test cases for security service functions"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_config = Mock()
        self.mock_config.web_configuration.authentication.enable = True
        self.mock_config.web_configuration.authentication.username = "testuser"
        self.mock_config.web_configuration.authentication.password = "testpass"

    def test_get_security_service_auth_disabled(self):
        """Test get_security_service when authentication is disabled"""
        self.mock_config.web_configuration.authentication.enable = False
        
        with patch('ingenious.services.dependencies.logger') as mock_logger:
            result = get_security_service(config=self.mock_config)
            
            assert result == "anonymous"
            mock_logger.warning.assert_called_once()

    @patch('ingenious.services.dependencies.get_username_from_token')
    def test_get_security_service_jwt_token_valid(self, mock_get_username):
        """Test get_security_service with valid JWT token"""
        mock_token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        mock_get_username.return_value = "jwt_user"
        
        result = get_security_service(token=mock_token, config=self.mock_config)
        
        assert result == "jwt_user"
        mock_get_username.assert_called_once_with("valid_token")

    @patch('ingenious.services.dependencies.get_username_from_token')
    def test_get_security_service_jwt_token_invalid_fallback_to_basic(self, mock_get_username):
        """Test get_security_service with invalid JWT token, fallback to basic auth"""
        mock_token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
        mock_get_username.side_effect = HTTPException(status_code=401, detail="Invalid token")
        
        credentials = HTTPBasicCredentials(username="testuser", password="testpass")
        
        result = get_security_service(token=mock_token, credentials=credentials, config=self.mock_config)
        
        assert result == "testuser"

    def test_get_security_service_basic_auth_valid(self):
        """Test get_security_service with valid basic auth"""
        credentials = HTTPBasicCredentials(username="testuser", password="testpass")
        
        result = get_security_service(credentials=credentials, config=self.mock_config)
        
        assert result == "testuser"

    def test_get_security_service_basic_auth_invalid_username(self):
        """Test get_security_service with invalid username"""
        credentials = HTTPBasicCredentials(username="wronguser", password="testpass")
        
        with pytest.raises(HTTPException) as exc_info:
            get_security_service(credentials=credentials, config=self.mock_config)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in exc_info.value.detail

    def test_get_security_service_basic_auth_invalid_password(self):
        """Test get_security_service with invalid password"""
        credentials = HTTPBasicCredentials(username="testuser", password="wrongpass")
        
        with pytest.raises(HTTPException) as exc_info:
            get_security_service(credentials=credentials, config=self.mock_config)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_security_service_no_credentials(self):
        """Test get_security_service with no credentials"""
        with pytest.raises(HTTPException) as exc_info:
            get_security_service(config=self.mock_config)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authentication required" in exc_info.value.detail


class TestSecurityServiceOptional:
    """Test cases for optional security service"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_config = Mock()
        self.mock_config.web_configuration.authentication.enable = True
        self.mock_config.web_configuration.authentication.username = "testuser"
        self.mock_config.web_configuration.authentication.password = "testpass"

    def test_get_security_service_optional_auth_disabled(self):
        """Test get_security_service_optional when authentication is disabled"""
        self.mock_config.web_configuration.authentication.enable = False
        
        with patch('ingenious.services.dependencies.logger') as mock_logger:
            result = get_security_service_optional(config=self.mock_config)
            
            assert result is None
            mock_logger.warning.assert_called_once()

    def test_get_security_service_optional_valid_credentials(self):
        """Test get_security_service_optional with valid credentials"""
        credentials = HTTPBasicCredentials(username="testuser", password="testpass")
        
        result = get_security_service_optional(credentials=credentials, config=self.mock_config)
        
        assert result == "testuser"

    def test_get_security_service_optional_no_credentials(self):
        """Test get_security_service_optional with no credentials"""
        with pytest.raises(HTTPException) as exc_info:
            get_security_service_optional(config=self.mock_config)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthUser:
    """Test cases for get_auth_user function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_config = Mock()
        self.mock_config.web_configuration.authentication.enable = True
        self.mock_config.web_configuration.authentication.username = "testuser" 
        self.mock_config.web_configuration.authentication.password = "testpass"

    def test_get_auth_user_auth_disabled(self):
        """Test get_auth_user when authentication is disabled"""
        self.mock_config.web_configuration.authentication.enable = False
        mock_request = Mock()
        
        with patch('ingenious.services.dependencies.logger') as mock_logger:
            result = get_auth_user(mock_request, self.mock_config)
            
            assert result == "anonymous"
            mock_logger.warning.assert_called_once()

    @patch('ingenious.services.dependencies.get_username_from_token')
    def test_get_auth_user_jwt_token_valid(self, mock_get_username):
        """Test get_auth_user with valid JWT Bearer token"""
        mock_request = Mock()
        mock_request.headers.get.return_value = "Bearer valid_token"
        mock_get_username.return_value = "jwt_user"
        
        result = get_auth_user(mock_request, self.mock_config)
        
        assert result == "jwt_user"
        mock_get_username.assert_called_once_with("valid_token")

    @patch('ingenious.services.dependencies.get_username_from_token')
    def test_get_auth_user_jwt_invalid_fallback_to_basic(self, mock_get_username):
        """Test get_auth_user with invalid JWT, fallback to basic auth"""
        mock_request = Mock()
        basic_auth = base64.b64encode(b"testuser:testpass").decode()
        mock_request.headers.get.return_value = f"Basic {basic_auth}"
        mock_get_username.side_effect = HTTPException(status_code=401, detail="Invalid token")
        
        result = get_auth_user(mock_request, self.mock_config)
        
        assert result == "testuser"

    def test_get_auth_user_basic_auth_valid(self):
        """Test get_auth_user with valid Basic Auth"""
        mock_request = Mock()
        basic_auth = base64.b64encode(b"testuser:testpass").decode()
        mock_request.headers.get.return_value = f"Basic {basic_auth}"
        
        result = get_auth_user(mock_request, self.mock_config)
        
        assert result == "testuser"

    def test_get_auth_user_basic_auth_invalid_format(self):
        """Test get_auth_user with invalid Basic Auth format"""
        mock_request = Mock()
        mock_request.headers.get.return_value = "Basic invalid_base64"
        
        with pytest.raises(HTTPException) as exc_info:
            get_auth_user(mock_request, self.mock_config)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_auth_user_basic_auth_invalid_credentials(self):
        """Test get_auth_user with invalid Basic Auth credentials"""
        mock_request = Mock()
        basic_auth = base64.b64encode(b"wronguser:wrongpass").decode()
        mock_request.headers.get.return_value = f"Basic {basic_auth}"
        
        with pytest.raises(HTTPException) as exc_info:
            get_auth_user(mock_request, self.mock_config)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_auth_user_no_auth_header(self):
        """Test get_auth_user with no authorization header"""
        mock_request = Mock()
        mock_request.headers.get.return_value = ""
        
        with pytest.raises(HTTPException) as exc_info:
            get_auth_user(mock_request, self.mock_config)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_conditional_security(self):
        """Test get_conditional_security wrapper function"""
        mock_request = Mock()
        self.mock_config.web_configuration.authentication.enable = False
        
        with patch('ingenious.services.dependencies.get_auth_user', return_value="test_user") as mock_get_auth:
            result = get_conditional_security(mock_request, self.mock_config)
            
            assert result == "test_user"
            mock_get_auth.assert_called_once_with(mock_request, self.mock_config)


class TestSyncTemplates:
    """Test cases for sync_templates function"""

    def test_sync_templates_local_storage(self):
        """Test sync_templates with local storage type"""
        mock_config = Mock()
        mock_config.file_storage.revisions.storage_type = "local"
        
        # Should return early without doing anything
        result = sync_templates(mock_config)
        assert result is None

    @patch('asyncio.run')
    @patch('ingenious.services.dependencies.FileStorage')
    @patch('os.getcwd')
    @patch('os.path.join')
    @patch('builtins.open', mock_open())
    def test_sync_templates_non_local_storage(self, mock_join, mock_getcwd, mock_fs_class, mock_asyncio_run):
        """Test sync_templates with non-local storage"""
        mock_config = Mock()
        mock_config.file_storage.revisions.storage_type = "azure"
        
        mock_getcwd.return_value = "/working/dir"
        mock_join.side_effect = lambda *args: "/".join(args)
        
        # Mock FileStorage instance
        mock_fs = Mock()
        mock_fs_class.return_value = mock_fs
        
        sync_templates(mock_config)
        
        # Verify FileStorage was created
        mock_fs_class.assert_called_once_with(mock_config)
        
        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()

    def test_all_dependency_functions_have_docstrings(self):
        """Test that all dependency functions have proper docstrings"""
        functions_to_test = [
            get_di_container,
            get_config,
            get_openai_service,
            get_chat_history_repository,
            get_chat_service,
            get_message_feedback_service,
            get_file_storage_data,
            get_file_storage_revisions,
            get_project_config,
            get_security_service,
            get_security_service_optional,
            get_auth_user,
            get_conditional_security,
            sync_templates
        ]
        
        for func in functions_to_test:
            assert func.__doc__ is not None, f"{func.__name__} should have a docstring"
            assert len(func.__doc__.strip()) > 0, f"{func.__name__} docstring should not be empty"