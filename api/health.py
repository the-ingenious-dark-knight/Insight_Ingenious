"""
Health check and diagnostic API endpoints.

Provides endpoints for monitoring application health and status.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
import platform
import sys
from core.auth import optional_auth, get_config
from core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="Application version")
    uptime: Optional[str] = Field(default=None, description="Application uptime")


class DetailedHealthResponse(BaseModel):
    """Detailed health check response model."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="Application version")
    system_info: Dict[str, Any] = Field(..., description="System information")
    config_status: Dict[str, Any] = Field(..., description="Configuration status")
    agent_status: Dict[str, Any] = Field(..., description="Agent system status")


# Store startup time for uptime calculation
import time
_startup_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.
    
    Returns basic application health status. This endpoint does not require
    authentication to allow load balancers and monitoring systems to check health.
    
    Returns:
        Basic health status
    """
    config = get_config()
    uptime_seconds = time.time() - _startup_time
    uptime_str = f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m {int(uptime_seconds % 60)}s"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=config.app.version,
        uptime=uptime_str
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(
    current_user: Optional[str] = Depends(optional_auth)
) -> DetailedHealthResponse:
    """
    Detailed health check endpoint with system information.
    
    Provides comprehensive health and system information. Requires authentication
    if auth is enabled, but works without auth if disabled.
    
    Args:
        current_user: Optional authenticated user
        
    Returns:
        Detailed health status and system information
    """
    config = get_config()
    
    # System information
    system_info = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "architecture": platform.architecture(),
        "processor": platform.processor() or "Unknown",
        "hostname": platform.node(),
    }
    
    # Configuration status
    config_status = {
        "auth_enabled": config.auth.enabled,
        "debug_mode": config.app.debug,
        "log_level": config.logging.level,
        "models_configured": len(config.models),
    }
    
    # Agent system status
    try:
        from agents.registry import get_agent_registry
        registry = get_agent_registry()
        
        agent_status = {
            "agent_types_registered": len(registry.list_agent_types()),
            "agent_instances_created": len(registry.list_agent_instances()),
            "registry_healthy": True,
        }
    except Exception as e:
        logger.warning(f"Error checking agent status: {e}")
        agent_status = {
            "agent_types_registered": 0,
            "agent_instances_created": 0,
            "registry_healthy": False,
            "error": str(e),
        }
    
    return DetailedHealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=config.app.version,
        system_info=system_info,
        config_status=config_status,
        agent_status=agent_status
    )


@router.get("/status")
async def status_check() -> Dict[str, Any]:
    """
    Simple status endpoint returning basic application state.
    
    Returns:
        Application status information
    """
    config = get_config()
    
    return {
        "app_name": config.app.name,
        "version": config.app.version,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }
