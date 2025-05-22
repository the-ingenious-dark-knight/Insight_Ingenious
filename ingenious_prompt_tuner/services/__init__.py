"""Service for managing file operations and prompt templates."""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from ingenious.files.files_repository import FileStorage
from ingenious.models.test_data import Events
from ingenious.utils.namespace_utils import get_path_from_namespace_with_fallback
from ingenious_prompt_tuner.config import APP_CONFIG


class FileService:
    """Handles file operations for the prompt tuner."""

    def __init__(self, config):
        """Initialize with application configuration."""
        self.config = config
        self.fs = FileStorage(config, Category="revisions")
        self.fs_data = FileStorage(config, Category="data")
        self.events = Events(fs=self.fs)
        self.prompt_template_folder = None
        self.functional_tests_folder = None
        self.data_folder = None

    async def read_file(self, file_name: str, file_path: str) -> str:
        """Read a file's contents."""
        return await self.fs.read_file(file_name=file_name, file_path=file_path)

    async def write_file(self, file_name: str, file_path: str, content: str) -> bool:
        """Write content to a file."""
        return await self.fs.write_file(
            file_name=file_name, file_path=file_path, content=content
        )

    async def check_if_file_exists(self, file_name: str, file_path: str) -> bool:
        """Check if a file exists."""
        return await self.fs.check_if_file_exists(
            file_name=file_name, file_path=file_path
        )

    async def list_files(self, file_path: str) -> List[str]:
        """List files in a directory."""
        return await self.fs.list_files(file_path)

    async def get_prompt_template_path(self, revision_id: str) -> str:
        """Get the prompt template path for a revision."""
        return await self.fs.get_prompt_template_path(revision_id)

    async def get_functional_tests_path(self, revision_id: str) -> str:
        """Get the functional tests path for a revision."""
        path = await self.fs.get_functional_tests_path(revision_id)
        self.functional_tests_folder = path
        return path

    async def ensure_prompt_templates(
        self, revision_id: str, force_copy: bool = False
    ) -> str:
        """Ensure prompt templates exist for a revision, copying if needed."""
        source_prompt_folder = get_path_from_namespace_with_fallback(
            "templates/prompts"
        )
        target_prompt_folder = await self.fs.get_prompt_template_path(revision_id)

        # Check if folders changed or need initialization
        folder_changed = self.prompt_template_folder != target_prompt_folder
        if folder_changed:
            self.prompt_template_folder = target_prompt_folder

        # Check if prompts exist
        existing_prompts = await self.fs.list_files(target_prompt_folder)
        no_existing_prompts = len(existing_prompts) == 0

        # Copy prompts if needed
        if force_copy or no_existing_prompts:
            print(f"Copying prompts to {target_prompt_folder}")
            for file in os.listdir(source_prompt_folder):
                if ".jinja" in file:
                    with open(f"{source_prompt_folder}/{file}", "r") as f:
                        content = f.read()
                        await self.fs.write_file(file, target_prompt_folder, content)

        return target_prompt_folder

    async def ensure_test_data(self, revision_id: str, force_copy: bool = False) -> str:
        """Ensure test data exists for a revision, copying if needed."""
        target_folder = f"functional_test_outputs/{revision_id}"

        # Check if folder changed
        folder_changed = self.functional_tests_folder != target_folder
        if folder_changed:
            self.functional_tests_folder = target_folder

        # Check if data exists
        existing_files = await self.fs.list_files(target_folder)
        no_existing_files = len(existing_files) == 0

        # Copy data if needed
        if force_copy or no_existing_files:
            source_folder = get_path_from_namespace_with_fallback("sample_data")
            source_files = [
                f for f in os.listdir(source_folder) if "readme.md" not in f.lower()
            ]

            for file in source_files:
                if any(ext in file for ext in [".md", ".yml", ".json"]):
                    with open(f"{source_folder}/{file}", "r") as f:
                        content = f.read()

                        if file == "events.yml":
                            # Event file goes to test folder
                            await self.fs.write_file(file, target_folder, content)
                        else:
                            # Data files go to data folder
                            await self.fs_data.write_file(file, target_folder, content)

        return target_folder

    async def get_events(self, revision_id: str) -> Events:
        """Get events for a revision."""
        await self.events.load_events_from_file(
            f"functional_test_outputs/{revision_id}"
        )
        return self.events
