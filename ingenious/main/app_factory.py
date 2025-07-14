"""
FastAPI application factory.

This module contains the factory function for creating and configuring
the FastAPI application with all necessary middleware, routes, and services.
"""

import importlib.resources as pkg_resources
import os
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

from .exception_handlers import ExceptionHandlers
from .middleware import RequestContextMiddleware
from .routing import RouteManager

if TYPE_CHECKING:
    from ingenious.config import IngeniousSettings


class FastAgentAPI:
    """FastAPI application wrapper with initialization and configuration."""

    def __init__(self, config: "IngeniousSettings"):
        self.config = config
        self.app = self._create_app()
        self._configure_app()

    def _create_app(self) -> FastAPI:
        """Create the FastAPI application instance."""
        return FastAPI(title="FastAgent API", version="1.0.0")

    def _configure_app(self) -> None:
        """Configure the FastAPI application with middleware, routes, and services."""
        self._setup_dependency_injection()
        self._setup_working_directory()
        self._setup_middleware()
        self._setup_routes()
        self._setup_exception_handlers()
        self._setup_optional_services()
        self._setup_root_redirect()

    def _setup_dependency_injection(self) -> None:
        """Initialize dependency injection container."""
        from ingenious.services.container import init_container
        self.container = init_container()

    def _setup_working_directory(self) -> None:
        """Set the working directory."""
        os.chdir(os.environ["INGENIOUS_WORKING_DIR"])

    def _setup_middleware(self) -> None:
        """Configure middleware stack."""
        # Add request context middleware first
        self.app.add_middleware(RequestContextMiddleware)

        # Add CORS middleware
        origins = [
            "http://localhost",
            "http://localhost:5173",
            "http://localhost:4173",
        ]
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self) -> None:
        """Register all application routes."""
        RouteManager.register_all_routes(self.app, self.config)

    def _setup_exception_handlers(self) -> None:
        """Configure exception handlers."""
        ExceptionHandlers.register_handlers(self.app)

    def _setup_optional_services(self) -> None:
        """Setup optional services based on configuration."""
        self._setup_prompt_tuner()
        self._setup_chainlit()

    def _setup_prompt_tuner(self) -> None:
        """Mount Flask Prompt Tuner App if enabled."""
        if self.config.prompt_tuner.enable:
            import ingenious_prompt_tuner as prompt_tuner
            self.flask_app = prompt_tuner.create_app_for_fastapi()
            self.app.mount("/prompt-tuner", WSGIMiddleware(self.flask_app))

    def _setup_chainlit(self) -> None:
        """Mount ChainLit if enabled."""
        if self.config.chainlit_configuration.enable:
            from chainlit.utils import mount_chainlit
            chainlit_path = pkg_resources.files("ingenious.chainlit") / "app.py"
            mount_chainlit(app=self.app, target=str(chainlit_path), path="/chainlit")

    def _setup_root_redirect(self) -> None:
        """Setup root endpoint redirect."""
        self.app.get("/", tags=["Root"])(self.redirect_to_docs)

    async def redirect_to_docs(self) -> RedirectResponse:
        """Redirect the root endpoint to /docs."""
        return RedirectResponse(url="/docs")

    async def root(self) -> HTMLResponse:
        """Serve the root HTML page."""
        html_path = pkg_resources.files("ingenious.chainlit") / "index.html"
        with html_path.open("r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)


def create_app(config: "IngeniousSettings") -> FastAPI:
    """
    Factory function to create a configured FastAPI application.
    
    Args:
        config: Ingenious configuration settings
        
    Returns:
        Configured FastAPI application instance
    """
    api = FastAgentAPI(config)
    return api.app