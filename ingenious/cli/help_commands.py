"""
Help and status CLI commands for Insight Ingenious.

This module contains commands for getting help, checking status, and validating configuration.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from typing_extensions import Annotated


def register_commands(app: typer.Typer, console: Console) -> None:
    """Register help and status commands with the typer app."""

    @app.command(name="help", help="Show detailed help and getting started guide")
    def help_command(
        topic: Annotated[
            Optional[str],
            typer.Argument(help="Specific topic: setup, workflows, config, deployment"),
        ] = None,
    ):
        """
        📚 Show comprehensive help for getting started with Insight Ingenious.

        Topics available:
        • setup - Initial project setup steps
        • workflows - Understanding and configuring workflows
        • config - Configuration file details
        • deployment - Deployment options and best practices
        """
        if topic is None:
            console.print(
                "[bold blue]🚀 Insight Ingenious - Quick Start Guide[/bold blue]\n"
            )

            console.print("[bold]1. Initialize a new project:[/bold]")
            console.print("   ingen init")
            console.print("")

            console.print("[bold]2. Configure your project:[/bold]")
            console.print("   • Copy .env.example to .env and add your API keys")
            console.print("   • Update config.yml and profiles.yml as needed")
            console.print("")

            console.print("[bold]3. Set environment variables:[/bold]")
            console.print("   export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml")
            console.print("   export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml")
            console.print("")

            console.print("[bold]4. Start the server:[/bold]")
            console.print("   ingen serve")
            console.print("")

            console.print("[bold]5. Access the interfaces:[/bold]")
            console.print("   • API: http://localhost:80")
            console.print("   • Chat: http://localhost:80/chainlit")
            console.print("   • Prompt Tuner: http://localhost:80/prompt-tuner")
            console.print("")

            console.print("[bold yellow]💡 Helpful Commands:[/bold yellow]")
            console.print("   ingen status      # Check configuration")
            console.print("   ingen workflows   # List available workflows")
            console.print("   ingen test        # Run tests")
            console.print(
                "   ingen help <topic> # Get detailed help on specific topics"
            )
            console.print("")

            console.print("[bold yellow]📖 Documentation:[/bold yellow]")
            console.print(
                "   GitHub: https://github.com/Insight-Services-APAC/ingenious"
            )

        elif topic == "setup":
            console.print("[bold blue]🛠️  Project Setup Guide[/bold blue]\n")
            console.print("To set up your Insight Ingenious project:")
            console.print("1. Run `ingen init` to generate project files")
            console.print("2. Configure API keys and settings in `.env`")
            console.print("3. Update `config.yml` and `profiles.yml` as needed")
            console.print("4. Set environment variables:")
            console.print("   export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml")
            console.print("   export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml")
            console.print("5. Start the server with `ingen serve`")

        elif topic == "workflows":
            console.print("[bold blue]🔄 Workflows Guide[/bold blue]\n")
            console.print(
                "Workflows are the core of Insight Ingenious. They define how agents"
            )
            console.print("process and respond to user inputs.\n")
            console.print(
                "Use 'ingen workflows' to see all available workflows and their requirements."
            )

        elif topic == "config":
            console.print("[bold blue]⚙️  Configuration Guide[/bold blue]\n")
            console.print("Configuration is split between two files:")
            console.print("• config.yml - Non-sensitive project settings")
            console.print("• profiles.yml - API keys and sensitive configuration")

        elif topic == "deployment":
            console.print("[bold blue]🚀 Deployment Guide[/bold blue]\n")
            console.print("Insight Ingenious can be deployed in several ways:")
            console.print("• Local development: ingen serve")
            console.print("• Docker: Use provided Docker templates")
            console.print("• Cloud: Deploy to Azure, AWS, or other cloud providers")

        else:
            console.print(f"[red]❌ Unknown help topic: {topic}[/red]")
            console.print("\nAvailable topics: setup, workflows, config, deployment")
            console.print("Use 'ingen help' for general help.")

    @app.command(name="status", help="Check system status and configuration")
    def status():
        """
        🔍 Check the status of your Insight Ingenious configuration.

        Validates:
        • Configuration files existence and validity
        • Environment variables
        • Required dependencies
        • Available workflows
        """
        console.print("[bold blue]🔍 Insight Ingenious System Status[/bold blue]\n")

        # Check environment variables
        console.print("[bold]Environment Variables:[/bold]")
        project_path = os.getenv("INGENIOUS_PROJECT_PATH")
        profile_path = os.getenv("INGENIOUS_PROFILE_PATH")

        if project_path:
            console.print(f"  ✅ INGENIOUS_PROJECT_PATH: {project_path}")
            if not Path(project_path).exists():
                console.print("  ⚠️  [yellow]Config file not found at path[/yellow]")
        else:
            console.print("  ❌ INGENIOUS_PROJECT_PATH not set")

        if profile_path:
            console.print(f"  ✅ INGENIOUS_PROFILE_PATH: {profile_path}")
            if not Path(profile_path).exists():
                console.print("  ⚠️  [yellow]Profile file not found at path[/yellow]")
        else:
            console.print("  ❌ INGENIOUS_PROFILE_PATH not set")

        # Check local files
        console.print("\n[bold]Local Files:[/bold]")
        local_config = Path.cwd() / "config.yml"
        local_profile = Path.cwd() / "profiles.yml"
        local_env = Path.cwd() / ".env"

        console.print(f"  {'✅' if local_config.exists() else '❌'} config.yml")
        console.print(f"  {'✅' if local_profile.exists() else '❌'} profiles.yml")
        console.print(f"  {'✅' if local_env.exists() else '❌'} .env")

        # Quick setup guidance
        if not project_path or not profile_path:
            console.print("\n[bold yellow]💡 Quick Setup:[/bold yellow]")
            console.print("  export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml")
            console.print("  export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml")

        if not local_config.exists():
            console.print(
                "\n[bold yellow]💡 Initialize project:[/bold yellow] ingen init"
            )

    @app.command(name="version", help="Show version information")
    def version():
        """
        📦 Display version information for Insight Ingenious.
        """
        try:
            # Try to get version from package metadata
            from importlib.metadata import version as get_version

            version_str = get_version("insight-ingenious")
            console.print(
                f"[bold blue]Insight Ingenious[/bold blue] version [bold]{version_str}[/bold]"
            )
        except Exception:
            console.print(
                "[bold blue]Insight Ingenious[/bold blue] - Development Version"
            )

        console.print("🚀 GenAI Accelerator Framework")
        console.print(
            "📖 Documentation: https://github.com/Insight-Services-APAC/ingenious"
        )

    @app.command(name="validate", help="Validate system configuration and requirements")
    def validate():
        """
        ✅ Comprehensive validation of your Insight Ingenious setup.

        Performs deep validation of:
        • Configuration file syntax and required fields
        • Profile file syntax and credentials
        • Azure OpenAI connectivity
        • Workflow requirements
        • Dependencies

        This command helps identify issues before starting the server.
        """
        console.print(
            "[bold blue]✅ Insight Ingenious Configuration Validation[/bold blue]\n"
        )

        validation_passed = True

        # 1. Check environment variables
        console.print("[bold]1. Environment Variables:[/bold]")
        project_path = os.getenv("INGENIOUS_PROJECT_PATH")
        profile_path = os.getenv("INGENIOUS_PROFILE_PATH")

        if not project_path:
            console.print("  ❌ INGENIOUS_PROJECT_PATH not set")
            console.print(
                "     [dim]Fix: export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml[/dim]"
            )
            validation_passed = False
        elif not Path(project_path).exists():
            console.print(f"  ❌ Config file not found: {project_path}")
            console.print("     [dim]Fix: Run 'ingen init' to create config.yml[/dim]")
            validation_passed = False
        else:
            console.print(f"  ✅ INGENIOUS_PROJECT_PATH: {project_path}")

        if not profile_path:
            console.print("  ❌ INGENIOUS_PROFILE_PATH not set")
            console.print(
                "     [dim]Fix: export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml[/dim]"
            )
            validation_passed = False
        elif not Path(profile_path).exists():
            console.print(f"  ❌ Profile file not found: {profile_path}")
            console.print(
                "     [dim]Fix: Run 'ingen init' to create profiles.yml[/dim]"
            )
            validation_passed = False
        else:
            console.print(f"  ✅ INGENIOUS_PROFILE_PATH: {profile_path}")

        # 2. Validate configuration files
        console.print("\n[bold]2. Configuration File Validation:[/bold]")
        try:
            if project_path and Path(project_path).exists():
                import ingenious.config.config as ingen_config

                _ = ingen_config.get_config()
                console.print("  ✅ config.yml syntax and validation passed")
            else:
                console.print("  ❌ Cannot validate config.yml - file not found")
                validation_passed = False
        except Exception as e:
            console.print(f"  ❌ config.yml validation failed: {str(e)}")
            console.print("     [dim]Common fixes:[/dim]")
            console.print("     [dim]• Check YAML syntax (indentation, quotes)[/dim]")
            console.print(
                "     [dim]• Ensure required sections exist (models, profile)[/dim]"
            )
            console.print(
                "     [dim]• Comment out optional services if not using them[/dim]"
            )
            validation_passed = False

        try:
            if profile_path and Path(profile_path).exists():
                import ingenious.dependencies as igen_deps

                _ = igen_deps.get_profile()
                console.print("  ✅ profiles.yml syntax and validation passed")
            else:
                console.print("  ❌ Cannot validate profiles.yml - file not found")
                validation_passed = False
        except Exception as e:
            console.print(f"  ❌ profiles.yml validation failed: {str(e)}")
            console.print("     [dim]Common fixes:[/dim]")
            console.print("     [dim]• Set AZURE_OPENAI_API_KEY in .env file[/dim]")
            console.print("     [dim]• Set AZURE_OPENAI_BASE_URL in .env file[/dim]")
            console.print("     [dim]• Check YAML syntax and structure[/dim]")
            console.print(
                "     [dim]• Comment out optional services if not configured[/dim]"
            )
            validation_passed = False

        # 3. Check Azure OpenAI connectivity
        console.print("\n[bold]3. Azure OpenAI Connectivity:[/bold]")
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_BASE_URL")

        if not azure_key:
            console.print("  ❌ AZURE_OPENAI_API_KEY not set in environment")
            console.print(
                "     [dim]Fix: Add AZURE_OPENAI_API_KEY=your-key to .env file[/dim]"
            )
            validation_passed = False
        else:
            console.print("  ✅ AZURE_OPENAI_API_KEY found")

        if not azure_endpoint:
            console.print("  ❌ AZURE_OPENAI_BASE_URL not set in environment")
            console.print(
                "     [dim]Fix: Add AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com/ to .env[/dim]"
            )
            validation_passed = False
        else:
            console.print("  ✅ AZURE_OPENAI_BASE_URL found")

        # 4. Check workflow availability
        console.print("\n[bold]4. Workflow Availability:[/bold]")
        try:
            # Check if bike-insights workflow files exist
            extensions_path = Path.cwd() / "ingenious_extensions"
            if extensions_path.exists():
                console.print("  ✅ ingenious_extensions directory found")

                # Check for key workflow files
                services_path = extensions_path / "services"
                if services_path.exists():
                    console.print("  ✅ Services directory found")
                else:
                    console.print("  ⚠️  Services directory not found")
            else:
                console.print(
                    "  ❌ ingenious_extensions directory not found - run 'ingen init'"
                )
                validation_passed = False
        except Exception as e:
            console.print(f"  ❌ Workflow validation failed: {str(e)}")
            validation_passed = False

        # 5. Summary and recommendations
        console.print(
            f"\n[bold]{'✅ Validation Summary' if validation_passed else '❌ Validation Summary'}:[/bold]"
        )

        if validation_passed:
            console.print(
                "  🎉 [green]All validations passed! Your Ingenious setup is ready.[/green]"
            )
            console.print("  🚀 You can now run: [bold]ingen serve[/bold]")
        else:
            console.print(
                "  ⚠️  [yellow]Some validations failed. Please fix the issues above.[/yellow]"
            )
            console.print("\n[bold]🔧 Quick Fix Commands:[/bold]")
            console.print("  • Missing files: [bold]ingen init[/bold]")
            console.print("  • Set environment variables:")
            console.print(
                "    [bold]export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml[/bold]"
            )
            console.print(
                "    [bold]export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml[/bold]"
            )
            console.print("  • Create .env file with Azure OpenAI credentials:")
            console.print(
                "    [bold]echo 'AZURE_OPENAI_API_KEY=your-key' > .env[/bold]"
            )
            console.print(
                "    [bold]echo 'AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com/' >> .env[/bold]"
            )
            console.print(
                "  • Set environment: [bold]export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml[/bold]"
            )
            console.print("  • Edit credentials: [bold]nano .env[/bold]")

        if not validation_passed:
            raise typer.Exit(1)
