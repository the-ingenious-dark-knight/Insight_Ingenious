import importlib
import logging
import os

from fastapi import FastAPI

from ingenious.common.utils.namespace_utils import import_class_with_fallback
from ingenious.domain.model.api.api_routes import IApiRoutes

logger = logging.getLogger(__name__)


class TemplateNotFoundException(Exception):
    """Exception raised when a template is not found."""
    pass


def load_extensions(app: FastAPI, config: any) -> None:
    """Load custom extensions for the application"""
    try:
        # Try to load custom API routes
        custom_api_routes_module = importlib.import_module("api.routes.custom")
        if custom_api_routes_module.__name__ != "ingenious.api.routes.custom":
            custom_api_routes_class = import_class_with_fallback(
                "api.routes.custom", "Api_Routes"
            )
            custom_api_routes_instance: IApiRoutes = custom_api_routes_class(
                config, app
            )
            custom_api_routes_instance.add_custom_routes()
            logger.info("Custom API routes loaded")
    except (ImportError, AttributeError) as e:
        logger.debug(f"No custom API routes found: {str(e)}")
    except Exception as e:
        logger.error(f"Error loading custom API routes: {str(e)}")


def copy_template_directory(*args, **kwargs):
    """Stub for copy_template_directory."""
    pass


def get_extension_path(*args, **kwargs):
    """Stub for get_extension_path."""
    return "/tmp/fake_extension_path"


def list_extensions(*args, **kwargs):
    """Stub for list_extensions."""
    return ["template", "custom_extension"]
