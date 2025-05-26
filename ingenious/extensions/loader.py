"""
Extension loader module.

This module provides functionality for loading and managing extensions.
"""

import os
import shutil
from pathlib import Path
from typing import List


class TemplateNotFoundException(Exception):
    """Exception raised when a template is not found."""

    def __init__(self, template_name: str):
        """
        Initialize the exception.

        Args:
            template_name: The name of the template that was not found
        """
        self.template_name = template_name
        super().__init__(f"Template '{template_name}' not found")


def list_extensions() -> List[str]:
    """
    List all available extensions.

    Returns:
        List of extension names
    """
    extensions_dir = os.path.dirname(__file__)
    all_items = os.listdir(extensions_dir)
    
    # Filter to only include directories and exclude __pycache__, etc.
    extensions = [
        item for item in all_items
        if not item.startswith("__")
        and not item.endswith(".py")
    ]
    
    return extensions


def get_extension_path(extension_name: str) -> str:
    """
    Get the path to an extension.

    Args:
        extension_name: The name of the extension

    Returns:
        The path to the extension

    Raises:
        TemplateNotFoundException: If the extension is not found
    """
    extensions_dir = os.path.dirname(__file__)
    extension_path = os.path.join(extensions_dir, extension_name)
    
    if not os.path.exists(extension_path):
        raise TemplateNotFoundException(extension_name)
    
    return extension_path


def copy_template_directory(template_name: str, destination_path: str) -> bool:
    """
    Copy a template directory to a destination.

    Args:
        template_name: The name of the template to copy
        destination_path: The destination path

    Returns:
        True if successful, False otherwise
    """
    try:
        template_path = get_extension_path(template_name)
        
        if not os.path.exists(template_path):
            return False
        
        shutil.copytree(template_path, destination_path, dirs_exist_ok=True)
        return True
    except Exception:
        return False
