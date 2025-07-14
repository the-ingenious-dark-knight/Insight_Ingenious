"""
Utility functions and classes for the CLI.

This module contains helper functions and classes used by various CLI commands.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from sysconfig import get_paths

import ingenious.utils.stage_executor as stage_executor_module
from ingenious.utils.namespace_utils import import_class_with_fallback


class CliFunctions:
    """Utility functions for CLI operations."""
    
    class RunTestBatch(stage_executor_module.IActionCallable):
        """Action callable for running test batches."""
        
        async def __call__(self, progress, task_id, **kwargs):
            module_name = "tests.run_tests"
            class_name = "RunBatches"
            try:
                repository_class_import = import_class_with_fallback(
                    module_name, class_name
                )
                repository_class = repository_class_import(
                    progress=progress, task_id=task_id
                )

                await repository_class.run()

            except (ImportError, AttributeError) as e:
                raise ValueError(f"Batch Run Failed: {module_name}") from e

    @staticmethod
    def PureLibIncludeDirExists():
        """Check if the ingenious package exists in site-packages."""
        ChkPath = Path(get_paths()["purelib"]) / Path("ingenious/")
        return os.path.exists(ChkPath)

    @staticmethod
    def GetIncludeDir():
        """Get the include directory for the ingenious package."""
        ChkPath = Path(get_paths()["purelib"]) / Path("ingenious/")
        # print(ChkPath)
        # Does Check for the path
        if os.path.exists(ChkPath):
            return ChkPath
        else:
            path = Path(os.getcwd()) / Path("ingenious/")
            # print(str(path))
            return path

    @staticmethod
    def copy_ingenious_folder(src, dst):
        """Copy the ingenious folder from source to destination."""
        if not os.path.exists(dst):
            os.makedirs(dst)  # Create the destination directory if it doesn't exist

        for item in os.listdir(src):
            src_path = os.path.join(src, item)
            dst_path = os.path.join(dst, item)

            if os.path.isdir(src_path):
                # Recursively copy subdirectories
                CliFunctions.copy_ingenious_folder(src_path, dst_path)
            else:
                # Copy files
                if not os.path.exists(dst_path) or os.path.getmtime(
                    src_path
                ) > os.path.getmtime(dst_path):
                    shutil.copy2(src_path, dst_path)  # Copy file with metadata