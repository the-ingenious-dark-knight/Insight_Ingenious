"""
FastAPI Application Factory module.

This module provides a factory for creating FastAPI applications with proper configuration.
It follows the Factory pattern to create and configure FastAPI instances.
"""

from typing import List, Optional, Type

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

import ingenious.common.config.config as ingen_config
from ingenious.common.di.container import get_container
from ingenious.presentation.api.managers.base_manager import IManager


class ApplicationFactory:
    """
    Factory for creating and configuring FastAPI applications.

    This class follows the Single Responsibility Principle by focusing solely on
    creating and configuring FastAPI applications.
    """

    @staticmethod
    def create_app(
        config: ingen_config.Config,
        title: str = "Ingenious API",
        version: str = "1.0.0",
        managers: Optional[List[Type[IManager]]] = None,
    ) -> FastAPI:
        """
        Create and configure a FastAPI application.

        Args:
            config: The application configuration
            title: The title of the API
            version: The version of the API
            managers: Optional list of manager classes to use for configuration

        Returns:
            A configured FastAPI application
        """
        # Create the FastAPI application
        app = FastAPI(title=title, version=version)

        # Set up exception handlers
        app.add_exception_handler(
            Exception, ApplicationFactory._generic_exception_handler
        )

        # Set up root endpoint
        app.add_api_route(
            "/", endpoint=ApplicationFactory._redirect_to_docs, methods=["GET"]
        )

        # Configure using managers
        if managers:
            container = get_container()
            for manager_class in managers:
                manager = container.resolve(manager_class)
                manager.configure()

        return app

    @staticmethod
    async def _redirect_to_docs():
        """
        Redirect the root endpoint to /docs.

        Returns:
            RedirectResponse: A redirection to the /docs endpoint
        """
        return RedirectResponse(url="/docs")

    @staticmethod
    async def _generic_exception_handler(request: Request, exc: Exception):
        """
        Generic exception handler for the application.

        Args:
            request: The request that caused the exception
            exc: The exception that was raised

        Returns:
            JSONResponse with error details
        """
        # Log the exception
        import logging

        logger = logging.getLogger(__name__)
        logger.exception(exc)

        return JSONResponse(
            status_code=500, content={"detail": f"An error occurred: {str(exc)}"}
        )
