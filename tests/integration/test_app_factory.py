"""
Integration tests for modular FastAPI application factory.

Tests that the refactored main application components work together correctly
and maintain the same functionality as the original monolithic structure.
"""

import os
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ingenious.config import create_minimal_config
from ingenious.main import FastAgentAPI, create_app
from ingenious.main.app_factory import FastAgentAPI as NewFastAgentAPI
from ingenious.main.exception_handlers import ExceptionHandlers
from ingenious.main.middleware import RequestContextMiddleware
from ingenious.main.routing import RouteManager


class TestAppFactory:
    """Test the application factory functions."""

    def test_create_app_function(self):
        """Test that create_app function works correctly."""
        config = create_minimal_config()
        
        with patch.dict(os.environ, {"INGENIOUS_WORKING_DIR": "/tmp"}):
            app = create_app(config)
            assert isinstance(app, FastAPI)
            assert app.title == "FastAgent API"
            assert app.version == "1.0.0"

    def test_fast_agent_api_initialization(self):
        """Test FastAgentAPI class initialization."""
        config = create_minimal_config()
        
        with patch.dict(os.environ, {"INGENIOUS_WORKING_DIR": "/tmp"}):
            api = NewFastAgentAPI(config)
            assert isinstance(api.app, FastAPI)
            assert hasattr(api, 'container')
            assert api.config == config


class TestMiddleware:
    """Test middleware functionality."""

    def test_request_context_middleware_creation(self):
        """Test that RequestContextMiddleware can be instantiated."""
        middleware = RequestContextMiddleware()
        assert middleware is not None

    def test_middleware_integration(self):
        """Test middleware is properly integrated into the app."""
        config = create_minimal_config()
        
        with patch.dict(os.environ, {"INGENIOUS_WORKING_DIR": "/tmp"}):
            app = create_app(config)
            
            # Check that middleware is added
            middleware_classes = [type(middleware) for middleware in app.user_middleware]
            middleware_names = [cls.__name__ for cls in middleware_classes]
            assert any("RequestContextMiddleware" in name for name in middleware_names)


class TestExceptionHandlers:
    """Test exception handler functionality."""

    def test_exception_handlers_registration(self):
        """Test that exception handlers can be registered."""
        app = FastAPI()
        ExceptionHandlers.register_handlers(app)
        
        # Verify handlers are registered
        assert Exception in app.exception_handlers
        
        from fastapi.exceptions import RequestValidationError
        assert RequestValidationError in app.exception_handlers

    def test_status_code_mapping(self):
        """Test error to status code mapping."""
        from ingenious.errors import AuthenticationError, DatabaseError, RequestValidationError
        
        # Test various error types
        auth_error = AuthenticationError("Test auth error")
        assert ExceptionHandlers._get_status_code_for_error(auth_error) == 401
        
        db_error = DatabaseError("Test db error")
        assert ExceptionHandlers._get_status_code_for_error(db_error) == 503
        
        validation_error = RequestValidationError("Test validation error")
        assert ExceptionHandlers._get_status_code_for_error(validation_error) == 422


class TestRouting:
    """Test route management functionality."""

    def test_route_manager_builtin_routes(self):
        """Test that built-in routes are registered correctly."""
        app = FastAPI()
        RouteManager.register_builtin_routes(app)
        
        # Check that routes are registered
        routes = [route.path for route in app.routes]
        assert any("/api/v1/auth" in route for route in routes)
        assert any("/api/v1" in route for route in routes)

    def test_route_manager_all_routes(self):
        """Test that all routes are registered."""
        config = create_minimal_config()
        app = FastAPI()
        
        RouteManager.register_all_routes(app, config)
        
        # Verify routes exist
        routes = [route.path for route in app.routes]
        assert len(routes) > 0


class TestAppIntegration:
    """Integration tests for the complete application."""

    def test_app_basic_functionality(self):
        """Test basic app functionality with test client."""
        config = create_minimal_config()
        
        with patch.dict(os.environ, {"INGENIOUS_WORKING_DIR": "/tmp"}):
            app = create_app(config)
            client = TestClient(app)
            
            # Test root redirect
            response = client.get("/", allow_redirects=False)
            assert response.status_code == 307  # Redirect status
            assert response.headers["location"] == "/docs"
            
            # Test docs endpoint (should exist)
            response = client.get("/docs")
            assert response.status_code == 200

    def test_api_endpoints_exist(self):
        """Test that expected API endpoints exist."""
        config = create_minimal_config()
        
        with patch.dict(os.environ, {"INGENIOUS_WORKING_DIR": "/tmp"}):
            app = create_app(config)
            client = TestClient(app)
            
            # Test that diagnostic endpoint exists (even if it returns an error)
            response = client.get("/api/v1/diagnostic")
            assert response.status_code in [200, 401, 422, 500]  # Any valid HTTP status

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is properly configured."""
        config = create_minimal_config()
        
        with patch.dict(os.environ, {"INGENIOUS_WORKING_DIR": "/tmp"}):
            app = create_app(config)
            client = TestClient(app)
            
            # Test CORS headers on options request
            response = client.options("/api/v1/diagnostic", headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            })
            
            # Should have CORS headers or handle the request appropriately
            assert response.status_code in [200, 204, 405]


class TestBackwardCompatibility:
    """Test backward compatibility with original main.py structure."""

    def test_old_imports_still_work(self):
        """Test that old import paths still work with deprecation warnings."""
        # Test that we can still import from the old location
        with pytest.warns(DeprecationWarning):
            from ingenious.main import FastAgentAPI as OldFastAgentAPI
            assert OldFastAgentAPI is not None

    def test_get_config_function_exists(self):
        """Test that get_config function is still available."""
        from ingenious.main import get_config
        
        with patch.dict(os.environ, {
            "INGENIOUS_PROJECT_PATH": "",
            "AZURE_OPENAI_API_KEY": "test-key",
            "AZURE_OPENAI_BASE_URL": "https://test.openai.azure.com/",
        }):
            config = get_config()
            assert config is not None


class TestOptionalServices:
    """Test optional service configuration."""

    def test_prompt_tuner_disabled(self):
        """Test app creation with prompt tuner disabled."""
        config = create_minimal_config()
        config.prompt_tuner.enable = False
        
        with patch.dict(os.environ, {"INGENIOUS_WORKING_DIR": "/tmp"}):
            app = create_app(config)
            assert isinstance(app, FastAPI)

    def test_chainlit_disabled(self):
        """Test app creation with chainlit disabled."""
        config = create_minimal_config()
        config.chainlit_configuration.enable = False
        
        with patch.dict(os.environ, {"INGENIOUS_WORKING_DIR": "/tmp"}):
            app = create_app(config)
            assert isinstance(app, FastAPI)


class TestConfigurationVariations:
    """Test app creation with different configuration variations."""

    def test_different_web_config(self):
        """Test app creation with different web configuration."""
        config = create_minimal_config()
        config.web_configuration.port = 9000
        config.web_configuration.ip_address = "127.0.0.1"
        
        with patch.dict(os.environ, {"INGENIOUS_WORKING_DIR": "/tmp"}):
            app = create_app(config)
            assert isinstance(app, FastAPI)

    def test_authentication_enabled(self):
        """Test app creation with authentication enabled."""
        config = create_minimal_config()
        config.web_configuration.authentication.enable = True
        config.web_configuration.authentication.username = "test"
        config.web_configuration.authentication.password = "test123"
        
        with patch.dict(os.environ, {"INGENIOUS_WORKING_DIR": "/tmp"}):
            app = create_app(config)
            assert isinstance(app, FastAPI)