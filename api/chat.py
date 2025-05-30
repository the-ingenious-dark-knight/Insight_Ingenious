"""
Chat API endpoints for agent interactions.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from agents.registry import AgentRegistry
from core.auth import get_current_user


router = APIRouter()


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
    try:
        # Get agent instance
        agent = AgentRegistry.get_agent(request.agent_type)
        
        # Run the agent
        response = await agent.run(request.message)
        
        # Clean up the agent
        await agent.close()
        
        return ChatResponse(
            response=response,
            agent_type=request.agent_type,
            agent_name=agent.config.name
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/agents")
async def list_agents(current_user: dict = Depends(get_current_user)):
    """List all available agent types."""
    return {"agents": AgentRegistry.list_agents()}


@router.post("/agents/{agent_type}/chat", response_model=ChatResponse)
async def chat_with_specific_agent(
    agent_type: str,
    message: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Chat with a specific agent type.
    
    - **agent_type**: Type of agent to use
    - **message**: The message to send to the agent
    """
    try:
        # Get agent instance
        agent = AgentRegistry.get_agent(agent_type)
        
        # Run the agent
        response = await agent.run(message)
        
        # Clean up the agent
        await agent.close()
        
        return ChatResponse(
            response=response,
            agent_type=agent_type,
            agent_name=agent.config.name
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
