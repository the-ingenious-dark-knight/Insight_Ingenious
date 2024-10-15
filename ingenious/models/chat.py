from typing import Optional
from pydantic import BaseModel


class Action(BaseModel):
    action: str


class KnowledgeBaseLink(BaseModel):
    title: str
    url: str


class Product(BaseModel):
    sku: str


class ChatRequest(BaseModel):
    thread_id: Optional[str] = None
    user_prompt: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    topic: Optional[str] = None
    conversation_flow: str


class ChatResponse(BaseModel):
    thread_id: str
    message_id: str
    agent_response: str
    followup_questions: Optional[dict[str, str]] = {}
    actions: Optional[list[Action]] = []
    knowledge_base_links: Optional[list[KnowledgeBaseLink]] = []
    products: Optional[list[Product]] = []
    token_count: int
    max_token_count: int
    topic: Optional[str] = None
