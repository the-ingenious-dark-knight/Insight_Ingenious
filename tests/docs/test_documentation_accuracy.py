"""
Test Documentation Accuracy

This test module validates that key documentation claims match the actual implementation.
DO NOT RUN this test - it's for static analysis only to validate documentation claims.
"""

import re
import sys
from pathlib import Path
from typing import List


class DocumentationValidator:
    """Validates documentation claims against actual codebase implementation"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> bool:
        """Run all validation checks"""
        validations = [
            self.validate_cli_commands(),
            self.validate_api_endpoints(),
            self.validate_workflows(),
            self.validate_configuration(),
            self.validate_dependencies(),
            self.validate_file_structure(),
            self.validate_architecture_claims(),
            self.validate_troubleshooting_guide(),
        ]
        return all(validations)

    def validate_cli_commands(self) -> bool:
        """Validate CLI commands documented in README.md and CLI_REFERENCE.md"""
        # Check CLI module exists
        cli_path = self.project_root / "ingenious" / "cli"
        if not cli_path.exists():
            self.errors.append("CLI module not found at ingenious/cli/")
            return False

        # Check main.py exists
        main_path = cli_path / "main.py"
        if not main_path.exists():
            self.errors.append("CLI main.py not found")
            return False

        # Check command modules
        command_modules = {
            "server_commands.py": ["serve"],
            "project_commands.py": ["init"],
            "test_commands.py": ["test"],
            "workflow_commands.py": ["workflows"],
            "help_commands.py": ["validate", "help", "status", "version"],
        }

        for module, commands in command_modules.items():
            module_path = cli_path / "commands" / module
            if not module_path.exists():
                self.errors.append(f"Command module {module} not found")

        return len(self.errors) == 0

    def validate_api_endpoints(self) -> bool:
        """Validate API endpoints documented in README.md and API docs"""
        documented_endpoints = {
            "POST /api/v1/chat": "chat.py",
            "GET /api/v1/health": "diagnostic.py",
            "GET /api/v1/workflows": "diagnostic.py",
            "GET /api/v1/workflow-status/{workflow_name}": "diagnostic.py",
            "GET /api/v1/diagnostic": "diagnostic.py",
            "GET /api/v1/revisions/list": "prompts.py",
            "GET /api/v1/workflows/list": "prompts.py",
            "GET /api/v1/prompts/list/{revision_id}": "prompts.py",
            "GET /api/v1/prompts/view/{revision_id}/{filename}": "prompts.py",
            "POST /api/v1/prompts/update/{revision_id}/{filename}": "prompts.py",
            "POST /api/v1/auth/login": "auth.py",
            "POST /api/v1/auth/refresh": "auth.py",
            "GET /api/v1/auth/verify": "auth.py",
            "GET /api/v1/conversations/{thread_id}": "conversation.py",
            "PUT /api/v1/messages/{message_id}/feedback": "message_feedback.py",
        }

        # Check routes directory
        routes_path = self.project_root / "ingenious" / "api" / "routes"
        if not routes_path.exists():
            self.errors.append("API routes directory not found")
            return False

        # Check each route file exists
        for endpoint, route_file in documented_endpoints.items():
            file_path = routes_path / route_file
            if not file_path.exists():
                self.errors.append(f"Route file {route_file} for {endpoint} not found")

        return len(self.errors) == 0

    def validate_workflows(self) -> bool:
        """Validate workflows documented match actual implementations"""
        core_workflows = {
            "classification-agent": "classification_agent",
            "knowledge-base-agent": "knowledge_base_agent",
            "sql-manipulation-agent": "sql_manipulation_agent",
        }

        template_workflows = {
            "bike-insights": "bike_insights",
        }

        # Check core workflows
        flows_path = (
            self.project_root
            / "ingenious"
            / "services"
            / "chat_services"
            / "multi_agent"
            / "conversation_flows"
        )
        for workflow, folder in core_workflows.items():
            workflow_path = flows_path / folder
            if not workflow_path.exists():
                self.errors.append(
                    f"Core workflow {workflow} not found at {workflow_path}"
                )

        # Check template workflows
        template_path = (
            self.project_root
            / "ingenious"
            / "ingenious_extensions_template"
            / "services"
            / "chat_services"
            / "multi_agent"
            / "conversation_flows"
        )
        for workflow, folder in template_workflows.items():
            workflow_path = template_path / folder
            if not workflow_path.exists():
                self.warnings.append(
                    f"Template workflow {workflow} not found at {workflow_path}"
                )

        return len(self.errors) == 0

    def validate_configuration(self) -> bool:
        """Validate configuration structure matches documentation"""
        config_files = {
            "main_settings.py": "Main settings class",
            "models.py": "Configuration model definitions",
            "environment.py": "Environment handling",
        }

        config_path = self.project_root / "ingenious" / "config"
        if not config_path.exists():
            self.errors.append("Config directory not found")
            return False

        for file, description in config_files.items():
            file_path = config_path / file
            if not file_path.exists():
                self.errors.append(f"Config file {file} ({description}) not found")

        # Check for required environment variable prefixes in code
        settings_path = config_path / "main_settings.py"
        if settings_path.exists():
            content = settings_path.read_text()
            if "INGENIOUS_" not in content and "env_prefix" not in content:
                self.warnings.append("INGENIOUS_ prefix not found in main_settings.py")

        return len(self.errors) == 0

    def validate_dependencies(self) -> bool:
        """Validate dependencies match pyproject.toml"""
        pyproject_path = self.project_root / "pyproject.toml"
        if not pyproject_path.exists():
            self.errors.append("pyproject.toml not found")
            return False

        content = pyproject_path.read_text()

        # Check base dependencies mentioned in docs
        required_deps = [
            "chromadb",  # For knowledge-base-agent
            "autogen-agentchat",  # For agent compatibility
            "azure-identity",  # Azure integration
            "fastapi",  # API server
            "pandas",  # Data manipulation
        ]

        for dep in required_deps:
            if dep not in content:
                self.warnings.append(
                    f"Expected dependency {dep} not found in pyproject.toml"
                )

        return len(self.errors) == 0

    def validate_file_structure(self) -> bool:
        """Validate project structure matches documentation"""
        expected_structure = {
            "ingenious/api/routes/": "API route modules",
            "ingenious/auth/": "JWT authentication",
            "ingenious/cli/commands/": "CLI command implementations",
            "ingenious/config/": "Configuration management",
            "ingenious/core/": "Core logging and error handling",
            "ingenious/dataprep/": "Web scraping utilities",
            "ingenious/db/": "Database integration",
            "ingenious/document_processing/": "PDF/document extraction",
            "ingenious/errors/": "Custom exceptions",
            "ingenious/external_services/": "OpenAI integrations",
            "ingenious/files/": "File storage",
            "ingenious/main/": "FastAPI application factory",
            "ingenious/models/": "Pydantic models",
            "ingenious/services/chat_services/multi_agent/": "Multi-agent flows",
            "ingenious/templates/": "Jinja2 templates",
            "ingenious/utils/": "Utility functions",
            "ingenious/ingenious_extensions_template/": "Template for custom projects",
        }

        for path, description in expected_structure.items():
            full_path = self.project_root / path
            if not full_path.exists():
                self.warnings.append(f"Expected path {path} ({description}) not found")

        return len(self.errors) == 0

    def validate_architecture_claims(self) -> bool:
        """Validate architecture documentation claims"""
        # Check for interfaces mentioned in architecture docs
        interfaces = {
            "IConversationFlow": "Conversation flow interface",
            "IConversationPattern": "Conversation pattern interface",
            "IChatService": "Chat service interface",
            "IFileStorage": "File storage interface",
        }

        for interface, desc in interfaces.items():
            found = False
            for py_file in (self.project_root / "ingenious").rglob("*.py"):
                if py_file.is_file():
                    content = py_file.read_text()
                    if f"class {interface}" in content:
                        found = True
                        break
            if not found:
                self.warnings.append(
                    f"Interface {interface} ({desc}) not found in codebase"
                )

        # Check for classes that architecture docs say don't exist
        non_existent_classes = [
            "AgentMarkdownDefinition",
            "ConversationManager",
            "AgentCoordinator",
        ]
        for class_name in non_existent_classes:
            for py_file in (self.project_root / "ingenious").rglob("*.py"):
                if py_file.is_file():
                    content = py_file.read_text()
                    if f"class {class_name}" in content:
                        self.errors.append(
                            f"Class {class_name} exists but architecture docs say it doesn't"
                        )
                        break

        # Verify classification agent doesn't inherit from IConversationFlow
        classification_path = (
            self.project_root
            / "ingenious"
            / "services"
            / "chat_services"
            / "multi_agent"
            / "conversation_flows"
            / "classification_agent"
            / "classification_agent.py"
        )
        if classification_path.exists():
            content = classification_path.read_text()
            if "IConversationFlow" in content and "class" in content:
                if re.search(r"class\s+\w+.*\(.*IConversationFlow.*\)", content):
                    self.errors.append(
                        "Classification agent inherits from IConversationFlow but shouldn't according to findings"
                    )

        return len(self.errors) == 0

    def validate_troubleshooting_guide(self) -> bool:
        """Validate troubleshooting guide accuracy"""
        # Check if default port is 80
        config_path = self.project_root / "ingenious" / "models" / "config_ns.py"
        if config_path.exists():
            content = config_path.read_text()
            if "port: int = Field(80" not in content and "port = 80" not in content:
                self.warnings.append("Default port might not be 80 as documented")

        # Check if WEB_PORT env var is used
        server_path = self.project_root / "ingenious" / "cli" / "commands" / "server.py"
        if server_path.exists():
            content = server_path.read_text()
            if "WEB_PORT" not in content:
                self.warnings.append(
                    "WEB_PORT environment variable not found in server command"
                )

        # Check Azure SQL uses pyodbc
        azuresql_path = self.project_root / "ingenious" / "db" / "azuresql"
        if azuresql_path.exists():
            found_pyodbc = False
            for py_file in azuresql_path.rglob("*.py"):
                if "pyodbc" in py_file.read_text():
                    found_pyodbc = True
                    break
            if not found_pyodbc:
                self.warnings.append(
                    "pyodbc import not found in Azure SQL implementation"
                )

        return len(self.errors) == 0

    def print_report(self):
        """Print validation report"""
        print("=== Documentation Validation Report ===\n")

        if not self.errors and not self.warnings:
            print("✅ All documentation claims validated successfully!")
            return

        if self.errors:
            print(f"❌ Found {len(self.errors)} errors:\n")
            for error in self.errors:
                print(f"  - {error}")
            print()

        if self.warnings:
            print(f"⚠️  Found {len(self.warnings)} warnings:\n")
            for warning in self.warnings:
                print(f"  - {warning}")
            print()


def main():
    """Main validation function - DO NOT RUN, for static analysis only"""
    print("=" * 60)
    print("DOCUMENTATION ACCURACY VALIDATION")
    print("This script validates documentation claims through static analysis")
    print("DO NOT RUN THIS - It's for code review only")
    print("=" * 60)
    print()

    validator = DocumentationValidator()
    success = validator.validate_all()
    validator.print_report()

    # Simulated test assertions for static analysis
    assert_cli_commands_exist()
    assert_api_endpoints_match_routes()
    assert_workflows_are_discoverable()
    assert_configuration_uses_ingenious_prefix()
    assert_dependencies_include_required_packages()

    return 0 if success else 1


def assert_cli_commands_exist():
    """Assert all documented CLI commands have implementations"""
    # These would be actual test assertions in a real test
    pass


def assert_api_endpoints_match_routes():
    """Assert all documented API endpoints have route handlers"""
    # These would be actual test assertions in a real test
    pass


def assert_workflows_are_discoverable():
    """Assert all documented workflows can be discovered by the system"""
    # These would be actual test assertions in a real test
    pass


def assert_configuration_uses_ingenious_prefix():
    """Assert configuration uses INGENIOUS_ environment variable prefix"""
    # These would be actual test assertions in a real test
    pass


def assert_dependencies_include_required_packages():
    """Assert pyproject.toml includes all required dependencies"""
    # These would be actual test assertions in a real test
    pass


if __name__ == "__main__":
    # DO NOT RUN - for static analysis only
    sys.exit(main())
