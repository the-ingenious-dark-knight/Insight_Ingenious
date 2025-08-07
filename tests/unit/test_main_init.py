"""
Tests for ingenious.main.__init__ module
"""

import ingenious.main


class TestMainInit:
    """Test cases for main __init__ module"""

    def test_module_docstring(self):
        """Test that the module has appropriate documentation"""
        docstring = ingenious.main.__doc__
        assert docstring is not None
        assert "Main application factory and components" in docstring
        assert "FastAPI application factory" in docstring

    def test_expected_exports(self):
        """Test that the module exports expected components"""
        expected_exports = [
            "FastAgentAPI",
            "create_app",
            "ExceptionHandlers",
            "RequestContextMiddleware",
            "RouteManager",
        ]

        assert hasattr(ingenious.main, "__all__")
        assert ingenious.main.__all__ == expected_exports

    def test_all_exports_are_accessible(self):
        """Test that all exported components are accessible"""
        for export in ingenious.main.__all__:
            assert hasattr(ingenious.main, export)
            assert getattr(ingenious.main, export) is not None

    def test_fast_agent_api_import(self):
        """Test that FastAgentAPI is imported correctly"""
        assert hasattr(ingenious.main, "FastAgentAPI")
        from ingenious.main.app_factory import FastAgentAPI

        assert ingenious.main.FastAgentAPI is FastAgentAPI

    def test_create_app_import(self):
        """Test that create_app is imported correctly"""
        assert hasattr(ingenious.main, "create_app")
        from ingenious.main.app_factory import create_app

        assert ingenious.main.create_app is create_app

    def test_exception_handlers_import(self):
        """Test that ExceptionHandlers is imported correctly"""
        assert hasattr(ingenious.main, "ExceptionHandlers")
        from ingenious.main.exception_handlers import ExceptionHandlers

        assert ingenious.main.ExceptionHandlers is ExceptionHandlers

    def test_request_context_middleware_import(self):
        """Test that RequestContextMiddleware is imported correctly"""
        assert hasattr(ingenious.main, "RequestContextMiddleware")
        from ingenious.main.middleware import RequestContextMiddleware

        assert ingenious.main.RequestContextMiddleware is RequestContextMiddleware

    def test_route_manager_import(self):
        """Test that RouteManager is imported correctly"""
        assert hasattr(ingenious.main, "RouteManager")
        from ingenious.main.routing import RouteManager

        assert ingenious.main.RouteManager is RouteManager

    def test_module_structure(self):
        """Test the overall module structure"""
        # Verify the module has the expected structure
        assert hasattr(ingenious.main, "__name__")
        assert hasattr(ingenious.main, "__doc__")
        assert hasattr(ingenious.main, "__all__")

    def test_import_without_error(self):
        """Test that the module can be imported without errors"""
        # This test passes if the import at the top succeeds
        import ingenious.main as main_module

        assert main_module is not None

    def test_all_imports_are_classes_or_functions(self):
        """Test that all imported components are classes or functions"""
        for export_name in ingenious.main.__all__:
            export_obj = getattr(ingenious.main, export_name)

            # Each export should be either a class or a function
            assert (
                isinstance(export_obj, type)  # class
                or callable(export_obj)  # function
            ), f"{export_name} should be a class or callable function"

    def test_module_name_correct(self):
        """Test that module name is correct"""
        assert ingenious.main.__name__ == "ingenious.main"

    def test_imports_from_correct_modules(self):
        """Test that imports come from the expected submodules"""
        # Test that imports are from the correct submodules
        from ingenious.main import app_factory, exception_handlers, middleware, routing

        # These modules should exist and be importable
        assert app_factory is not None
        assert exception_handlers is not None
        assert middleware is not None
        assert routing is not None
