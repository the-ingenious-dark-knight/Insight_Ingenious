"""
Project management CLI commands for Insight Ingenious.

This module contains commands for initializing projects and managing project structure.
"""

from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path

import typer
from rich.console import Console


def register_commands(app: typer.Typer, console: Console) -> None:
    """Register project-related commands with the typer app."""
    
    @app.command(name="init", help="Initialize a new Insight Ingenious project")
    def init():
        """
        🏗️  Initialize a new Insight Ingenious project in the current directory.

        Creates a complete project structure with:
        • config.yml - Project configuration (non-sensitive settings)
        • profiles.yml - Environment profiles (API keys, secrets)
        • .env.example - Example environment variables
        • ingenious_extensions/ - Your custom agents and workflows
        • templates/prompts/quickstart-1/ - Ready-to-use bike-insights workflow templates
        • Dockerfile - Docker containerization setup
        • .dockerignore - Docker build exclusions
        • tmp/ - Temporary files and memory storage

        🎯 INCLUDES: Pre-configured quickstart-1 templates for immediate bike-insights testing!

        NEXT STEPS after running this command:
        1. Copy .env.example to .env and add your credentials
        2. Update config.yml and profiles.yml for your environment
        3. Set environment variables:
           export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
           export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
        4. Start the server: ingen serve

        For detailed configuration help: igen workflows --help
        """
        return initialize_new_project()

    # Keep old command for backward compatibility
    @app.command(hidden=True)
    def initialize_new_project():
        """
        Generate template folders for a new project using the Ingenious framework.

        Creates the following structure:
        • config.yml - Project configuration (non-sensitive settings) in project directory
        • profiles.yml - Environment profiles (API keys, secrets) in project directory
        • .env.example - Example environment variables file
        • ingenious_extensions/ - Your custom agents and workflows
        • templates/prompts/quickstart-1/ - Pre-configured bike-insights workflow templates
        • Dockerfile - Docker containerization setup at project root
        • .dockerignore - Docker build exclusions at project root
        • tmp/ - Temporary files and memory

        NEXT STEPS after running this command:
        1. Copy .env.example to .env and fill in your credentials
        2. Update config.yml and profiles.yml as needed for your project
        3. Set environment variables:
           export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
           export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
        4. Start the server: ingen serve

        For workflow-specific configuration requirements, see:
        docs/workflows/README.md
        """
        base_path = Path(__file__).parent.parent
        templates_paths = {
            "ingenious_extensions": base_path / "ingenious_extensions_template",
            "tmp": None,  # No template, just create the folder
        }

        for folder_name, template_path in templates_paths.items():
            destination = Path.cwd() / folder_name

            # Skip if the destination folder already exists
            if destination.exists():
                console.print(
                    f"[warning]Folder '{folder_name}' already exists. Skipping...[/warning]"
                )
                continue

            # Check if a template path exists (if applicable)
            if template_path and not template_path.exists():
                console.print(
                    f"[error]Template directory '{template_path}' not found. Skipping...[/error]"
                )
                continue

            try:
                # Create the destination folder
                destination.mkdir(parents=True, exist_ok=True)

                if template_path:
                    # Copy template contents if a template path is provided
                    for item in template_path.iterdir():
                        src_path = template_path / item
                        dst_path = destination / item.name

                        # Skip Docker files when copying to ingenious_extensions - they'll be copied to project root separately
                        if folder_name == "ingenious_extensions" and item.name in [
                            "Dockerfile",
                            ".dockerignore",
                            "start.sh",
                        ]:
                            continue

                        if src_path.is_dir():
                            if "__pycache__" not in src_path.parts:
                                shutil.copytree(
                                    src_path,
                                    dst_path,
                                    ignore=shutil.ignore_patterns("__pycache__"),
                                )
                            # replace all instances of 'ingenious_extensions_template' with the project name:
                            for root, dirs, files in os.walk(dst_path):
                                for file in files:
                                    try:
                                        file_path = os.path.join(root, file)
                                        with open(file_path, "r") as f:
                                            file_contents = f.read()
                                        file_contents = file_contents.replace(
                                            "ingenious.ingenious_extensions_template",
                                            destination.name,
                                        )
                                        with open(file_path, "w") as f:
                                            f.write(file_contents)
                                    except Exception as e:
                                        console.print(
                                            f"[error]Error processing file '{file_path}': {e}[/error]"
                                        )
                        else:
                            try:
                                shutil.copy2(src_path, dst_path)
                            except Exception as e:
                                console.print(
                                    f"[error]Error copying files in  '{src_path}': {e}[/error]"
                                )
                elif folder_name == "tmp":
                    # Create an empty context.md file in the 'tmp' folder
                    (destination / "context.md").touch()

                console.print(f"[info]Folder '{folder_name}' created successfully.[/info]")

            except Exception as e:
                console.print(
                    f"[error]Error processing folder '{folder_name}': {e}[/error]"
                )

        # create a gitignore file
        gitignore_path = Path.cwd() / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, "w") as f:
                git_ignore_content = [
                    "*.pyc",
                    "__pycache__",
                    "*.log",
                    "/files/",
                    "/tmp/",
                    ".env",
                ]
                f.write("\n".join(git_ignore_content))

        # create a config file in project directory - prefer minimal template
        minimal_config_path = templates_paths["ingenious_extensions"] / "config.minimal.yml"
        template_config_path = (
            templates_paths["ingenious_extensions"] / "config.template.yml"
        )

        # Use minimal template if available, otherwise fall back to full template
        source_config_path = (
            minimal_config_path if minimal_config_path.exists() else template_config_path
        )

        if source_config_path.exists():
            config_path = Path.cwd() / "config.yml"
            if not config_path.exists():
                shutil.copy2(source_config_path, config_path)
                template_type = (
                    "minimal" if source_config_path == minimal_config_path else "full"
                )
                console.print(
                    f"[info]Config file created successfully at {config_path} using {template_type} template.[/info]"
                )
            else:
                console.print(
                    f"[info]Config file already exists at {config_path}. Preserving existing configuration.[/info]"
                )
        else:
            console.print("[warning]Config file templates not found. Skipping...[/warning]")

        # create profile file in project directory - prefer minimal template
        minimal_profile_path = (
            templates_paths["ingenious_extensions"] / "profiles.minimal.yml"
        )
        template_profile_path = (
            templates_paths["ingenious_extensions"] / "profiles.template.yml"
        )

        # Use minimal template if available, otherwise fall back to full template
        source_profile_path = (
            minimal_profile_path if minimal_profile_path.exists() else template_profile_path
        )

        if source_profile_path.exists():
            profile_path = Path.cwd() / "profiles.yml"
            if not profile_path.exists():
                shutil.copy2(source_profile_path, profile_path)
                template_type = (
                    "minimal" if source_profile_path == minimal_profile_path else "full"
                )
                console.print(
                    f"[info]Profile file created successfully at {profile_path} using {template_type} template[/info]"
                )
            else:
                console.print(
                    f"[info]Profile file already exists at {profile_path}. Preserving existing configuration.[/info]"
                )
        else:
            console.print(
                "[warning]Profile file templates not found. Skipping...[/warning]"
            )

        # create .env.example file - prefer minimal template
        minimal_env_path = templates_paths["ingenious_extensions"] / ".env.minimal"
        template_env_example_path = templates_paths["ingenious_extensions"] / ".env.example"

        # Use minimal template if available, otherwise fall back to full template
        source_env_path = (
            minimal_env_path if minimal_env_path.exists() else template_env_example_path
        )

        if source_env_path.exists():
            env_example_path = Path.cwd() / ".env.example"
            if not env_example_path.exists():
                shutil.copy2(source_env_path, env_example_path)
                template_type = "minimal" if source_env_path == minimal_env_path else "full"
                console.print(
                    f"[info].env.example file created successfully at {env_example_path} using {template_type} template[/info]"
                )
            else:
                console.print(
                    f"[info].env.example file already exists at {env_example_path}. Preserving existing file.[/info]"
                )
        else:
            console.print(
                "[warning].env.example templates not found. Skipping...[/warning]"
            )

        # Create Docker files at project root
        docker_file_path = templates_paths["ingenious_extensions"] / "Dockerfile"
        dockerignore_file_path = templates_paths["ingenious_extensions"] / ".dockerignore"
        start_sh_file_path = templates_paths["ingenious_extensions"] / "start.sh"

        if docker_file_path.exists():
            project_docker_path = Path.cwd() / "Dockerfile"
            if not project_docker_path.exists():
                shutil.copy2(docker_file_path, project_docker_path)
                console.print(
                    f"[info]Dockerfile created successfully at {project_docker_path}[/info]"
                )
            else:
                console.print(
                    f"[info]Dockerfile already exists at {project_docker_path}. Preserving existing file.[/info]"
                )
        else:
            console.print("[warning]Dockerfile template not found. Skipping...[/warning]")

        if dockerignore_file_path.exists():
            project_dockerignore_path = Path.cwd() / ".dockerignore"
            if not project_dockerignore_path.exists():
                shutil.copy2(dockerignore_file_path, project_dockerignore_path)
                console.print(
                    f"[info].dockerignore created successfully at {project_dockerignore_path}[/info]"
                )
            else:
                console.print(
                    f"[info].dockerignore already exists at {project_dockerignore_path}. Preserving existing file.[/info]"
                )
        else:
            console.print(
                "[warning].dockerignore template not found. Skipping...[/warning]"
            )

        if start_sh_file_path.exists():
            project_start_sh_path = Path.cwd() / "start.sh"
            if not project_start_sh_path.exists():
                shutil.copy2(start_sh_file_path, project_start_sh_path)
                # Make start.sh executable
                project_start_sh_path.chmod(
                    project_start_sh_path.stat().st_mode | stat.S_IEXEC
                )
                console.print(
                    f"[info]start.sh created successfully at {project_start_sh_path}[/info]"
                )
            else:
                console.print(
                    f"[info]start.sh already exists at {project_start_sh_path}. Preserving existing file.[/info]"
                )
        else:
            console.print("[warning]start.sh template not found. Skipping...[/warning]")

        # Create quickstart-1 templates folder and copy prompt templates
        console.print("\n[bold]Setting up quickstart-1 prompt templates...[/bold]")
        quickstart_templates_destination = (
            Path.cwd() / "templates" / "prompts" / "quickstart-1"
        )

        # First try to copy from existing ingenious_extensions in the project
        existing_quickstart_source = (
            Path.cwd() / "ingenious_extensions" / "templates" / "prompts" / "quickstart-1"
        )
        # Fallback to the template directory
        template_quickstart_source = (
            templates_paths["ingenious_extensions"]
            / "templates"
            / "prompts"
            / "quickstart-1"
        )

        quickstart_templates_source = None
        if existing_quickstart_source.exists():
            quickstart_templates_source = existing_quickstart_source
            console.print("[info]Found existing quickstart-1 templates in project[/info]")
        elif template_quickstart_source.exists():
            quickstart_templates_source = template_quickstart_source
            console.print("[info]Using template quickstart-1 templates[/info]")

        if quickstart_templates_source and quickstart_templates_source.exists():
            try:
                # Create the templates directory structure
                quickstart_templates_destination.mkdir(parents=True, exist_ok=True)

                # Copy all prompt template files
                templates_copied = 0
                for template_file in quickstart_templates_source.iterdir():
                    if template_file.is_file() and template_file.suffix == ".jinja":
                        dst_file = quickstart_templates_destination / template_file.name
                        if not dst_file.exists():
                            shutil.copy2(template_file, dst_file)
                            console.print(f"[info]  ✓ {template_file.name}[/info]")
                            templates_copied += 1
                        else:
                            console.print(
                                f"[info]  ↺ {template_file.name} (already exists)[/info]"
                            )

                if templates_copied > 0:
                    console.print(
                        f"[info]✅ {templates_copied} quickstart-1 templates created successfully at {quickstart_templates_destination}[/info]"
                    )
                    console.print(
                        "[info]🎯 Ready for bike-insights workflow testing![/info]"
                    )
                else:
                    console.print(
                        "[info]✅ Quickstart-1 templates already configured[/info]"
                    )

            except Exception as e:
                console.print(f"[error]Error creating quickstart-1 templates: {e}[/error]")
        else:
            console.print(
                "[warning]Quickstart-1 template source not found. Creating templates from base prompts...[/warning]"
            )

            # Fallback: copy base templates from ingenious_extensions_template
            base_prompts_source = (
                templates_paths["ingenious_extensions"] / "templates" / "prompts"
            )
            if base_prompts_source.exists():
                try:
                    quickstart_templates_destination.mkdir(parents=True, exist_ok=True)

                    # Copy core template files
                    template_files = [
                        "bike_lookup_agent_prompt.jinja",
                        "customer_sentiment_agent_prompt.jinja",
                        "fiscal_analysis_agent_prompt.jinja",
                        "summary_agent_prompt.jinja",
                        "summary_prompt.jinja",
                    ]

                    templates_copied = 0
                    for template_name in template_files:
                        src_file = base_prompts_source / template_name
                        dst_file = quickstart_templates_destination / template_name

                        if src_file.exists() and not dst_file.exists():
                            shutil.copy2(src_file, dst_file)
                            console.print(f"[info]  ✓ {template_name}[/info]")
                            templates_copied += 1

                    # Create a basic user_proxy_prompt.jinja if it doesn't exist
                    user_proxy_file = (
                        quickstart_templates_destination / "user_proxy_prompt.jinja"
                    )
                    if not user_proxy_file.exists():
                        with open(user_proxy_file, "w") as f:
                            f.write(
                                "### ROLE\nYou are a user proxy agent that coordinates multi-agent conversations for bike sales analysis.\n"
                            )
                        console.print("[info]  ✓ user_proxy_prompt.jinja (created)[/info]")
                        templates_copied += 1

                    if templates_copied > 0:
                        console.print(
                            f"[info]✅ {templates_copied} quickstart-1 templates created from base templates[/info]"
                        )
                        console.print(
                            "[info]🎯 Ready for bike-insights workflow testing![/info]"
                        )

                except Exception as e:
                    console.print(
                        f"[error]Error creating quickstart-1 templates from base: {e}[/error]"
                    )

        console.print("[info]✅ Project initialization completed![/info]")
        console.print("[warning]⚠️  Next steps:[/warning]")
        console.print("1. Copy .env.example to .env and fill in your credentials")
        console.print("2. Set environment variables:")
        console.print("[info]   export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml[/info]")
        console.print("[info]   export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml[/info]")
        console.print("3. Start the server:")
        console.print("[info]   ingen serve[/info]")
        console.print("\n[bold yellow]💡 Tips:[/bold yellow]")
        console.print("• Check configuration: ingen status")
        console.print("• List workflows: ingen workflows")
        console.print("• Get help: ingen --help")
        console.print("\n[bold green]🎯 Ready for bike-insights workflow![/bold green]")
        console.print("• Quickstart-1 templates are pre-configured")
        console.print(
            "• Test immediately with: curl -X POST http://localhost:80/api/v1/chat ..."
        )