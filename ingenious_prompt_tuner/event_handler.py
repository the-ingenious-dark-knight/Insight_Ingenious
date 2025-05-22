import json
import logging
from typing import Any, Dict

import jsonpickle

from ingenious.models.chat import ChatRequest

logger = logging.getLogger(__name__)


class EventHandler:
    """Handles loading and processing of event data files."""

    def __init__(self, config, fs_data, revision_id: str):
        """
        Initialize the event handler.

        Args:
            config: The application configuration
            fs_data: The file storage for data files
            revision_id: The revision ID
        """
        self.config = config
        self.fs_data = fs_data
        self.revision_id = revision_id

    async def load_event_data(self, file_name: str, file_path: str) -> Dict[str, Any]:
        """
        Load event data from a file.

        Args:
            file_name: The name of the file
            file_path: The path to the file

        Returns:
            The loaded JSON data as a dictionary
        """
        try:
            file_contents = await self.fs_data.read_file(
                file_name=file_name, file_path=file_path
            )
            return json.loads(file_contents)
        except Exception as e:
            logger.error(f"Error loading event data from {file_path}/{file_name}: {e}")
            return {}

    def prepare_chat_request(
        self,
        json_object: Dict[str, Any],
        identifier: str,
        identifier_group: str,
        conversation_flow: str,
        event_type: str,
    ) -> ChatRequest:
        """
        Prepare a chat request from event data.

        Args:
            json_object: The event data
            identifier: The request identifier
            identifier_group: The identifier group
            conversation_flow: The conversation flow to use
            event_type: The event type

        Returns:
            A prepared ChatRequest object
        """
        # Add the identifier and revision ID to the JSON object
        json_object["identifier"] = identifier
        json_object["revision_id"] = self.revision_id

        # Create the chat request
        return ChatRequest(
            user_id=identifier_group,
            thread_id=identifier,
            user_prompt=jsonpickle.dumps(json_object, unpicklable=False),
            conversation_flow=conversation_flow,
            event_type=event_type,
        )
