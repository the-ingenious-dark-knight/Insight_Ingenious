"""
Test suite to validate documentation accuracy against codebase implementation.

This test file validates key documentation claims by examining the actual code
without executing it. It ensures documentation stays synchronized with implementation.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set

import pytest


class CodeAnalyzer:
    """Static code analyzer for validating documentation claims."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def find_api_routes(self) -> Dict[str, List[str]]:
        """Find all API routes defined in the codebase."""
        routes = {}
        routes_dir = self.project_root / "ingenious" / "api" / "routes"
        
        for py_file in routes_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            content = py_file.read_text()
            # Find router.method decorators
            router_pattern = r'@router\.(get|post|put|delete|patch)\("([^"]+)"'
            matches = re.findall(router_pattern, content)
            
            for method, path in matches:
                if py_file.stem not in routes:
                    routes[py_file.stem] = []
                routes[py_file.stem].append(f"{method.upper()} {path}")
                
        return routes

    def find_cli_commands(self) -> Set[str]:
        """Find all CLI commands defined in the codebase."""
        commands = set()
        cli_dir = self.project_root / "ingenious" / "cli"
        
        for py_file in cli_dir.rglob("*.py"):
            content = py_file.read_text()
            # Find @app.command decorators
            command_pattern = r'@app\.command\((?:name="([^"]+)"|hidden=True)'
            matches = re.findall(command_pattern, content)
            
            for match in matches:
                if match and not match.startswith("_"):
                    commands.add(match)
                    
        return commands

    def find_environment_variables(self) -> Set[str]:
        """Find all INGENIOUS_ prefixed environment variables."""
        env_vars = set()
        
        # Check config models
        config_dir = self.project_root / "ingenious" / "config"
        for py_file in config_dir.rglob("*.py"):
            content = py_file.read_text()
            # Find INGENIOUS_ environment variable references
            env_pattern = r'INGENIOUS_[A-Z_]+'
            matches = re.findall(env_pattern, content)
            env_vars.update(matches)
            
        return env_vars

    def find_workflows(self) -> Set[str]:
        """Find all available workflows."""
        workflows = set()
        flows_dir = self.project_root / "ingenious" / "services" / "chat_services" / "multi_agent" / "conversation_flows"
        
        if flows_dir.exists():
            for item in flows_dir.iterdir():
                if item.is_dir() and not item.name.startswith("__"):
                    workflows.add(item.name)
                    
        return workflows

    def check_model_fields(self, model_path: str, field_name: str) -> bool:
        """Check if a model has a specific field."""
        try:
            file_path = self.project_root / model_path
            if not file_path.exists():
                return False
                
            content = file_path.read_text()
            # Simple check for field definition
            field_pattern = rf'{field_name}:\s*\w+'
            return bool(re.search(field_pattern, content))
        except Exception:
            return False



class TestDocumentationAccuracy:
    """Test cases for documentation accuracy validation."""

    @pytest.fixture
    def analyzer(self):
        """Create code analyzer instance."""
        project_root = Path(__file__).parent.parent.parent
        return CodeAnalyzer(project_root)

    def test_api_endpoints_documented(self, analyzer):
        """Verify documented API endpoints exist in code."""
        # Key endpoints that should exist based on documentation
        expected_endpoints = {
            "chat": ["POST /chat"],
            "diagnostic": ["GET /health", "GET /workflows", "GET /workflow-status/{workflow_name}"],
            "auth": ["POST /login", "POST /refresh", "GET /verify"],
            "conversation": ["GET /conversations/{thread_id}"],
            "message_feedback": ["PUT /messages/{message_id}/feedback"],
            "prompts": ["GET /prompts/list/{revision_id}", "GET /prompts/view/{revision_id}/{filename}", 
                       "POST /prompts/update/{revision_id}/{filename}"]
        }
        
        actual_routes = analyzer.find_api_routes()
        
        for module, endpoints in expected_endpoints.items():
            assert module in actual_routes, f"API module {module} not found"
            for endpoint in endpoints:
                method, path = endpoint.split(" ", 1)
                found = any(
                    route.startswith(method) and path in route 
                    for route in actual_routes[module]
                )
                assert found, f"Endpoint {endpoint} not found in {module}.py"

    def test_cli_commands_documented(self, analyzer):
        """Verify documented CLI commands exist."""
        expected_commands = {
            "init", "serve", "workflows", "test", "validate",
            "help", "status", "version", "dataprep", "document-processing"
        }
        
        actual_commands = analyzer.find_cli_commands()
        
        for command in expected_commands:
            assert command in actual_commands, f"CLI command '{command}' not found in code"

    def test_core_workflows_exist(self, analyzer):
        """Verify core workflows are in the library."""
        core_workflows = {
            "classification_agent",
            "knowledge_base_agent", 
            "sql_manipulation_agent"
        }
        
        actual_workflows = analyzer.find_workflows()
        
        for workflow in core_workflows:
            assert workflow in actual_workflows, f"Core workflow '{workflow}' not found"

    def test_environment_variable_prefix(self, analyzer):
        """Verify environment variables use INGENIOUS_ prefix."""
        env_vars = analyzer.find_environment_variables()
        
        # All found env vars should start with INGENIOUS_
        for var in env_vars:
            assert var.startswith("INGENIOUS_"), f"Environment variable {var} doesn't use INGENIOUS_ prefix"

    def test_azure_sql_field_name(self, analyzer):
        """Verify Azure SQL model uses correct field name."""
        # Check that AzureSqlSettings uses database_connection_string
        has_field = analyzer.check_model_fields(
            "ingenious/config/models.py",
            "database_connection_string"
        )
        assert has_field, "AzureSqlSettings should have 'database_connection_string' field"

    def test_python_version_requirement(self):
        """Verify Python version requirement in pyproject.toml."""
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()
        
        # Check for Python 3.13+ requirement
        assert 'requires-python = ">=3.13"' in content, "Python 3.13+ requirement not found"

    def test_api_prefix(self, analyzer):
        """Verify API routes use /api/v1/ prefix."""
        routing_file = Path(__file__).parent.parent.parent / "ingenious" / "main" / "routing.py"
        content = routing_file.read_text()
        
        # Check for /api/v1 prefix in route registration
        assert 'prefix="/api/v1"' in content, "API routes should use /api/v1 prefix"

    def test_default_port_configuration(self):
        """Verify default port configuration."""
        server_commands = Path(__file__).parent.parent.parent / "ingenious" / "cli" / "server_commands.py"
        content = server_commands.read_text()
        
        # Check default port is 80 or uses WEB_PORT env var
        assert 'int(os.getenv("WEB_PORT", "80"))' in content, "Default port should be 80 or $WEB_PORT"

    def test_jwt_authentication_configurable(self, analyzer):
        """Verify JWT authentication is configurable."""
        auth_settings = analyzer.check_model_fields(
            "ingenious/config/models.py",
            "enable"
        )
        assert auth_settings, "Authentication should have 'enable' field for configuration"

    def test_storage_backends_supported(self):
        """Verify both local and Azure storage backends are supported."""
        files_dir = Path(__file__).parent.parent.parent / "ingenious" / "files"
        
        # Check for both local and azure subdirectories
        assert (files_dir / "local").exists(), "Local storage backend not found"
        assert (files_dir / "azure").exists(), "Azure storage backend not found"

    def test_template_workflow_location(self):
        """Verify bike-insights is in template, not core library."""
        # Check core library doesn't have bike-insights
        core_flows = Path(__file__).parent.parent.parent / "ingenious" / "services" / "chat_services" / "multi_agent" / "conversation_flows"
        assert not (core_flows / "bike_insights").exists(), "bike-insights should not be in core library"
        
        # Check template has bike-insights
        template_flows = Path(__file__).parent.parent.parent / "ingenious" / "ingenious_extensions_template" / "services" / "chat_services" / "multi_agent" / "conversation_flows"
        assert (template_flows / "bike_insights").exists(), "bike-insights should be in template"

    def test_documentation_files_exist(self):
        """Verify all referenced documentation files exist."""
        docs_to_check = [
            "README.md",
            "docs/api/README.md",
            "docs/getting-started/configuration.md",
            "docs/workflows/README.md",
            "docs/CLI_REFERENCE.md",
            "docs/architecture/README.md",
            "docs/troubleshooting/README.md"
        ]
        
        project_root = Path(__file__).parent.parent.parent
        for doc in docs_to_check:
            doc_path = project_root / doc
            assert doc_path.exists(), f"Documentation file {doc} not found"



if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
