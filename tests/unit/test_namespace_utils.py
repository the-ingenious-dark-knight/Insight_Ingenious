from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from ingenious.utils.namespace_utils import (
    _importer,
    get_dir_roots,
    get_file_from_namespace_with_fallback,
    get_inbuilt_api_routes,
    get_namespaces,
    get_path_from_namespace_with_fallback,
    normalize_workflow_name,
    print_namespace_modules,
)


@pytest.mark.unit
class TestNamespaceUtils:
    """Test namespace utility functions"""

    def test_normalize_workflow_name_with_hyphens(self):
        """Test normalizing workflow name with hyphens"""
        result = normalize_workflow_name("bike-insights")
        assert result == "bike_insights"

    def test_normalize_workflow_name_with_underscores(self):
        """Test normalizing workflow name with underscores"""
        result = normalize_workflow_name("bike_insights")
        assert result == "bike_insights"

    def test_normalize_workflow_name_mixed_case(self):
        """Test normalizing workflow name with mixed case"""
        result = normalize_workflow_name("Bike-Insights")
        assert result == "bike_insights"

    def test_normalize_workflow_name_empty(self):
        """Test normalizing empty workflow name"""
        result = normalize_workflow_name("")
        assert result == ""

    def test_normalize_workflow_name_none(self):
        """Test normalizing None workflow name"""
        result = normalize_workflow_name(None)
        assert result is None

    def test_get_namespaces(self):
        """Test getting list of namespaces"""
        namespaces = get_namespaces()
        expected = [
            "ingenious_extensions",
            "ingenious.ingenious_extensions_template",
            "ingenious",
        ]
        assert namespaces == expected

    @patch("ingenious.utils.namespace_utils.Path.exists")
    @patch("ingenious.utils.namespace_utils.get_paths")
    def test_get_dir_roots(self, mock_get_paths, mock_exists):
        """Test getting directory roots"""
        mock_get_paths.return_value = {"purelib": "/path/to/site-packages"}
        mock_exists.return_value = True

        with patch("ingenious.utils.namespace_utils.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/current/working/dir")

            dirs = get_dir_roots()

            assert len(dirs) == 3
            assert str(dirs[0]).endswith("ingenious_extensions")
            assert str(dirs[1]).endswith("ingenious_extensions_template")
            assert str(dirs[2]).endswith("ingenious")

    @patch("ingenious.utils.namespace_utils.get_paths")
    def test_get_inbuilt_api_routes_working_dir(self, mock_get_paths):
        """Test getting inbuilt API routes from working directory"""
        mock_get_paths.return_value = {"purelib": "/path/to/site-packages"}

        with (
            patch("ingenious.utils.namespace_utils.os.getcwd") as mock_getcwd,
            patch("pathlib.Path.exists") as mock_exists,
        ):
            mock_getcwd.return_value = "/current/working/dir"
            mock_exists.return_value = True

            result = get_inbuilt_api_routes()

            assert result is not None
            assert str(result).endswith("api/routes")

    @patch("ingenious.utils.namespace_utils.get_dir_roots")
    def test_get_file_from_namespace_with_fallback_success(self, mock_get_dir_roots):
        """Test successful file retrieval with fallback"""
        mock_dir = Path("/test/dir")
        mock_get_dir_roots.return_value = [mock_dir]

        file_content = "test file content"

        with (
            patch.object(Path, "exists", return_value=True),
            patch("builtins.open", mock_open(read_data=file_content)),
        ):
            result = get_file_from_namespace_with_fallback(
                "test.module", "test_file.txt"
            )

            assert result == file_content

    @patch("ingenious.utils.namespace_utils.get_dir_roots")
    def test_get_file_from_namespace_with_fallback_file_not_found(
        self, mock_get_dir_roots
    ):
        """Test file retrieval with fallback when file not found"""
        mock_dir = Path("/test/dir")
        mock_get_dir_roots.return_value = [mock_dir]

        with patch("ingenious.utils.namespace_utils.os.path.exists") as mock_exists:
            mock_exists.return_value = False

            result = get_file_from_namespace_with_fallback(
                "test.module", "test_file.txt"
            )

            assert result is None

    @patch("ingenious.utils.namespace_utils.get_dir_roots")
    def test_get_path_from_namespace_with_fallback_success(self, mock_get_dir_roots):
        """Test successful path retrieval with fallback"""
        mock_dir = Path("/test/dir")
        mock_get_dir_roots.return_value = [mock_dir]

        with patch.object(Path, "exists", return_value=True):
            result = get_path_from_namespace_with_fallback("test/path")

            assert result == mock_dir / "test/path"

    @patch("ingenious.utils.namespace_utils.get_dir_roots")
    def test_get_path_from_namespace_with_fallback_not_found(self, mock_get_dir_roots):
        """Test path retrieval with fallback when path not found"""
        mock_dir = Path("/test/dir")
        mock_get_dir_roots.return_value = [mock_dir]

        with patch("ingenious.utils.namespace_utils.os.path.exists") as mock_exists:
            mock_exists.return_value = False

            result = get_path_from_namespace_with_fallback("test/path")

            assert result is None

    def test_print_namespace_modules_with_package(self):
        """Test printing namespace modules for a package"""
        # Test with a real package that we know exists
        import contextlib
        import io

        # Capture stdout to verify the function works
        captured_output = io.StringIO()

        # Use a real package for testing
        with contextlib.redirect_stdout(captured_output):
            print_namespace_modules(
                "unittest"
            )  # unittest is a real package with modules

        output = captured_output.getvalue()

        # Verify that the function found and printed some modules
        # unittest package has several modules like case, loader, mock, etc.
        assert "Found module:" in output

        # Check for some known unittest modules
        known_modules = ["case", "mock", "loader", "result"]
        found_any = any(module in output for module in known_modules)
        assert found_any, (
            f"Expected to find at least one of {known_modules} in output: {output}"
        )

    def test_print_namespace_modules_without_package(self):
        """Test printing namespace modules for a non-package"""
        with patch.object(_importer, "import_module") as mock_import_module:
            # Mock module without __path__ attribute by using spec
            mock_module_spec = Mock(spec=[])
            mock_import_module.return_value = mock_module_spec

            # Just verify the function runs without error
            print_namespace_modules("test.namespace")

            # Verify the mock was called appropriately
            mock_import_module.assert_called_once_with("test.namespace")
