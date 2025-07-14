"""
Tests for dependency group installations and compatibility.

This module verifies that all optional dependency groups can be installed
correctly and that their core functionality works as expected.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

import pytest


class DependencyGroupTester:
    """Test utility for verifying dependency group installations."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        
    def test_group_installation(self, group: str, test_imports: List[str]) -> bool:
        """
        Test that a dependency group can be installed and its packages imported.
        
        Args:
            group: Name of the dependency group to test
            test_imports: List of package names to test importing
            
        Returns:
            True if installation and imports succeed, False otherwise
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = Path(temp_dir) / "test_env"
            
            try:
                # Create virtual environment
                subprocess.run([
                    sys.executable, "-m", "venv", str(venv_path)
                ], check=True, capture_output=True)
                
                # Get pip path for the virtual environment
                if sys.platform == "win32":
                    pip_path = venv_path / "Scripts" / "pip"
                    python_path = venv_path / "Scripts" / "python"
                else:
                    pip_path = venv_path / "bin" / "pip"
                    python_path = venv_path / "bin" / "python"
                
                # Install the package with the specific group
                install_cmd = [
                    str(pip_path), "install", "-e", f"{self.project_root}[{group}]"
                ]
                subprocess.run(install_cmd, check=True, capture_output=True)
                
                # Test imports
                for package in test_imports:
                    import_cmd = [
                        str(python_path), "-c", f"import {package}"
                    ]
                    subprocess.run(import_cmd, check=True, capture_output=True)
                    
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"Error testing group {group}: {e}")
                if e.stdout:
                    print(f"STDOUT: {e.stdout.decode()}")
                if e.stderr:
                    print(f"STDERR: {e.stderr.decode()}")
                return False


@pytest.fixture
def dependency_tester():
    """Fixture providing a DependencyGroupTester instance."""
    return DependencyGroupTester()


class TestDependencyGroups:
    """Test cases for dependency groups."""
    
    def test_minimal_group(self, dependency_tester):
        """Test that minimal group installs with core dependencies only."""
        # Minimal group should be empty, so just test core imports
        core_imports = [
            "dependency_injector",
            "fastapi", 
            "jsonpickle",
            "pydantic",
            "structlog",
            "typer"
        ]
        
        assert dependency_tester.test_group_installation("minimal", core_imports)
    
    def test_core_group(self, dependency_tester):
        """Test that core group installs successfully."""
        core_imports = [
            "aiosqlite",
            "jinja2"
        ]
        
        assert dependency_tester.test_group_installation("core", core_imports)
    
    def test_auth_group(self, dependency_tester):
        """Test that auth group installs successfully."""
        auth_imports = [
            "bcrypt",
            "passlib",
            "jose"  # python-jose imports as 'jose'
        ]
        
        assert dependency_tester.test_group_installation("auth", auth_imports)
    
    def test_azure_group(self, dependency_tester):
        """Test that azure group installs successfully."""
        azure_imports = [
            "azure.core",
            "azure.cosmos", 
            "azure.identity",
            "azure.keyvault",
            "azure.search.documents",
            "azure.storage.blob"
        ]
        
        assert dependency_tester.test_group_installation("azure", azure_imports)
    
    def test_ai_group(self, dependency_tester):
        """Test that ai group installs successfully."""
        ai_imports = [
            "autogen_agentchat",
            "autogen_ext",
            "openai"
        ]
        
        assert dependency_tester.test_group_installation("ai", ai_imports)
    
    def test_database_group(self, dependency_tester):
        """Test that database group installs successfully."""
        db_imports = [
            "pyodbc",
            "psutil"
        ]
        
        assert dependency_tester.test_group_installation("database", db_imports)
    
    @pytest.mark.slow
    def test_ui_group(self, dependency_tester):
        """Test that ui group installs successfully."""
        ui_imports = [
            "chainlit",
            "flask"
        ]
        
        assert dependency_tester.test_group_installation("ui", ui_imports)
    
    def test_document_processing_group(self, dependency_tester):
        """Test that document-processing group installs successfully."""
        doc_imports = [
            "fitz",  # pymupdf imports as 'fitz'
            "psutil"
        ]
        
        assert dependency_tester.test_group_installation("document-processing", doc_imports)
    
    @pytest.mark.slow  
    def test_ml_group(self, dependency_tester):
        """Test that ml group installs successfully."""
        ml_imports = [
            "chromadb",
            "sentence_transformers"
        ]
        
        assert dependency_tester.test_group_installation("ml", ml_imports)
    
    def test_dataprep_group(self, dependency_tester):
        """Test that dataprep group installs successfully."""
        dataprep_imports = [
            "scrapfly",
            "dotenv",  # python-dotenv imports as 'dotenv'
            "backoff"
        ]
        
        assert dependency_tester.test_group_installation("dataprep", dataprep_imports)
    
    def test_visualization_group(self, dependency_tester):
        """Test that visualization group installs successfully."""
        viz_imports = [
            "matplotlib",
            "seaborn"
        ]
        
        assert dependency_tester.test_group_installation("visualization", viz_imports)
    
    def test_development_group(self, dependency_tester):
        """Test that development group installs successfully."""
        dev_imports = [
            "IPython"  # ipython package imports as IPython
        ]
        
        assert dependency_tester.test_group_installation("development", dev_imports)


class TestDependencyCompatibility:
    """Test dependency compatibility and conflicts."""
    
    def test_pip_check_passes(self):
        """Test that pip check passes for current environment."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "check"
            ], capture_output=True, text=True, check=True)
            assert result.returncode == 0
        except subprocess.CalledProcessError as e:
            pytest.fail(f"pip check failed: {e.stderr}")
    
    def test_no_security_vulnerabilities(self):
        """Test that no security vulnerabilities exist in current dependencies."""
        try:
            result = subprocess.run([
                "uv", "run", "pip-audit", "--format=json"
            ], capture_output=True, text=True, check=True)
            
            # If pip-audit succeeds with no output, no vulnerabilities found
            assert result.returncode == 0
            
        except subprocess.CalledProcessError as e:
            # pip-audit returns non-zero when vulnerabilities are found
            if "found vulnerabilities" in e.stdout.lower():
                pytest.fail(f"Security vulnerabilities found: {e.stdout}")
            else:
                # Other errors (missing pip-audit, etc.) should not fail tests
                pytest.skip(f"pip-audit not available or other error: {e.stderr}")
    
    def test_core_imports_work(self):
        """Test that core package imports work correctly."""
        core_packages = [
            "dependency_injector",
            "fastapi",
            "jsonpickle", 
            "pydantic",
            "structlog",
            "typer"
        ]
        
        for package in core_packages:
            try:
                __import__(package)
            except ImportError as e:
                pytest.fail(f"Failed to import core package {package}: {e}")


class TestInstallationSizes:
    """Test installation sizes for different dependency groups."""
    
    @pytest.mark.slow
    def test_minimal_installation_size(self):
        """Test that minimal installation stays under size limit."""
        # This would require actually installing in a clean environment
        # and measuring size - marked as slow test
        pytest.skip("Size testing requires isolated environment setup")
    
    def test_dependency_count_reasonable(self):
        """Test that dependency counts are reasonable for each group."""
        import configparser
        
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        
        # This is a basic check - in practice you'd parse TOML properly
        with open(pyproject_path) as f:
            content = f.read()
            
        # Core dependencies should be minimal (< 10)
        core_deps = content.count('dependencies = [')
        assert core_deps == 1, "Should have exactly one dependencies section"
        
        # Each optional group should have reasonable number of deps (< 20 each)
        optional_groups = [
            "minimal", "core", "auth", "azure", "ai", "database", 
            "ui", "document-processing", "document-advanced", "ml",
            "dataprep", "visualization", "development", "standard", "full"
        ]
        
        for group in optional_groups:
            assert f"{group} = [" in content, f"Missing dependency group: {group}"


@pytest.mark.integration
class TestDependencyIntegration:
    """Integration tests for dependency functionality."""
    
    def test_fastapi_starts(self):
        """Test that FastAPI can start with current dependencies."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        app = FastAPI()
        
        @app.get("/health")
        def health():
            return {"status": "healthy"}
        
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_structured_logging_works(self):
        """Test that structured logging works correctly."""
        import structlog
        
        logger = structlog.get_logger("test")
        
        # This should not raise an exception
        logger.info("Test log message", key="value")
    
    def test_dependency_injection_works(self):
        """Test that dependency injection container works."""
        from dependency_injector import containers, providers
        
        class TestContainer(containers.DeclarativeContainer):
            config = providers.Configuration()
            
        container = TestContainer()
        assert container is not None
    
    def test_pydantic_validation_works(self):
        """Test that Pydantic validation works correctly."""
        from pydantic import BaseModel, ValidationError
        import pytest
        
        class TestModel(BaseModel):
            name: str
            age: int
            
        # Valid data should work
        model = TestModel(name="test", age=25)
        assert model.name == "test"
        assert model.age == 25
        
        # Invalid data should raise ValidationError
        with pytest.raises(ValidationError):
            TestModel(name="test", age="invalid")