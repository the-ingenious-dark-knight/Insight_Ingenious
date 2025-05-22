import importlib
from typing import Any, Dict, List, Optional

import ingenious.common.config.config as Config
from ingenious.domain.interfaces.repository.chat_history_repository import (
    IChatHistoryRepository,
)
from ingenious.domain.model.chat.chat_history_models import StepDict, ThreadDict, User
from ingenious.domain.model.chat.message import Message
from ingenious.domain.model.database.database_client import DatabaseClientType


class ChatHistoryRepository(IChatHistoryRepository):
    """Implementation of the chat history repository interface"""

    def __init__(self, db_type: DatabaseClientType, config: Config.Config):
        module_name = f"ingenious.infrastructure.database.{db_type.value.lower()}"
        class_name = f"{db_type.value.lower()}_ChatHistoryRepository"

        try:
            module = importlib.import_module(module_name)
            repository_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(
                f"Unsupported database client type: {module_name}.{class_name}"
            ) from e

        self.repository = repository_class(config=config)

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        return await self.repository.update_thread(
            thread_id=thread_id,
            name=name,
            user_id=user_id,
            metadata=metadata,
            tags=tags,
        )

    async def add_user(self, identifier: str) -> User:
        return await self.repository.add_user(identifier)

    async def add_step(self, step_dict: StepDict) -> str:
        return await self.repository.add_step(step_dict)

    async def get_user(self, identifier: str) -> User | None:
        return await self.repository.get_user(identifier)

    async def add_message(self, message: Message) -> str:
        return await self.repository.add_message(message)

    async def add_memory(self, memory: Message) -> str:
        return await self.repository.add_memory(memory)

    async def get_message(self, message_id: str, thread_id: str) -> Message | None:
        return await self.repository.get_message(message_id, thread_id)

    async def get_memory(self, message_id: str, thread_id: str) -> Message | None:
        return await self.repository.get_memory(message_id, thread_id)

    async def update_memory(self) -> Message | None:
        return await self.repository.update_memory()

    async def get_thread_messages(self, thread_id: str) -> list[Message]:
        return await self.repository.get_thread_messages(thread_id)

    async def get_thread_memory(self, thread_id: str) -> Optional[list[ThreadDict]]:
        return await self.repository.get_thread_memory(thread_id)

    async def get_threads_for_user(
        self, identifier: str, thread_id: Optional[str]
    ) -> Optional[List[ThreadDict]]:
        return await self.repository.get_threads_for_user(identifier, thread_id)

    async def update_message_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        return await self.repository.update_message_feedback(
            message_id, thread_id, positive_feedback
        )

    async def update_memory_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        return await self.repository.update_memory_feedback(
            message_id, thread_id, positive_feedback
        )

    async def update_message_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        return await self.repository.update_message_content_filter_results(
            message_id, thread_id, content_filter_results
        )

    async def update_memory_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        return await self.repository.update_memory_content_filter_results(
            message_id, thread_id, content_filter_results
        )

    async def delete_thread(self, thread_id: str) -> None:
        return await self.repository.delete_thread(thread_id)

    async def delete_thread_memory(self, thread_id: str) -> None:
        return await self.repository.delete_thread_memory(thread_id)

    async def delete_user_memory(self, user_id: str) -> None:
        return await self.repository.delete_user_memory(user_id)

    async def get_messages(self, thread_id: str) -> List[Message]:
        """Implementation for the interface method"""
        return await self.get_thread_messages(thread_id)

    async def get_thread_metadata(self, thread_id: str) -> Dict[str, Any]:
        """Implementation for the interface method"""
        # This might need proper implementation based on repository capabilities
        threads = await self.repository.get_thread_messages(thread_id)
        if threads and isinstance(threads, list) and len(threads) > 0:
            thread = threads[0]
            if hasattr(thread, "metadata"):
                return thread.metadata
        return {}
