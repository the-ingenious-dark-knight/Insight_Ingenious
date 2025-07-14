import importlib.resources as pkg_resources
import logging
import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

import ingenious.config.config as ingen_config
from ingenious.api.routes import auth as auth_route
from ingenious.api.routes import chat as chat_route
from ingenious.api.routes import diagnostic as diagnostic_route
from ingenious.api.routes import message_feedback as message_feedback_route
from ingenious.api.routes import prompts as prompts_route
from ingenious.core.structured_logging import (
    clear_request_context,
    get_logger,
    set_request_context,
)
from ingenious.errors import (
    APIError,
    IngeniousError,
    ServiceError,
    handle_exception,
)

# Import your routers
from ingenious.models.api_routes import IApiRoutes
from ingenious.utils.namespace_utils import (
    import_class_with_fallback,
    import_module_with_fallback,
)


# Delay config loading until needed
def get_config():
    return ingen_config.get_config(os.getenv("INGENIOUS_PROJECT_PATH", ""))


# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to set request context for structured logging and tracing."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Extract user info from request if available
        user_id = None
        session_id = None
        client_ip = None
        user_agent = None

        # Get client information
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")

        # Extract session ID from custom header or cookies
        session_id = request.headers.get("X-Session-ID") or request.cookies.get(
            "session_id"
        )

        # Try to get user info from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from ingenious.auth.jwt import get_username_from_token

                token = auth_header[7:]  # Remove "Bearer " prefix
                user_id = get_username_from_token(token)
            except Exception:
                # Token validation failed, use fallback
                user_id = "unauthenticated"
        elif auth_header and auth_header.startswith("Basic "):
            # For basic auth, extract username without validating
            try:
                import base64

                credentials_str = base64.b64decode(auth_header[6:]).decode("utf-8")
                username, _ = credentials_str.split(":", 1)
                user_id = username
            except Exception:
                user_id = "unauthenticated"
        else:
            user_id = "anonymous"

        # Set request context with correlation ID
        request_id = set_request_context(
            user_id=user_id,
            session_id=session_id,
            client_ip=client_ip,
            user_agent=user_agent,
        )

        # Log request start
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            query_params=str(request.query_params),
            user_id=user_id,
            session_id=session_id,
            client_ip=client_ip,
            user_agent=user_agent,
            operation="request_start",
        )

        # Process request and add timing
        try:
            response = await call_next(request)
            processing_time = time.time() - start_time

            # Log request completion
            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                processing_time_seconds=processing_time,
                user_id=user_id,
                operation="request_complete",
            )

            # Add tracing headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"

            return response

        except Exception as exc:
            processing_time = time.time() - start_time

            # Log request failure
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                processing_time_seconds=processing_time,
                error_type=type(exc).__name__,
                error_message=str(exc),
                user_id=user_id,
                operation="request_error",
                exc_info=True,
            )

            raise exc

        finally:
            # Clear context after request
            clear_request_context()


class FastAgentAPI:
    def __init__(self, config: ingen_config.IngeniousSettings):
        # Initialize dependency injection container
        from ingenious.services.container import init_container

        self.container = init_container()

        # Set the working directory
        os.chdir(os.environ["INGENIOUS_WORKING_DIR"])

        # Initialize FastAPI app
        self.app = FastAPI(title="FastAgent API", version="1.0.0")

        # Mount Flask Prompt Tuner App if enabled
        if config.prompt_tuner.enable:
            import ingenious_prompt_tuner as prompt_tuner

            self.flask_app = prompt_tuner.create_app_for_fastapi()
            # Mount Flask App
            self.app.mount("/prompt-tuner", WSGIMiddleware(self.flask_app))

        # TODO: Add CORS option to config.
        origins = [
            "http://localhost",
            "http://localhost:5173",
            "http://localhost:4173",
        ]

        # Add request context middleware first
        self.app.add_middleware(RequestContextMiddleware)

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add in-built routes
        self.app.include_router(
            auth_route.router, prefix="/api/v1/auth", tags=["Authentication"]
        )
        self.app.include_router(chat_route.router, prefix="/api/v1", tags=["Chat"])
        self.app.include_router(
            diagnostic_route.router, prefix="/api/v1", tags=["Diagnostic"]
        )
        self.app.include_router(
            prompts_route.router, prefix="/api/v1", tags=["Prompts"]
        )
        self.app.include_router(
            message_feedback_route.router, prefix="/api/v1", tags=["Message Feedback"]
        )

        # Add custom routes from ingenious extensions
        custom_api_routes_module = import_module_with_fallback("api.routes.custom")
        if custom_api_routes_module.__name__ != "ingenious.api.routes.custom":
            custom_api_routes_class = import_class_with_fallback(
                "api.routes.custom", "Api_Routes"
            )
            custom_api_routes_class_instance: IApiRoutes = custom_api_routes_class(
                config, self.app
            )
            custom_api_routes_class_instance.add_custom_routes()

        # Add exception handlers
        self.app.add_exception_handler(Exception, self.generic_exception_handler)

        # Add specific handlers for FastAPI validation errors
        from fastapi.exceptions import RequestValidationError as FastAPIValidationError

        self.app.add_exception_handler(
            FastAPIValidationError, self.validation_exception_handler
        )

        # Mount ChainLit
        if config.chainlit_configuration.enable:
            from chainlit.utils import mount_chainlit

            chainlit_path = pkg_resources.files("ingenious.chainlit") / "app.py"
            mount_chainlit(app=self.app, target=str(chainlit_path), path="/chainlit")

        # Redirect `/` to `/docs`
        self.app.get("/", tags=["Root"])(self.redirect_to_docs)

    async def redirect_to_docs(self):
        """Redirect the root endpoint to /docs."""
        return RedirectResponse(url="/docs")

    async def generic_exception_handler(self, request: Request, exc: Exception):
        if os.environ.get("LOADENV") == "True":
            load_dotenv()

        # Handle Ingenious errors with proper status codes and user messages
        if isinstance(exc, IngeniousError):
            status_code = self._get_status_code_for_error(exc)

            logger.error(
                "Ingenious error in API",
                error_type=exc.__class__.__name__,
                error_code=exc.error_code,
                category=exc.category.value,
                severity=exc.severity.value,
                correlation_id=exc.context.correlation_id,
                request_path=str(request.url.path),
                request_method=request.method,
                user_id=exc.context.user_id,
                recoverable=exc.recoverable,
                exc_info=True,
            )

            response_content = {
                "error": {
                    "code": exc.error_code,
                    "message": exc.user_message,
                    "correlation_id": exc.context.correlation_id,
                    "recoverable": exc.recoverable,
                    "recovery_suggestion": exc.recovery_suggestion,
                }
            }

            response = JSONResponse(status_code=status_code, content=response_content)

            # Add rate limiting headers if applicable
            if hasattr(exc, "retry_after") and exc.retry_after:
                response.headers["Retry-After"] = str(exc.retry_after)
                response.headers["X-RateLimit-Reset"] = str(
                    int(time.time()) + exc.retry_after
                )

            return response

        # Convert generic exceptions to Ingenious errors
        else:
            ingenious_error = handle_exception(
                exc,
                operation="api_request",
                component="fastapi",
                request_path=str(request.url.path),
                request_method=request.method,
            )

            logger.error(
                "Unhandled exception converted to IngeniousError",
                error_type=type(exc).__name__,
                error_message=str(exc),
                correlation_id=ingenious_error.context.correlation_id,
                request_path=str(request.url.path),
                request_method=request.method,
                exc_info=True,
            )

            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": ingenious_error.error_code,
                        "message": ingenious_error.user_message,
                        "correlation_id": ingenious_error.context.correlation_id,
                        "recoverable": ingenious_error.recoverable,
                    }
                },
            )

    async def validation_exception_handler(self, request: Request, exc):
        """Handle FastAPI validation errors with structured format."""
        from ingenious.errors import RequestValidationError

        # Create structured validation error
        validation_error = RequestValidationError(
            "Request validation failed",
            context={
                "request_path": str(request.url.path),
                "request_method": request.method,
                "validation_errors": exc.errors() if hasattr(exc, "errors") else [],
                "request_body": getattr(exc, "body", None),
            },
            user_message="Invalid request format. Please check your input data.",
        )

        logger.warning(
            "Request validation error",
            error_type="RequestValidationError",
            error_code=validation_error.error_code,
            request_path=str(request.url.path),
            request_method=request.method,
            validation_errors=exc.errors() if hasattr(exc, "errors") else [],
            correlation_id=validation_error.context.correlation_id,
        )

        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": validation_error.error_code,
                    "message": validation_error.user_message,
                    "correlation_id": validation_error.context.correlation_id,
                    "details": exc.errors() if hasattr(exc, "errors") else [],
                    "recoverable": validation_error.recoverable,
                }
            },
        )

    def _get_status_code_for_error(self, error: IngeniousError) -> int:
        """Map Ingenious errors to appropriate HTTP status codes."""
        from ingenious.errors import (
            AuthenticationError,
            AuthorizationError,
            ConfigurationError,
            DatabaseError,
            RateLimitError,
            RequestValidationError,
            ResourceError,
            WorkflowNotFoundError,
        )

        # Authentication and authorization errors
        if isinstance(error, AuthenticationError):
            return 401
        elif isinstance(error, AuthorizationError):
            return 403

        # Client errors (4xx)
        elif isinstance(error, RequestValidationError):
            return 422  # Unprocessable Entity for validation errors
        elif isinstance(error, ConfigurationError):
            return 400  # Bad Request for configuration issues
        elif isinstance(error, (WorkflowNotFoundError, ResourceError)):
            return 404
        elif isinstance(error, RateLimitError):
            return 429

        # Server errors (5xx)
        elif isinstance(error, DatabaseError):
            return 503  # Service Unavailable for database issues
        elif isinstance(error, ServiceError):
            return 502  # Bad Gateway for service issues
        elif isinstance(error, APIError):
            # Check if it's a client error based on message
            if "timeout" in error.message.lower():
                return 504  # Gateway Timeout
            elif "not found" in error.message.lower():
                return 404
            else:
                return 500

        # Default to internal server error
        else:
            return 500

    async def root(self):
        # Locate the HTML file in ingenious.api
        html_path = pkg_resources.files("ingenious.chainlit") / "index.html"
        with html_path.open("r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
