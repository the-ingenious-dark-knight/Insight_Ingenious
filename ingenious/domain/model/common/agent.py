import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Agent Configuration"""
    name: str
    system_message: str
    model: str = "gpt-3.5-turbo"
