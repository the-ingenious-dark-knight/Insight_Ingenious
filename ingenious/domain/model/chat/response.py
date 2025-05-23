from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .message import Message


class ChatResponse(BaseModel):
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    job_id: str
    tools: Optional[List[dict]] = []
    thread_id: str
    message_id: str
    agent_response: dict
    token_count: int
    max_token_count: int
