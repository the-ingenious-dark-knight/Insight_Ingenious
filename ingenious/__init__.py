# ingenious/__init__.py
"""
Ingenious - AI-powered conversation and workflow engine.

This package provides a modular system for building AI-powered applications
with support for dynamic workflows, chat services, and extensible architectures.
"""

# Explicit imports for better IDE support and clearer dependencies
from . import config, models, services, utils

__version__ = "1.0.0"
__all__ = ["config", "models", "services", "utils"]
