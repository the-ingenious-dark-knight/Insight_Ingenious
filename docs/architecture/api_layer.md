# API Layer

This document details the API layer of the Insight Ingenious application.

## Overview

The API layer provides RESTful endpoints for interacting with the application. It's built using FastAPI, a modern, fast (high-performance) web framework for building APIs with Python.

## Key Components

- **FastAPI Application**: Main application instance
- **API Routers**: Modular endpoint groups
- **Request/Response Models**: Pydantic models for API contracts
- **Middleware**: Cross-cutting concerns like CORS and error handling

## FastAPI Application

The main application is created in `main.py`:

```python
def create_app(config_path: str = "config.yaml") -> FastAPI:
    """Create and configure the FastAPI application."""
    # Load configuration
    config = reload_config(config_path)
    
    # Set up logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Create FastAPI app
    app = FastAPI(
        title=config.app.name,
        version=config.app.version,
        debug=config.app.debug,
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register API routers
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
    
    return app
```

## API Routers

The API is organized into routers for different functionality:

### Health Router (`api/health.py`)

Endpoints for application health and status:

```python
@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.
    Returns status, version, and uptime information.
    """
    # Implementation
```

### Chat Router (`api/chat.py`)

Endpoints for interacting with agents:

```python
@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Chat with an agent.
    
    - **message**: The message to send to the agent
    - **agent_type**: Type of agent to use (default: "chat")
    - **context**: Optional context for the conversation
    """
    # Implementation
```

### Agents Router (`api/agents.py`)

Endpoints for managing agents:

```python
@router.get("/agents", response_model=List[str])
async def list_agents(current_user: dict = Depends(get_current_user)):
    """
    List all available agent instances.
    """
    # Implementation
```

## Request/Response Models

API contracts are defined using Pydantic models:

```python
class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    message: str
    agent_type: str = "chat"
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    response: str
    agent_type: str
    agent_name: str
```

## Error Handling

The API includes consistent error handling:

```python
@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
```

## Authentication

API endpoints are secured using HTTP Basic Authentication:

```python
@router.get("/protected-endpoint")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    # Only accessible with valid credentials
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

These pages provide complete documentation of all endpoints, including:

- Request and response models
- Authentication requirements
- Example requests and responses
