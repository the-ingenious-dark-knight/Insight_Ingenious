from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .message import Message


class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str
    user_id: str
    user_prompt: str
    conversation_flow: str
    thread_id: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None
