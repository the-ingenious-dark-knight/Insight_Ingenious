"""
Agent management API endpoints.

Provides endpoints for discovering, creating, and managing agents.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from core.logging import get_structured_logger
from agents.registry import get_agent_registry

router = APIRouter()
logger = get_structured_logger(__name__)


class AgentInfo(BaseModel):
    """Agent information model."""
    name: str = Field(..., description="Agent name")
    type: str = Field(..., description="Agent type/class")
    config: Dict[str, Any] = Field(..., description="Agent configuration")
    agents_count: int = Field(..., description="Number of AutoGen agents")


class AgentCreateRequest(BaseModel):
    """Request model for creating agents."""
    agent_type: str = Field(..., description="Type of agent to create")
    name: str = Field(..., description="Unique name for the agent")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Agent configuration")


class AgentCreateResponse(BaseModel):
    """Response model for agent creation."""
    success: bool = Field(..., description="Whether creation was successful")
    agent_info: Optional[AgentInfo] = Field(default=None, description="Created agent info")
    error: Optional[str] = Field(default=None, description="Error message if any")


@router.get("/agents", response_model=List[str])
async def list_agent_instances(
    current_user: str = Depends(get_current_user)
) -> List[str]:
    """
    List all created agent instances.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of agent instance names
    """
    logger.info("Listing agent instances", extra_data={"user": current_user})
    
    registry = get_agent_registry()
    agents = registry.list_agent_instances()
    
    logger.info(f"Found {len(agents)} agent instances", extra_data={"user": current_user})
    return agents


@router.get("/agents/types", response_model=List[str])
async def list_agent_types(
    current_user: str = Depends(get_current_user)
) -> List[str]:
    """
    List all available agent types.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of registered agent types
    """
    logger.info("Listing agent types", extra_data={"user": current_user})
    
    registry = get_agent_registry()
    types = registry.list_agent_types()
    
    logger.info(f"Found {len(types)} agent types", extra_data={"user": current_user})
    return types


@router.get("/agents/{agent_name}", response_model=AgentInfo)
async def get_agent_info(
    agent_name: str,
    current_user: str = Depends(get_current_user)
) -> AgentInfo:
    """
    Get information about a specific agent.
    
    Args:
        agent_name: Name of the agent
        current_user: Authenticated user
        
    Returns:
        Agent information
    """
    logger.info(f"Getting agent info for {agent_name}", extra_data={"user": current_user})
    
    registry = get_agent_registry()
    agent_info = registry.get_agent_info(agent_name)
    
    if not agent_info:
        logger.warning(f"Agent not found: {agent_name}", extra_data={"user": current_user})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found"
        )
    
    return AgentInfo(**agent_info)


@router.post("/agents", response_model=AgentCreateResponse)
async def create_agent(
    request: AgentCreateRequest,
    current_user: str = Depends(get_current_user)
) -> AgentCreateResponse:
    """
    Create a new agent instance.
    
    Args:
        request: Agent creation request
        current_user: Authenticated user
        
    Returns:
        Agent creation response
    """
    logger.info(
        f"Creating agent: {request.name} (type: {request.agent_type})",
        extra_data={"user": current_user}
    )
    
    try:
        registry = get_agent_registry()
        
        # Check if agent name already exists
        if registry.get_agent(request.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Agent with name '{request.name}' already exists"
            )
        
        # Create the agent
        agent = registry.create_agent(
            agent_type=request.agent_type,
            name=request.name,
            config=request.config
        )
        
        agent_info = agent.get_info()
        
        logger.info(
            f"Agent created successfully: {request.name}",
            extra_data={"user": current_user}
        )
        
        return AgentCreateResponse(
            success=True,
            agent_info=AgentInfo(**agent_info)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        logger.warning(f"Invalid agent creation request: {e}", extra_data={"user": current_user})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating agent: {e}", extra_data={"user": current_user})
        return AgentCreateResponse(
            success=False,
            error=str(e)
        )


@router.delete("/agents/{agent_name}")
async def delete_agent(
    agent_name: str,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete an agent instance.
    
    Args:
        agent_name: Name of the agent to delete
        current_user: Authenticated user
        
    Returns:
        Deletion status
    """
    logger.info(f"Deleting agent: {agent_name}", extra_data={"user": current_user})
    
    registry = get_agent_registry()
    success = registry.remove_agent(agent_name)
    
    if not success:
        logger.warning(f"Agent not found for deletion: {agent_name}", extra_data={"user": current_user})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found"
        )
    
    logger.info(f"Agent deleted successfully: {agent_name}", extra_data={"user": current_user})
    return {"success": True, "message": f"Agent '{agent_name}' deleted successfully"}
