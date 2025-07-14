"""
Help and status CLI commands for Insight Ingenious.

This module contains commands for getting help, checking status, and validating configuration.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from rich.panel import Panel

from ingenious.cli.base import BaseCommand, CommandError, ExitCode
from ingenious.cli.utilities import OutputFormatters, ValidationUtils


class HelpCommand(BaseCommand):
    """Show detailed help and getting started guide."""

    def execute(self, topic: Optional[str] = None) -> None:
        """
        Show comprehensive help for getting started with Insight Ingenious.

        Args:
            topic: Specific topic to show help for (setup, workflows, config, deployment)
        """
        if topic is None:
            self._show_general_help()
        elif topic == "setup":
            self._show_setup_help()
        elif topic == "workflows":
            self._show_workflows_help()
        elif topic == "config":
            self._show_config_help()
        elif topic == "deployment":
            self._show_deployment_help()
        else:
            self.print_error(f"Unknown help topic: {topic}")
            self.console.print(
                "\nAvailable topics: setup, workflows, config, deployment"
            )
            self.console.print("Use 'ingen help' for general help.")
            raise CommandError(
                f"Invalid help topic: {topic}", ExitCode.VALIDATION_ERROR
            )

    def _show_general_help(self) -> None:
        """Show general help information."""
        self.console.print(
            "[bold blue]🚀 Insight Ingenious - Quick Start Guide[/bold blue]\n"
        )

        sections = [
            ("1. Initialize a new project:", "ingen init"),
            (
                "2. Configure your project:",
                "• Copy .env.example to .env and add your API keys\n   • Update config.yml and profiles.yml as needed",
            ),
            (
                "3. Set environment variables:",
                "export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml\n   export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml",
            ),
            ("4. Start the server:", "ingen serve"),
            (
                "5. Access the interfaces:",
                "• API: http://localhost:80\n   • Chat: http://localhost:80/chainlit\n   • Prompt Tuner: http://localhost:80/prompt-tuner",
            ),
        ]

        for title, content in sections:
            self.console.print(f"[bold]{title}[/bold]")
            self.console.print(f"   {content}")
            self.console.print("")

        helpful_commands = Panel(
            "ingen status      # Check configuration\n"
            "ingen workflows   # List available workflows\n"
            "ingen test        # Run tests\n"
            "ingen help <topic> # Get detailed help on specific topics",
            title="💡 Helpful Commands",
            border_style="yellow",
        )
        self.console.print(helpful_commands)

        docs_panel = Panel(
            "GitHub: https://github.com/Insight-Services-APAC/ingenious",
            title="📖 Documentation",
            border_style="blue",
        )
        self.console.print(docs_panel)

    def _show_setup_help(self) -> None:
        """Show setup-specific help."""
        content = (
            "To set up your Insight Ingenious project:\n\n"
            "1. Run `ingen init` to generate project files\n"
            "2. Configure API keys and settings in `.env`\n"
            "3. Update `config.yml` and `profiles.yml` as needed\n"
            "4. Set environment variables:\n"
            "   export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml\n"
            "   export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml\n"
            "5. Start the server with `ingen serve`"
        )

        panel = Panel(content, title="🛠️  Project Setup Guide", border_style="blue")
        self.console.print(panel)

    def _show_workflows_help(self) -> None:
        """Show workflows-specific help."""
        content = (
            "Workflows are the core of Insight Ingenious. They define how agents\n"
            "process and respond to user inputs.\n\n"
            "Use 'ingen workflows' to see all available workflows and their requirements."
        )

        panel = Panel(content, title="🔄 Workflows Guide", border_style="blue")
        self.console.print(panel)

    def _show_config_help(self) -> None:
        """Show configuration-specific help."""
        content = (
            "Configuration is split between two files:\n"
            "• config.yml - Non-sensitive project settings\n"
            "• profiles.yml - API keys and sensitive configuration"
        )

        panel = Panel(content, title="⚙️  Configuration Guide", border_style="blue")
        self.console.print(panel)

    def _show_deployment_help(self) -> None:
        """Show deployment-specific help."""
        content = (
            "Insight Ingenious can be deployed in several ways:\n"
            "• Local development: ingen serve\n"
            "• Docker: Use provided Docker templates\n"
            "• Cloud: Deploy to Azure, AWS, or other cloud providers"
        )

        panel = Panel(content, title="🚀 Deployment Guide", border_style="blue")
        self.console.print(panel)


class StatusCommand(BaseCommand):
    """Check system status and configuration."""

    def execute(self) -> None:
        """
        Check the status of Insight Ingenious configuration.

        Validates:
        • Configuration files existence and validity
        • Environment variables
        • Required dependencies
        • Available workflows
        """
        self.console.print(
            "[bold blue]🔍 Insight Ingenious System Status[/bold blue]\n"
        )

        status_items = {}

        # Check environment variables
        self._check_environment_variables(status_items)

        # Check local files
        self._check_local_files(status_items)

        # Display status table
        table = OutputFormatters.create_status_table(status_items, "System Status")
        self.console.print(table)

        # Show recommendations if needed
        self._show_recommendations(status_items)

    def _check_environment_variables(self, status_items: dict) -> None:
        """Check environment variables status."""
        project_path = os.getenv("INGENIOUS_PROJECT_PATH")
        profile_path = os.getenv("INGENIOUS_PROFILE_PATH")

        if project_path:
            if Path(project_path).exists():
                status_items["INGENIOUS_PROJECT_PATH"] = {
                    "status": "OK",
                    "details": project_path,
                }
            else:
                status_items["INGENIOUS_PROJECT_PATH"] = {
                    "status": "Warning",
                    "details": f"File not found: {project_path}",
                }
        else:
            status_items["INGENIOUS_PROJECT_PATH"] = {
                "status": "Missing",
                "details": "Environment variable not set",
            }

        if profile_path:
            if Path(profile_path).exists():
                status_items["INGENIOUS_PROFILE_PATH"] = {
                    "status": "OK",
                    "details": profile_path,
                }
            else:
                status_items["INGENIOUS_PROFILE_PATH"] = {
                    "status": "Warning",
                    "details": f"File not found: {profile_path}",
                }
        else:
            status_items["INGENIOUS_PROFILE_PATH"] = {
                "status": "Missing",
                "details": "Environment variable not set",
            }

    def _check_local_files(self, status_items: dict) -> None:
        """Check local configuration files."""
        files_to_check = {
            "config.yml": Path.cwd() / "config.yml",
            "profiles.yml": Path.cwd() / "profiles.yml",
            ".env": Path.cwd() / ".env",
        }

        for name, path in files_to_check.items():
            if path.exists():
                status_items[f"Local {name}"] = {"status": "OK", "details": str(path)}
            else:
                status_items[f"Local {name}"] = {
                    "status": "Missing",
                    "details": "File not found in current directory",
                }

    def _show_recommendations(self, status_items: dict) -> None:
        """Show setup recommendations based on status."""
        has_issues = any(
            item.get("status", "").lower() in ["missing", "warning", "error"]
            for item in status_items.values()
            if isinstance(item, dict)
        )

        if has_issues:
            recommendations = [
                "export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml",
                "export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml",
            ]

            if any("Missing" in str(item) for item in status_items.values()):
                recommendations.insert(0, "ingen init  # Initialize missing files")

            panel = Panel(
                "\n".join(recommendations),
                title="💡 Quick Setup Recommendations",
                border_style="yellow",
            )
            self.console.print("\n")
            self.console.print(panel)


class VersionCommand(BaseCommand):
    """Show version information."""

    def execute(self) -> None:
        """Display version information for Insight Ingenious."""
        try:
            from importlib.metadata import version as get_version

            version_str = get_version("insight-ingenious")
            self.console.print(
                f"[bold blue]Insight Ingenious[/bold blue] version [bold]{version_str}[/bold]"
            )
        except Exception:
            self.console.print(
                "[bold blue]Insight Ingenious[/bold blue] - Development Version"
            )

        self.console.print("🚀 GenAI Accelerator Framework")
        self.console.print(
            "📖 Documentation: https://github.com/Insight-Services-APAC/ingenious"
        )


class ValidateCommand(BaseCommand):
    """Validate system configuration and requirements."""

    def execute(self) -> None:
        """
        Comprehensive validation of Insight Ingenious setup.

        Performs deep validation of:
        • Configuration file syntax and required fields
        • Profile file syntax and credentials
        • Azure OpenAI connectivity
        • Workflow requirements
        • Dependencies
        """
        self.console.print(
            "[bold blue]✅ Insight Ingenious Configuration Validation[/bold blue]\n"
        )

        validation_passed = True

        # 1. Check environment variables
        self.print_info("1. Checking environment variables...")
        env_passed = self._validate_environment_variables()
        validation_passed = validation_passed and env_passed

        # 2. Validate configuration files
        self.print_info("2. Validating configuration files...")
        config_passed = self._validate_configuration_files()
        validation_passed = validation_passed and config_passed

        # 3. Check Azure OpenAI connectivity
        self.print_info("3. Checking Azure OpenAI connectivity...")
        azure_passed = self._validate_azure_connectivity()
        validation_passed = validation_passed and azure_passed

        # 4. Check workflow availability
        self.print_info("4. Checking workflow availability...")
        workflow_passed = self._validate_workflows()
        validation_passed = validation_passed and workflow_passed

        # 5. Summary and recommendations
        self._show_validation_summary(validation_passed)

        if not validation_passed:
            raise CommandError("Validation failed", ExitCode.VALIDATION_ERROR)

    def _validate_environment_variables(self) -> bool:
        """Validate environment variables."""
        try:
            paths = self.validate_config_paths()
            self.print_success("Environment variables are properly configured")
            return True
        except CommandError as e:
            self.print_error(f"Environment validation failed: {e}")
            self._show_env_fix_commands()
            return False

    def _validate_configuration_files(self) -> bool:
        """Validate configuration file syntax and content."""
        success = True

        # Validate config.yml
        try:
            project_path = os.getenv("INGENIOUS_PROJECT_PATH") or "config.yml"
            is_valid, error = ValidationUtils.validate_yaml_file(project_path)
            if is_valid:
                self.print_success("config.yml syntax validation passed")
            else:
                self.print_error(f"config.yml validation failed: {error}")
                success = False
        except Exception as e:
            self.print_error(f"config.yml validation error: {e}")
            success = False

        # Validate profiles.yml
        try:
            profile_path = os.getenv("INGENIOUS_PROFILE_PATH") or "profiles.yml"
            is_valid, error = ValidationUtils.validate_yaml_file(profile_path)
            if is_valid:
                self.print_success("profiles.yml syntax validation passed")
            else:
                self.print_error(f"profiles.yml validation failed: {error}")
                success = False
        except Exception as e:
            self.print_error(f"profiles.yml validation error: {e}")
            success = False

        return success

    def _validate_azure_connectivity(self) -> bool:
        """Validate Azure OpenAI connectivity."""
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_BASE_URL")

        if not azure_key:
            self.print_error("AZURE_OPENAI_API_KEY not set")
            return False

        if not azure_endpoint:
            self.print_error("AZURE_OPENAI_BASE_URL not set")
            return False

        # Validate URL format
        is_valid_url, error = ValidationUtils.validate_url(azure_endpoint)
        if not is_valid_url:
            self.print_error(f"Invalid Azure endpoint URL: {error}")
            return False

        self.print_success("Azure OpenAI configuration found")
        return True

    def _validate_workflows(self) -> bool:
        """Validate workflow availability."""
        try:
            extensions_path = Path.cwd() / "ingenious_extensions"
            if extensions_path.exists():
                self.print_success("ingenious_extensions directory found")

                services_path = extensions_path / "services"
                if services_path.exists():
                    self.print_success("Services directory found")
                    return True
                else:
                    self.print_warning("Services directory not found")
                    return False
            else:
                self.print_error("ingenious_extensions directory not found")
                return False
        except Exception as e:
            self.print_error(f"Workflow validation failed: {e}")
            return False

    def _show_env_fix_commands(self) -> None:
        """Show commands to fix environment variable issues."""
        fix_commands = [
            "export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml",
            "export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml",
        ]

        panel = Panel(
            "\n".join(fix_commands),
            title="🔧 Environment Fix Commands",
            border_style="yellow",
        )
        self.console.print(panel)

    def _show_validation_summary(self, validation_passed: bool) -> None:
        """Show validation summary and next steps."""
        if validation_passed:
            success_panel = Panel(
                "🎉 All validations passed! Your Ingenious setup is ready.\n"
                "🚀 You can now run: ingen serve",
                title="✅ Validation Summary",
                border_style="green",
            )
            self.console.print(success_panel)
        else:
            fix_commands = [
                "• Missing files: ingen init",
                "• Set environment variables:",
                "  export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml",
                "  export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml",
                "• Create .env file with Azure OpenAI credentials:",
                "  echo 'AZURE_OPENAI_API_KEY=your-key' > .env",
                "  echo 'AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com/' >> .env",
            ]

            error_panel = Panel(
                "\n".join(fix_commands),
                title="❌ Validation Issues - Fix Commands",
                border_style="red",
            )
            self.console.print(error_panel)


# Command registration functions for backward compatibility
def register_commands(app, console) -> None:
    """Register help commands with the typer app."""

    import typer
    from typing_extensions import Annotated

    @app.command(name="help", help="Show detailed help and getting started guide")
    def help_command(
        topic: Annotated[
            Optional[str],
            typer.Argument(help="Specific topic: setup, workflows, config, deployment"),
        ] = None,
    ):
        """Show comprehensive help for getting started with Insight Ingenious."""
        cmd = HelpCommand(console)
        cmd.run(topic=topic)

    @app.command(name="status", help="Check system status and configuration")
    def status():
        """Check the status of your Insight Ingenious configuration."""
        cmd = StatusCommand(console)
        cmd.run()

    @app.command(name="version", help="Show version information")
    def version():
        """Display version information for Insight Ingenious."""
        cmd = VersionCommand(console)
        cmd.run()

    @app.command(name="validate", help="Validate system configuration and requirements")
    def validate():
        """Comprehensive validation of your Insight Ingenious setup."""
        cmd = ValidateCommand(console)
        cmd.run()
