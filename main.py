"""
AutoGen FastAPI Template - Main Application

A minimal, developer-friendly template for building AutoGen-based agent APIs with FastAPI.

This application provides:
- Simple YAML + .env configuration
- Basic HTTP authentication
- RESTful API endpoints for agent interaction
- Agent registry for managing multiple agents
- Health checks and monitoring

Usage:
    uv run python main.py                    # Run with default config
    uv run python main.py --config custom.yaml  # Run with custom config
    uv run uvicorn main:app --reload         # Run with uvicorn directly
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import argparse

# Import core modules
from core.config import get_config, reload_config
from core.logging import setup_logging, get_logger
from core.auth import AuthError

# Import API routes
from api.health import router as health_router
from api.chat import router as chat_router

# Import agent registry
from agents.registry import AgentRegistry


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown tasks for the FastAPI application.
    """
    logger = get_logger(__name__)
    
    # Startup
    logger.info("Starting AutoGen FastAPI Template")
    
    # Setup logging
    setup_logging()
    logger.info("Logging configured")
    
    # Log available agents
    available_agents = AgentRegistry.list_agents()
    logger.info(f"Available agent types: {available_agents}")
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AutoGen FastAPI Template")
    logger.info("Application shutdown completed")


def create_app(config_path: str = "config.yaml") -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configured FastAPI application
    """
    # Load configuration
    config = reload_config(config_path)
    
    # Create FastAPI app
    app = FastAPI(
        title=config.app.name,
        version=config.app.version,
        description="A minimal abstraction over AutoGen and FastAPI for building agent APIs",
        lifespan=lifespan,
        debug=config.app.debug,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Exception handlers
    @app.exception_handler(AuthError)
    async def auth_exception_handler(request, exc: AuthError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        logger = get_logger(__name__)
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    
    # Include routers
    app.include_router(health_router, prefix="/api/v1", tags=["Health"])
    app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "AutoGen FastAPI Template",
            "version": config.app.version,
            "docs_url": "/docs",
            "health_url": "/api/v1/health",
        }
    
    return app


# Create the app instance
app = create_app()


def main():
    """Main entry point for running the application."""
    parser = argparse.ArgumentParser(description="AutoGen FastAPI Template")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Configuration file path (default: config.yaml)"
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Host to bind to (overrides config)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind to (overrides config)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = reload_config(args.config)
    
    # Override with command line arguments
    host = args.host or config.server.host
    port = args.port or config.server.port
    
    # The logs will be visible in the server logs
    logger = get_logger(__name__)
    logger.info(f"Starting AutoGen FastAPI Template on http://{host}:{port}/docs with config {args.config}")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=args.reload,
        reload_dirs=[".", "core", "agents", "api"] if args.reload else None,
    )


if __name__ == "__main__":
    main()
